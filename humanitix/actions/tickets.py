"""
Humanitix Tickets action - Retrieve ticket information for events.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from humanitix import humanitix
from helpers import HUMANITIX_API_BASE, get_api_headers, _build_ticket_response


@humanitix.action("get_tickets")
class GetTicketsAction(ActionHandler):
    """
    Retrieve tickets for a specific event.

    Returns ticket details including attendee information, ticket type,
    and check-in status. Can fetch a single ticket by ID or list all
    tickets for the event.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        event_id = inputs["event_id"]
        ticket_id = inputs.get("ticket_id")

        headers = get_api_headers(context)

        # Fetch tickets for the event
        response = await context.fetch(
            f"{HUMANITIX_API_BASE}/events/{event_id}/tickets",
            method="GET",
            headers=headers
        )

        tickets_data = response if isinstance(response, list) else response.get("data", [])

        if ticket_id:
            # Filter for specific ticket
            matching_ticket = None
            for ticket in tickets_data:
                if ticket.get("_id") == ticket_id:
                    matching_ticket = ticket
                    break

            if matching_ticket:
                tickets = [_build_ticket_response(matching_ticket)]
            else:
                raise Exception(f"Ticket with ID '{ticket_id}' not found for event '{event_id}'")
        else:
            # Return all tickets
            tickets = [_build_ticket_response(t) for t in tickets_data]

        return ActionResult(data={"tickets": tickets})
