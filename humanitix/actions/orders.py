"""
Humanitix Orders action - Retrieve order information for events.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from humanitix import humanitix
from helpers import HUMANITIX_API_BASE, get_api_headers, _build_order_response


@humanitix.action("get_orders")
class GetOrdersAction(ActionHandler):
    """
    Retrieve orders for a specific event.

    Returns order details including buyer information, ticket quantities,
    and payment status. Can fetch a single order by ID or list all orders
    for the event.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        event_id = inputs["event_id"]
        order_id = inputs.get("order_id")

        headers = get_api_headers(context)

        # Fetch orders for the event
        response = await context.fetch(
            f"{HUMANITIX_API_BASE}/events/{event_id}/orders",
            method="GET",
            headers=headers
        )

        orders_data = response if isinstance(response, list) else response.get("data", [])

        if order_id:
            # Filter for specific order
            matching_order = None
            for order in orders_data:
                if order.get("_id") == order_id:
                    matching_order = order
                    break

            if matching_order:
                orders = [_build_order_response(matching_order)]
            else:
                raise Exception(f"Order with ID '{order_id}' not found for event '{event_id}'")
        else:
            # Return all orders
            orders = [_build_order_response(o) for o in orders_data]

        return ActionResult(data={"orders": orders})
