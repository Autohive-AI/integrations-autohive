"""
Humanitix Tags action - Retrieve tag information.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from humanitix import humanitix
from helpers import HUMANITIX_API_BASE, get_api_headers, _build_tag_response


@humanitix.action("get_tags")
class GetTagsAction(ActionHandler):
    """
    Retrieve all tags from your Humanitix account.

    Tags are used to categorize and filter events in collection pages,
    widgets, or when passed as additional data via API.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_api_headers(context)

        response = await context.fetch(
            f"{HUMANITIX_API_BASE}/tags",
            method="GET",
            headers=headers
        )

        tags_data = response if isinstance(response, list) else response.get("data", [])
        tags = [_build_tag_response(t) for t in tags_data]

        return ActionResult(data={"tags": tags})
