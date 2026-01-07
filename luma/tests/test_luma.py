"""
Tests for Luma Event Platform Integration

Tests all actions with mocked API responses to verify correct behavior
without making actual Luma API calls.
"""

import sys
import os
from typing import Any

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from luma import luma

pytestmark = pytest.mark.asyncio


class MockExecutionContext:
    """
    Mock execution context that simulates Luma API responses.
    
    Routes requests based on URL patterns and HTTP methods to return
    pre-configured responses for testing.
    """
    
    def __init__(self, responses: dict[str, Any]):
        self.auth = {
            "api_key": "test_api_key_12345"
        }
        self._responses = responses
        self._requests = []

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ):
        self._requests.append({
            "url": url,
            "method": method,
            "params": params,
            "json": json
        })
        
        if "/user/get-self" in url:
            return self._responses.get("GET /user/get-self", {
                "user": {
                    "api_id": "user_123",
                    "email": "test@example.com",
                    "name": "Test User",
                    "username": "testuser"
                }
            })
        
        if "/calendar/list-events" in url:
            return self._responses.get("GET /calendar/list-events", {"entries": []})
        
        if "/calendar/list-people" in url:
            return self._responses.get("GET /calendar/list-people", {"entries": []})
        
        if "/event/get-guests" in url:
            return self._responses.get("GET /event/get-guests", {"entries": []})
        
        if "/event/get-guest" in url:
            return self._responses.get("GET /event/get-guest", {})
        
        if "/event/get" in url and method == "GET":
            return self._responses.get("GET /event/get", {})
        
        if "/event/ticket-types/list" in url:
            return self._responses.get("GET /event/ticket-types/list", {"ticket_types": []})
        
        if "/event/ticket-types/create" in url:
            return self._responses.get("POST /event/ticket-types/create", {})
        
        if "/event/coupons" in url and method == "GET":
            return self._responses.get("GET /event/coupons", {"coupons": []})
        
        if "/event/create-coupon" in url:
            return self._responses.get("POST /event/create-coupon", {})
        
        if "/event/create" in url and method == "POST":
            return self._responses.get("POST /event/create", {})
        
        if "/event/update-guest-status" in url and method == "POST":
            return self._responses.get("POST /event/update-guest-status", {})
        
        if "/event/update" in url and method == "POST":
            return self._responses.get("POST /event/update", {"success": True})
        
        if "/event/add-guests" in url and method == "POST":
            return self._responses.get("POST /event/add-guests", {})
        
        if "/event/send-invites" in url and method == "POST":
            return self._responses.get("POST /event/send-invites", {})
        
        return {}


# =============================================================================
# GET SELF TESTS
# =============================================================================

async def test_get_self_success():
    """Test getting authenticated user info."""
    responses = {
        "GET /user/get-self": {
            "user": {
                "api_id": "usr_abc123",
                "email": "organizer@example.com",
                "name": "Event Organizer",
                "username": "organizer"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_self", {}, context)
    data = result.result.data

    assert data["api_id"] == "usr_abc123"
    assert data["email"] == "organizer@example.com"
    assert data["name"] == "Event Organizer"


# =============================================================================
# GET EVENTS TESTS
# =============================================================================

async def test_get_events_list_success():
    """Test listing events from calendar."""
    responses = {
        "GET /calendar/list-events": {
            "entries": [
                {
                    "api_id": "evt_001",
                    "event": {
                        "api_id": "evt_001",
                        "name": "Tech Meetup",
                        "description": "Monthly tech meetup",
                        "start_at": "2024-12-15T18:00:00Z",
                        "end_at": "2024-12-15T21:00:00Z",
                        "timezone": "America/New_York",
                        "url": "https://lu.ma/techmeetup",
                        "visibility": "public"
                    }
                },
                {
                    "api_id": "evt_002",
                    "event": {
                        "api_id": "evt_002",
                        "name": "Product Launch",
                        "start_at": "2024-12-20T10:00:00Z",
                        "timezone": "America/Los_Angeles"
                    }
                }
            ],
            "next_cursor": "cursor_abc"
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_events", {}, context)
    data = result.result.data

    assert "events" in data
    assert len(data["events"]) == 2
    assert data["events"][0]["name"] == "Tech Meetup"
    assert data["events"][0]["timezone"] == "America/New_York"
    assert data["next_cursor"] == "cursor_abc"


async def test_get_events_list_empty():
    """Test listing events when calendar is empty."""
    responses = {
        "GET /calendar/list-events": {"entries": []}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_events", {}, context)
    data = result.result.data

    assert len(data["events"]) == 0
    assert data["next_cursor"] is None


async def test_get_events_single_success():
    """Test getting a specific event by API ID."""
    responses = {
        "GET /event/get": {
            "api_id": "evt_001",
            "name": "Workshop: Python Basics",
            "description": "<p>Learn Python fundamentals</p>",
            "description_md": "Learn Python fundamentals",
            "start_at": "2024-12-18T14:00:00Z",
            "end_at": "2024-12-18T17:00:00Z",
            "duration_interval": "PT3H",
            "timezone": "Europe/London",
            "url": "https://lu.ma/python-workshop",
            "cover_url": "https://example.com/cover.jpg",
            "visibility": "public",
            "event_type": "workshop",
            "created_at": "2024-12-01T10:00:00Z"
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_events", {"event_api_id": "evt_001"}, context)
    data = result.result.data

    assert len(data["events"]) == 1
    assert data["events"][0]["api_id"] == "evt_001"
    assert data["events"][0]["name"] == "Workshop: Python Basics"
    assert data["events"][0]["duration_interval"] == "PT3H"
    assert data["events"][0]["timezone"] == "Europe/London"
    assert data["next_cursor"] is None


# =============================================================================
# CREATE EVENT TESTS
# =============================================================================

async def test_create_event_success():
    """Test creating a new event."""
    responses = {
        "POST /event/create": {
            "event": {
                "api_id": "evt_new_001",
                "url": "https://lu.ma/new-event",
                "name": "New Event"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("create_event", {
        "name": "New Event",
        "start_at": "2024-12-25T18:00:00",
        "timezone": "America/New_York"
    }, context)
    data = result.result.data

    assert data["api_id"] == "evt_new_001"
    assert data["url"] == "https://lu.ma/new-event"
    assert data["name"] == "New Event"


async def test_create_event_with_location():
    """Test creating an in-person event with location."""
    responses = {
        "POST /event/create": {
            "event": {
                "api_id": "evt_new_002",
                "url": "https://lu.ma/office-party",
                "name": "Office Party"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("create_event", {
        "name": "Office Party",
        "start_at": "2024-12-20T19:00:00",
        "timezone": "America/Chicago",
        "geo_address_json": {
            "address": "123 Main St",
            "city": "Chicago",
            "region": "IL",
            "country": "USA"
        }
    }, context)
    data = result.result.data

    assert data["api_id"] == "evt_new_002"
    
    request = context._requests[-1]
    assert "geo_address_json" in request["json"]


# =============================================================================
# UPDATE EVENT TESTS
# =============================================================================

async def test_update_event_success():
    """Test updating an event."""
    responses = {
        "POST /event/update": {"success": True}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("update_event", {
        "event_api_id": "evt_001",
        "name": "Updated Event Name",
        "description": "Updated description"
    }, context)
    data = result.result.data

    assert data["success"] is True
    assert data["api_id"] == "evt_001"


# =============================================================================
# GET GUESTS TESTS
# =============================================================================

async def test_get_guests_list():
    """Test listing event guests."""
    responses = {
        "GET /event/get-guests": {
            "entries": [
                {
                    "guest": {
                        "api_id": "guest_001",
                        "approval_status": "approved",
                        "created_at": "2024-12-10T10:00:00Z"
                    },
                    "user": {
                        "email": "alice@example.com",
                        "name": "Alice Smith"
                    }
                },
                {
                    "guest": {
                        "api_id": "guest_002",
                        "approval_status": "pending",
                        "created_at": "2024-12-11T14:00:00Z"
                    },
                    "user": {
                        "email": "bob@example.com",
                        "name": "Bob Jones"
                    }
                }
            ],
            "next_cursor": None
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_guests", {"event_api_id": "evt_001"}, context)
    data = result.result.data

    assert len(data["guests"]) == 2
    assert data["guests"][0]["email"] == "alice@example.com"
    assert data["guests"][0]["approval_status"] == "approved"
    assert data["guests"][1]["email"] == "bob@example.com"
    assert data["guests"][1]["approval_status"] == "pending"


async def test_get_guests_single():
    """Test fetching a single guest by API ID."""
    responses = {
        "GET /event/get-guest": {
            "guest": {
                "api_id": "guest_001",
                "approval_status": "approved",
                "created_at": "2024-12-10T10:00:00Z",
                "checked_in_at": "2024-12-15T18:05:00Z"
            },
            "user": {
                "email": "alice@example.com",
                "name": "Alice Smith"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_guests", {
        "event_api_id": "evt_001",
        "guest_api_id": "guest_001"
    }, context)
    data = result.result.data

    assert len(data["guests"]) == 1
    assert data["guests"][0]["email"] == "alice@example.com"
    assert data["guests"][0]["api_id"] == "guest_001"
    assert data["next_cursor"] is None


async def test_get_guests_empty():
    """Test getting guests when none registered."""
    responses = {
        "GET /event/get-guests": {"entries": []}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("get_guests", {"event_api_id": "evt_001"}, context)
    data = result.result.data

    assert len(data["guests"]) == 0


# =============================================================================
# ADD GUESTS TESTS
# =============================================================================

async def test_add_guests_success():
    """Test adding guests to an event."""
    responses = {
        "POST /event/add-guests": {}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("add_guests", {
        "event_api_id": "evt_001",
        "guests": [
            {"email": "new1@example.com", "name": "New Guest 1"},
            {"email": "new2@example.com"}
        ]
    }, context)
    data = result.result.data

    assert data["success"] is True
    assert data["added_count"] == 2


# =============================================================================
# UPDATE GUEST STATUS TESTS
# =============================================================================

async def test_update_guest_status_approve():
    """Test approving a guest."""
    responses = {
        "POST /event/update-guest-status": {}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("update_guest_status", {
        "event_api_id": "evt_001",
        "guest_api_id": "guest_002",
        "approval_status": "approved"
    }, context)
    data = result.result.data

    assert data["success"] is True
    assert data["guest_api_id"] == "guest_002"
    assert data["new_status"] == "approved"


async def test_update_guest_status_decline():
    """Test declining a guest."""
    responses = {
        "POST /event/update-guest-status": {}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("update_guest_status", {
        "event_api_id": "evt_001",
        "guest_api_id": "guest_003",
        "approval_status": "declined"
    }, context)
    data = result.result.data

    assert data["success"] is True
    assert data["new_status"] == "declined"


# =============================================================================
# SEND INVITES TESTS
# =============================================================================

async def test_send_invites_success():
    """Test sending event invitations."""
    responses = {
        "POST /event/send-invites": {}
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("send_invites", {
        "event_api_id": "evt_001",
        "emails": ["invite1@example.com", "invite2@example.com", "invite3@example.com"]
    }, context)
    data = result.result.data

    assert data["success"] is True
    assert data["invited_count"] == 3


# =============================================================================
# TICKET TYPES TESTS
# =============================================================================

async def test_list_ticket_types_success():
    """Test listing ticket types for an event."""
    responses = {
        "GET /event/ticket-types/list": {
            "ticket_types": [
                {
                    "api_id": "tt_001",
                    "name": "General Admission",
                    "price": 25.00,
                    "currency": "USD",
                    "capacity": 100,
                    "sold_count": 45
                },
                {
                    "api_id": "tt_002",
                    "name": "VIP",
                    "price": 75.00,
                    "currency": "USD",
                    "capacity": 20,
                    "sold_count": 15
                }
            ]
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("list_ticket_types", {"event_api_id": "evt_001"}, context)
    data = result.result.data

    assert len(data["ticket_types"]) == 2
    assert data["ticket_types"][0]["name"] == "General Admission"
    assert data["ticket_types"][0]["price"] == 25.00
    assert data["ticket_types"][1]["name"] == "VIP"


async def test_create_ticket_type_success():
    """Test creating a new ticket type."""
    responses = {
        "POST /event/ticket-types/create": {
            "ticket_type": {
                "api_id": "tt_new_001",
                "name": "Early Bird"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("create_ticket_type", {
        "event_api_id": "evt_001",
        "name": "Early Bird",
        "price": 15.00,
        "currency": "USD",
        "capacity": 50
    }, context)
    data = result.result.data

    assert data["api_id"] == "tt_new_001"
    assert data["name"] == "Early Bird"


# =============================================================================
# COUPONS TESTS
# =============================================================================

async def test_list_coupons_success():
    """Test listing coupons for an event."""
    responses = {
        "GET /event/coupons": {
            "coupons": [
                {
                    "api_id": "coupon_001",
                    "code": "EARLYBIRD20",
                    "discount_type": "percentage",
                    "discount_value": 20,
                    "uses_remaining": 50
                }
            ]
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("list_coupons", {"event_api_id": "evt_001"}, context)
    data = result.result.data

    assert len(data["coupons"]) == 1
    assert data["coupons"][0]["code"] == "EARLYBIRD20"
    assert data["coupons"][0]["discount_value"] == 20


async def test_create_coupon_success():
    """Test creating a discount coupon."""
    responses = {
        "POST /event/create-coupon": {
            "coupon": {
                "api_id": "coupon_new_001",
                "code": "FLASH50"
            }
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("create_coupon", {
        "event_api_id": "evt_001",
        "code": "FLASH50",
        "discount_type": "percentage",
        "discount_value": 50,
        "max_uses": 10
    }, context)
    data = result.result.data

    assert data["api_id"] == "coupon_new_001"
    assert data["code"] == "FLASH50"


# =============================================================================
# LIST PEOPLE TESTS
# =============================================================================

async def test_list_people_success():
    """Test listing calendar people/contacts."""
    responses = {
        "GET /calendar/list-people": {
            "entries": [
                {
                    "person": {
                        "api_id": "person_001",
                        "events_attended": 5
                    },
                    "user": {
                        "email": "regular@example.com",
                        "name": "Regular Attendee"
                    }
                }
            ]
        }
    }
    context = MockExecutionContext(responses)
    result = await luma.execute_action("list_people", {}, context)
    data = result.result.data

    assert len(data["people"]) == 1
    assert data["people"][0]["email"] == "regular@example.com"
    assert data["people"][0]["events_attended"] == 5
