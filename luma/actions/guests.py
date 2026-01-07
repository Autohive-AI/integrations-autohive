"""
Luma Guest actions - List, add, and manage event guests.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from luma import luma
from helpers import get_auth_headers, build_url, format_guest_response


@luma.action("get_guests")
class GetGuestsAction(ActionHandler):
    """
    Get guests registered for an event.
    
    Can fetch a single guest by API ID or list all guests with pagination.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        event_api_id = inputs["event_api_id"]
        guest_api_id = inputs.get("guest_api_id")
        
        if guest_api_id:
            params = {
                "event_api_id": event_api_id,
                "guest_api_id": guest_api_id
            }
            
            response = await context.fetch(
                build_url("/event/get-guest"),
                method="GET",
                headers=headers,
                params=params
            )
            
            guests = [format_guest_response(response)]
            next_cursor = None
        else:
            limit = min(inputs.get("limit", 50), 100)
            
            params = {
                "event_api_id": event_api_id,
                "pagination_limit": limit
            }
            
            if inputs.get("pagination_cursor"):
                params["pagination_cursor"] = inputs["pagination_cursor"]
            
            response = await context.fetch(
                build_url("/event/get-guests"),
                method="GET",
                headers=headers,
                params=params
            )
            
            guests = [format_guest_response(entry) for entry in response.get("entries", [])]
            next_cursor = response.get("next_cursor")
        
        return ActionResult(data={
            "guests": guests,
            "next_cursor": next_cursor
        })


@luma.action("add_guests")
class AddGuestsAction(ActionHandler):
    """
    Add one or more guests to an event.
    
    Guests are registered automatically and can optionally receive notifications.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        guest_list = []
        for guest in inputs["guests"]:
            guest_entry = {"email": guest["email"]}
            if guest.get("name"):
                guest_entry["name"] = guest["name"]
            guest_list.append(guest_entry)
        
        request_body = {
            "event_api_id": inputs["event_api_id"],
            "guests": guest_list
        }
        
        response = await context.fetch(
            build_url("/event/add-guests"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        return ActionResult(data={
            "success": True,
            "added_count": len(guest_list)
        })


@luma.action("update_guest_status")
class UpdateGuestStatusAction(ActionHandler):
    """
    Update a guest's approval status.
    
    Can approve, decline, or set back to pending.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "event_api_id": inputs["event_api_id"],
            "guest_api_id": inputs["guest_api_id"],
            "approval_status": inputs["approval_status"]
        }
        
        response = await context.fetch(
            build_url("/event/update-guest-status"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        return ActionResult(data={
            "success": True,
            "guest_api_id": inputs["guest_api_id"],
            "new_status": inputs["approval_status"]
        })


@luma.action("send_invites")
class SendInvitesAction(ActionHandler):
    """
    Send email invitations to a list of email addresses.
    
    Recipients will receive an email with a link to RSVP to the event.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        
        request_body = {
            "event_api_id": inputs["event_api_id"],
            "emails": inputs["emails"]
        }
        
        response = await context.fetch(
            build_url("/event/send-invites"),
            method="POST",
            headers=headers,
            json=request_body
        )
        
        return ActionResult(data={
            "success": True,
            "invited_count": len(inputs["emails"])
        })
