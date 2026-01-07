"""
Luma integration helper functions.

This module contains shared utility functions and constants used across action files.
"""

from typing import Dict, Any
from autohive_integrations_sdk import ExecutionContext


LUMA_API_BASE_URL = "https://public-api.luma.com"
LUMA_API_VERSION = "v1"


def get_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """
    Build authentication headers for Luma API requests.
    
    Luma uses a custom header 'x-luma-api-key' for authentication.
    
    Args:
        context: ExecutionContext containing auth credentials
        
    Returns:
        Dictionary with authentication and content-type headers
    """
    api_key = context.auth.get("api_key", "")
    
    return {
        "x-luma-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def build_url(endpoint: str) -> str:
    """
    Build a full URL for a Luma API endpoint.
    
    Args:
        endpoint: API endpoint path (e.g., '/event/get')
        
    Returns:
        Full URL including base and version
    """
    endpoint = endpoint.lstrip("/")
    return f"{LUMA_API_BASE_URL}/{LUMA_API_VERSION}/{endpoint}"


def build_public_url(endpoint: str) -> str:
    """
    Build a full URL for a Luma public API endpoint.
    
    Some endpoints use /public/v1/ prefix instead of /v1/.
    
    Args:
        endpoint: API endpoint path (e.g., '/calendar/list-events')
        
    Returns:
        Full URL with public prefix
    """
    endpoint = endpoint.lstrip("/")
    return f"{LUMA_API_BASE_URL}/public/{LUMA_API_VERSION}/{endpoint}"


def format_event_response(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an event response into a consistent structure.
    
    Luma returns events with nested 'event' objects in list responses,
    but flat objects in single event responses. This normalizes the format.
    
    Args:
        event_data: Raw event data from API
        
    Returns:
        Normalized event dictionary
    """
    event = event_data.get("event", event_data)
    
    geo_address = None
    if event.get("geo_address_json"):
        geo_address = event["geo_address_json"]
    
    return {
        "api_id": event_data.get("api_id") or event.get("api_id", ""),
        "name": event.get("name", ""),
        "description": event.get("description", ""),
        "description_md": event.get("description_md", ""),
        "start_at": event.get("start_at", ""),
        "end_at": event.get("end_at", ""),
        "duration_interval": event.get("duration_interval", ""),
        "timezone": event.get("timezone", ""),
        "url": event.get("url", ""),
        "cover_url": event.get("cover_url", ""),
        "visibility": event.get("visibility", ""),
        "event_type": event.get("event_type", ""),
        "geo_address": geo_address,
        "meeting_url": event.get("meeting_url"),
        "zoom_meeting_url": event.get("zoom_meeting_url"),
        "created_at": event.get("created_at", "")
    }


def format_guest_response(guest_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a guest response into a consistent structure.
    
    Args:
        guest_data: Raw guest data from API
        
    Returns:
        Normalized guest dictionary
    """
    guest = guest_data.get("guest", guest_data)
    user = guest_data.get("user", {})
    
    return {
        "api_id": guest.get("api_id", ""),
        "email": user.get("email") or guest.get("email", ""),
        "name": user.get("name") or guest.get("name", ""),
        "approval_status": guest.get("approval_status", ""),
        "registered_at": guest.get("created_at") or guest.get("registered_at", ""),
        "checked_in_at": guest.get("checked_in_at"),
        "ticket_info": guest.get("ticket_info")
    }
