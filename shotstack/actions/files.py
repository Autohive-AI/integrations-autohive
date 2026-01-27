"""
Shotstack Files actions - Upload files and get upload URLs.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any
import aiohttp
import base64
import mimetypes

try:
    from shotstack.shotstack import shotstack
    from shotstack.helpers import (
        INGEST_API_BASE,
        get_environment,
        get_headers,
        poll_source_until_ready,
    )
except ImportError:
    from shotstack import shotstack
    from helpers import (
        INGEST_API_BASE,
        get_environment,
        get_headers,
        poll_source_until_ready,
    )


@shotstack.action("upload_file")
class UploadFileAction(ActionHandler):
    """Upload a file to Shotstack and get a URL for use in edits."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            # Default to False to avoid Lambda timeout - agent should use check_source_status
            wait_for_ready = inputs.get("wait_for_ready", False)

            # Support both new "file" object format (platform standard) and legacy flat format
            file_obj = inputs.get("file")
            if file_obj:
                # New format: {"file": {"content": "...", "name": "...", "contentType": "..."}}
                content_base64 = file_obj.get("content")
                filename = file_obj.get("name")
                content_type = file_obj.get("contentType")

                # Also check for S3 URL format (for large files)
                file_url = file_obj.get("url")
                if file_url and not content_base64:
                    # File is on S3, need to download it first
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            file_bytes = await response.read()
                            content_base64 = base64.b64encode(file_bytes).decode("utf-8")
            else:
                # Legacy format: {"content": "...", "filename": "..."}
                content_base64 = inputs.get("content")
                filename = inputs.get("filename")
                content_type = inputs.get("content_type")

            if not content_base64 or not filename:
                return ActionResult(
                    data={"result": False, "error": "Missing required file content or filename"},
                    cost_usd=0.0
                )

            file_bytes = base64.b64decode(content_base64)

            if not content_type:
                guessed_type, _ = mimetypes.guess_type(filename)
                content_type = guessed_type or "application/octet-stream"

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/upload",
                method="POST",
                headers=get_headers(context)
            )

            upload_data = response.get("data", {})
            attributes = upload_data.get("attributes", {})
            presigned_url = attributes.get("url")
            source_id = upload_data.get("id")

            # Get headers from Shotstack response if provided
            upload_headers = attributes.get("headers", {})

            if not presigned_url:
                return ActionResult(
                    data={"result": False, "error": "Failed to get presigned upload URL"},
                    cost_usd=0.0
                )

            # Use aiohttp directly for binary upload (context.fetch doesn't support binary body)
            # Skip Content-Type auto-header to avoid signature mismatch with presigned URL
            async with aiohttp.ClientSession() as session:
                # Include any headers from Shotstack response, or none if not provided
                put_headers = upload_headers if upload_headers else {}
                async with session.put(
                    presigned_url,
                    data=file_bytes,
                    headers=put_headers,
                    skip_auto_headers=['Content-Type']
                ) as upload_response:
                    if upload_response.status not in (200, 201):
                        error_text = await upload_response.text()
                        # Include debug info about what we received from Shotstack
                        return ActionResult(
                            data={
                                "result": False,
                                "error": f"Failed to upload file: {upload_response.status} - {error_text}",
                                "debug": {
                                    "shotstack_provided_headers": upload_headers,
                                    "presigned_url_preview": presigned_url[:100] + "..." if len(presigned_url) > 100 else presigned_url
                                }
                            },
                            cost_usd=0.0
                        )

            if wait_for_ready:
                poll_result = await poll_source_until_ready(context, source_id)
                if poll_result["status"] == "ready":
                    return ActionResult(
                        data={
                            "source_id": source_id,
                            "source_url": poll_result["source_url"],
                            "status": "ready",
                            "result": True
                        },
                        cost_usd=0.0
                    )
                else:
                    return ActionResult(
                        data={
                            "source_id": source_id,
                            "status": poll_result["status"],
                            "error": poll_result.get("error"),
                            "result": False
                        },
                        cost_usd=0.0
                    )
            else:
                return ActionResult(
                    data={
                        "source_id": source_id,
                        "status": "processing",
                        "result": True
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("check_source_status")
class CheckSourceStatusAction(ActionHandler):
    """Check the status of an uploaded file. Call until status is 'ready' or 'failed'."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            source_id = inputs["source_id"]

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/sources/{source_id}",
                method="GET",
                headers=get_headers(context)
            )

            source_data = response.get("data", {})
            attributes = source_data.get("attributes", {})
            status = attributes.get("status")  # status is inside attributes

            result_data = {
                "source_id": source_id,
                "status": status,
                "result": True
            }

            if status == "ready":
                result_data["source_url"] = attributes.get("source")
                result_data["message"] = "File is ready to use in edits!"
            elif status == "failed":
                result_data["error"] = source_data.get("error", "Source processing failed")
                result_data["result"] = False
            else:
                # Still processing (importing, etc.)
                result_data["message"] = f"File is {status}. Check again in a few seconds."

            return ActionResult(data=result_data, cost_usd=0.0)

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_upload_url")
class GetUploadUrlAction(ActionHandler):
    """Get a presigned URL for direct file upload."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/upload",
                method="POST",
                headers=get_headers(context)
            )

            upload_data = response.get("data", {})
            attributes = upload_data.get("attributes", {})

            return ActionResult(
                data={
                    "upload_url": attributes.get("url"),
                    "source_id": upload_data.get("id"),
                    "expires": attributes.get("expires"),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"upload_url": None, "source_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )
