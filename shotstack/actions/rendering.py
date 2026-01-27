"""
Shotstack Rendering actions - Core rendering with timeline control.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

try:
    from shotstack.shotstack import shotstack
    from shotstack.helpers import (
        EDIT_API_BASE,
        get_environment,
        get_headers,
        poll_render_until_complete,
        download_file_as_base64,
    )
except ImportError:
    from shotstack import shotstack
    from helpers import (
        EDIT_API_BASE,
        get_environment,
        get_headers,
        poll_render_until_complete,
        download_file_as_base64,
    )


@shotstack.action("render_and_wait")
class RenderAndWaitAction(ActionHandler):
    """Submit a render job and wait for completion."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            max_wait = inputs.get("max_wait_seconds", 300)
            poll_interval = inputs.get("poll_interval_seconds", 5)

            payload = {
                "timeline": inputs["timeline"],
                "output": inputs["output"]
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            if not render_id:
                return ActionResult(
                    data={"result": False, "error": "Failed to submit render job"},
                    cost_usd=0.0
                )

            poll_result = await poll_render_until_complete(
                context, render_id, max_wait, poll_interval
            )

            if poll_result["status"] == "done":
                render_data = poll_result.get("render", {})
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": "done",
                        "url": poll_result["url"],
                        "duration": render_data.get("duration"),
                        "result": True
                    },
                    cost_usd=0.0
                )
            else:
                return ActionResult(
                    data={
                        "render_id": render_id,
                        "status": poll_result["status"],
                        "error": poll_result.get("error"),
                        "result": False
                    },
                    cost_usd=0.0
                )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("download_render")
class DownloadRenderAction(ActionHandler):
    """Download a rendered video/image and return as base64."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            render_id = inputs.get("render_id")
            url = inputs.get("url")

            if render_id and not url:
                response = await context.fetch(
                    f"{EDIT_API_BASE}/{env}/render/{render_id}",
                    method="GET",
                    headers=get_headers(context)
                )
                render_data = response.get("response", {})
                status = render_data.get("status")

                if status != "done":
                    return ActionResult(
                        data={
                            "result": False,
                            "error": f"Render is not complete. Status: {status}"
                        },
                        cost_usd=0.0
                    )
                url = render_data.get("url")

            if not url:
                return ActionResult(
                    data={"result": False, "error": "No URL available. Provide render_id or url."},
                    cost_usd=0.0
                )

            download_result = await download_file_as_base64(context, url)

            return ActionResult(
                data={
                    "content": download_result["content"],
                    "content_type": download_result["content_type"],
                    "filename": download_result["filename"],
                    "size": download_result["size"],
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"result": False, "error": str(e)},
                cost_usd=0.0
            )
