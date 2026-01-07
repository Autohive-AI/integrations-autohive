"""
Luma Event actions - Create, retrieve, update events and manage ticket types/coupons.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from luma import luma
from helpers import get_auth_headers, build_url, format_event_response


@luma.action("get_self")
class GetSelfAction(ActionHandler):
    """
    Get information about the authenticated user.
    
    Used to verify API key validity and retrieve user details.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        response = await context.fetch(
            build_url("/user/get-self"),
            method="GET",
            headers=headers
        )
        
        user = response.get("user", response)
        
        return ActionResult(data={
            "api_id": user.get("api_id", ""),
            "email": user.get("email", ""),
            "name": user.get("name", ""),
            "username": user.get("username", "")
        })


@luma.action("create_event")
class CreateEventAction(ActionHandler):
    """
    Create a new event on the Luma calendar.
    
    Requires name, start time, and timezone. Other fields are optional.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "name": inputs["name"],
            "start_at": inputs["start_at"],
            "timezone": inputs["timezone"]
        }
        
        if inputs.get("description"):
            request_body["description"] = inputs["description"]
        
        if inputs.get("end_at"):
            request_body["end_at"] = inputs["end_at"]
        elif inputs.get("duration_interval"):
            request_body["duration_interval"] = inputs["duration_interval"]
        
        if inputs.get("geo_address_json"):
            request_body["geo_address_json"] = inputs["geo_address_json"]
        
        if inputs.get("meeting_url"):
            request_body["meeting_url"] = inputs["meeting_url"]
        
        if inputs.get("require_rsvp_approval") is not None:
            request_body["require_rsvp_approval"] = inputs["require_rsvp_approval"]
        
        if inputs.get("visibility"):
            request_body["visibility"] = inputs["visibility"]
        
        response = await context.fetch(
            build_url("/event/create"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        event = response.get("event", response)
        
        return ActionResult(data={
            "api_id": event.get("api_id", ""),
            "url": event.get("url", ""),
            "name": event.get("name", "")
        })


@luma.action("update_event")
class UpdateEventAction(ActionHandler):
    """
    Update an existing event's details.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "event_api_id": inputs["event_api_id"]
        }
        
        if inputs.get("name"):
            request_body["name"] = inputs["name"]
        
        if inputs.get("description"):
            request_body["description"] = inputs["description"]
        
        if inputs.get("start_at"):
            request_body["start_at"] = inputs["start_at"]
        
        if inputs.get("end_at"):
            request_body["end_at"] = inputs["end_at"]
        
        if inputs.get("timezone"):
            request_body["timezone"] = inputs["timezone"]
        
        if inputs.get("geo_address_json"):
            request_body["geo_address_json"] = inputs["geo_address_json"]
        
        if inputs.get("meeting_url"):
            request_body["meeting_url"] = inputs["meeting_url"]
        
        response = await context.fetch(
            build_url("/event/update"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        return ActionResult(data={
            "success": True,
            "api_id": inputs["event_api_id"]
        })


@luma.action("list_ticket_types")
class ListTicketTypesAction(ActionHandler):
    """
    Get all ticket types for an event.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        event_api_id = inputs["event_api_id"]
        
        response = await context.fetch(
            build_url("/event/ticket-types/list"),
            method="GET",
            headers=headers,
            params={"event_api_id": event_api_id}
        )
        
        ticket_types = []
        for tt in response.get("ticket_types", []):
            ticket_types.append({
                "api_id": tt.get("api_id", ""),
                "name": tt.get("name", ""),
                "price": tt.get("price", 0),
                "currency": tt.get("currency", "USD"),
                "capacity": tt.get("capacity"),
                "sold_count": tt.get("sold_count", 0)
            })
        
        return ActionResult(data={"ticket_types": ticket_types})


@luma.action("create_ticket_type")
class CreateTicketTypeAction(ActionHandler):
    """
    Create a new ticket type for an event.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "event_api_id": inputs["event_api_id"],
            "name": inputs["name"],
            "price": inputs["price"]
        }
        
        if inputs.get("currency"):
            request_body["currency"] = inputs["currency"]
        
        if inputs.get("capacity"):
            request_body["capacity"] = inputs["capacity"]
        
        if inputs.get("description"):
            request_body["description"] = inputs["description"]
        
        response = await context.fetch(
            build_url("/event/ticket-types/create"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        ticket_type = response.get("ticket_type", response)
        
        return ActionResult(data={
            "api_id": ticket_type.get("api_id", ""),
            "name": ticket_type.get("name", "")
        })


@luma.action("list_coupons")
class ListCouponsAction(ActionHandler):
    """
    Get all discount coupons for an event.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        event_api_id = inputs["event_api_id"]
        
        response = await context.fetch(
            build_url("/event/coupons"),
            method="GET",
            headers=headers,
            params={"event_api_id": event_api_id}
        )
        
        coupons = []
        for coupon in response.get("coupons", []):
            coupons.append({
                "api_id": coupon.get("api_id", ""),
                "code": coupon.get("code", ""),
                "discount_type": coupon.get("discount_type", ""),
                "discount_value": coupon.get("discount_value", 0),
                "uses_remaining": coupon.get("uses_remaining")
            })
        
        return ActionResult(data={"coupons": coupons})


@luma.action("create_coupon")
class CreateCouponAction(ActionHandler):
    """
    Create a discount coupon for an event.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "event_api_id": inputs["event_api_id"],
            "code": inputs["code"],
            "discount_type": inputs["discount_type"],
            "discount_value": inputs["discount_value"]
        }
        
        if inputs.get("max_uses"):
            request_body["max_uses"] = inputs["max_uses"]
        
        response = await context.fetch(
            build_url("/event/create-coupon"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        coupon = response.get("coupon", response)
        
        return ActionResult(data={
            "api_id": coupon.get("api_id", ""),
            "code": coupon.get("code", "")
        })
