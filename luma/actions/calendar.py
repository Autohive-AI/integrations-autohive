"""
Luma Calendar actions - List events, people, and calendar-level operations.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

from luma import luma
from helpers import get_auth_headers, build_url, build_public_url, format_event_response


@luma.action("get_events")
class GetEventsAction(ActionHandler):
    """
    Get events from the calendar.
    
    Can fetch a single event by API ID or list all events with pagination.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        event_api_id = inputs.get("event_api_id")
        
        if event_api_id:
            response = await context.fetch(
                build_url("/event/get"),
                method="GET",
                headers=headers,
                params={"event_api_id": event_api_id}
            )
            
            events = [format_event_response(response)]
            next_cursor = None
        else:
            limit = min(inputs.get("limit", 50), 100)
            
            params = {
                "pagination_limit": limit
            }
            
            if inputs.get("after"):
                params["after"] = inputs["after"]
            
            if inputs.get("pagination_cursor"):
                params["pagination_cursor"] = inputs["pagination_cursor"]
            
            response = await context.fetch(
                build_public_url("/calendar/list-events"),
                method="GET",
                headers=headers,
                params=params
            )
            
            events = [format_event_response(entry) for entry in response.get("entries", [])]
            next_cursor = response.get("next_cursor")
        
        return ActionResult(data={
            "events": events,
            "next_cursor": next_cursor
        })


@luma.action("list_people")
class ListPeopleAction(ActionHandler):
    """
    Get a list of people (contacts) associated with the calendar.
    
    Returns people who have registered for or attended events.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        headers = get_auth_headers(context)
        limit = min(inputs.get("limit", 50), 100)
        
        params = {
            "pagination_limit": limit
        }
        
        if inputs.get("pagination_cursor"):
            params["pagination_cursor"] = inputs["pagination_cursor"]
        
        response = await context.fetch(
            build_url("/calendar/list-people"),
            method="GET",
            headers=headers,
            params=params
        )
        
        people = []
        for entry in response.get("entries", []):
            person = entry.get("person", entry)
            user = entry.get("user", {})
            
            people.append({
                "api_id": person.get("api_id", ""),
                "email": user.get("email") or person.get("email", ""),
                "name": user.get("name") or person.get("name", ""),
                "events_attended": person.get("events_attended", 0)
            })
        
        return ActionResult(data={
            "people": people,
            "next_cursor": response.get("next_cursor")
        })
