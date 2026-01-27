"""
Humanitix Events action - Retrieve event information.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from humanitix import humanitix
from helpers import HUMANITIX_API_BASE, get_api_headers, _build_event_response


@humanitix.action("get_events")
class GetEventsAction(ActionHandler):
    """
    Retrieve events from your Humanitix account.

    Can fetch a single event by ID or list all events. Returns event details
    including name, dates, venue, and ticket information.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        event_id = inputs.get("event_id")

        headers = get_api_headers(context)

        if event_id:
            # Fetch single event - filter from the list since API may not support direct get
            response = await context.fetch(
                f"{HUMANITIX_API_BASE}/events",
                method="GET",
                headers=headers
            )

            events_data = response if isinstance(response, list) else response.get("data", [])
            matching_event = None

            for event in events_data:
                if event.get("_id") == event_id:
                    matching_event = event
                    break

            if matching_event:
                events = [_build_event_response(matching_event)]
            else:
                raise Exception(f"Event with ID '{event_id}' not found")
        else:
            # List all events
            response = await context.fetch(
                f"{HUMANITIX_API_BASE}/events",
                method="GET",
                headers=headers
            )

            events_data = response if isinstance(response, list) else response.get("data", [])
            events = [_build_event_response(e) for e in events_data]

        return ActionResult(data={"events": events})
