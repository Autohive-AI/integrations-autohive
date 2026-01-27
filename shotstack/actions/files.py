"""
Shotstack Files actions - Upload files and get upload URLs.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any
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
            content_base64 = inputs["content"]
            filename = inputs["filename"]
            content_type = inputs.get("content_type")
            wait_for_ready = inputs.get("wait_for_ready", True)

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

            if not presigned_url:
                return ActionResult(
                    data={"result": False, "error": "Failed to get presigned upload URL"},
                    cost_usd=0.0
                )

            await context.fetch(
                presigned_url,
                method="PUT",
                headers={"Content-Type": content_type},
                body=file_bytes
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
