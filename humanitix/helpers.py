"""
Humanitix integration helper functions.

This module contains shared utility functions used across multiple action files.
"""

from autohive_integrations_sdk import ExecutionContext
from typing import Dict, Any

# Humanitix API configuration
HUMANITIX_API_BASE = "https://api.humanitix.com/v1"


def get_api_headers(context: ExecutionContext) -> Dict[str, str]:
    """
    Get the authentication headers for Humanitix API requests.

    The Humanitix API uses the x-api-key header for authentication.

    Args:
        context: The execution context with authentication credentials

    Returns:
        Dictionary of headers to include in API requests
    """
    credentials = context.auth.get("credentials", {})
    api_key = credentials.get("api_key", "")

    return {
        "x-api-key": api_key,
        "Accept": "application/json"
    }


def _build_event_response(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an event object from the Humanitix API into a consistent response format.

    Args:
        event: Raw event data from the API

    Returns:
        Normalized event object with consistent field names
    """
    # Handle nested location/venue data
    location = event.get("location", {}) or {}
    venue = event.get("venue", {}) or {}

    # Merge location and venue info
    venue_info = {
        "name": venue.get("name") or location.get("name", ""),
        "address": location.get("address") or venue.get("address", ""),
        "city": location.get("city", ""),
        "state": location.get("state", ""),
        "country": location.get("country", "")
    }

    return {
        "id": event.get("_id", ""),
        "name": event.get("name", ""),
        "slug": event.get("slug", ""),
        "status": event.get("status", ""),
        "timezone": event.get("timezone", ""),
        "start_date": event.get("startDate") or event.get("start_date", ""),
        "end_date": event.get("endDate") or event.get("end_date", ""),
        "venue": venue_info,
        "url": event.get("eventUrl") or event.get("url", "")
    }


def _build_order_response(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an order object from the Humanitix API into a consistent response format.

    Args:
        order: Raw order data from the API

    Returns:
        Normalized order object with consistent field names
    """
    buyer = order.get("buyer", {}) or order.get("contact", {}) or {}
    tickets = order.get("tickets", []) or []

    return {
        "id": order.get("_id", ""),
        "order_number": order.get("orderNumber") or order.get("orderId", ""),
        "status": order.get("status", ""),
        "created_at": order.get("createdAt") or order.get("created_at", ""),
        "buyer": {
            "first_name": buyer.get("firstName") or buyer.get("first_name", ""),
            "last_name": buyer.get("lastName") or buyer.get("last_name", ""),
            "email": buyer.get("email", "")
        },
        "total_amount": order.get("totalAmount") or order.get("total", 0),
        "currency": order.get("currency", ""),
        "ticket_count": len(tickets) if isinstance(tickets, list) else order.get("ticketCount", 0)
    }


def _build_ticket_response(ticket: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a ticket object from the Humanitix API into a consistent response format.

    Args:
        ticket: Raw ticket data from the API

    Returns:
        Normalized ticket object with consistent field names
    """
    attendee = ticket.get("attendee", {}) or ticket.get("ticketHolder", {}) or {}

    checked_in = ticket.get("checkedIn", False) or ticket.get("checked_in", False)
    checked_in_at = ticket.get("checkedInAt") or ticket.get("checked_in_at")

    return {
        "id": ticket.get("_id", ""),
        "ticket_type": ticket.get("ticketType") or ticket.get("ticketTypeName", ""),
        "status": ticket.get("status", ""),
        "checked_in": checked_in,
        "checked_in_at": checked_in_at if checked_in else None,
        "attendee": {
            "first_name": attendee.get("firstName") or attendee.get("first_name", ""),
            "last_name": attendee.get("lastName") or attendee.get("last_name", ""),
            "email": attendee.get("email", "")
        },
        "order_id": ticket.get("orderId") or ticket.get("order_id", "")
    }


def _build_tag_response(tag: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a tag object from the Humanitix API into a consistent response format.

    Args:
        tag: Raw tag data from the API

    Returns:
        Normalized tag object with consistent field names
    """
    return {
        "id": tag.get("_id", ""),
        "name": tag.get("name", ""),
        "color": tag.get("color", "")
    }
