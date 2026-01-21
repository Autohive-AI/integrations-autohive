"""
Tests for LinkedIn Integration

Tests all actions with mocked API responses to verify correct behavior
without making actual LinkedIn API calls.
"""

from typing import Any

import pytest

from context import linkedin

pytestmark = pytest.mark.asyncio


class MockExecutionContext:
    """
    Mock execution context that simulates LinkedIn API responses.

    Routes requests based on URL patterns and HTTP methods to return
    pre-configured responses for testing.
    """

    def __init__(self, responses: dict[str, Any] = None):
        self.auth = {}
        self._responses = responses or {}
        self._requests = []

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ):
        self._requests.append({
            "url": url,
            "method": method,
            "params": params,
            "data": data,
            "json": json,
            "headers": headers
        })

        # Userinfo endpoint
        if "/userinfo" in url and method == "GET":
            return self._responses.get("GET /userinfo", {
                "sub": "abc123",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "picture": "https://media.licdn.com/pic.jpg",
                "locale": "en-US",
                "email": "test@example.com",
                "email_verified": True
            })

        # Posts endpoint
        if "/rest/posts" in url and method == "POST":
            return self._responses.get("POST /posts", {
                "id": "urn:li:share:123456789",
                "author": "urn:li:person:abc123",
                "lifecycleState": "PUBLISHED",
                "visibility": "PUBLIC",
                "commentary": "Test post",
                "createdAt": 1705849200000,
                "publishedAt": 1705849200000
            })

        return {}


# =============================================================================
# GET USER INFO TESTS
# =============================================================================

async def test_get_user_info_success():
    """Test getting user info returns correct structure."""
    responses = {
        "GET /userinfo": {
            "sub": "user123",
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "picture": "https://media.licdn.com/profile.jpg",
            "locale": "en-US",
            "email": "john.doe@example.com",
            "email_verified": True
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("get_user_info", {}, context)
    data = result.result.data

    assert data["result"] == "User information retrieved successfully"
    assert data["user_info"]["sub"] == "user123"
    assert data["user_info"]["name"] == "John Doe"
    assert data["user_info"]["given_name"] == "John"
    assert data["user_info"]["family_name"] == "Doe"
    assert data["user_info"]["email"] == "john.doe@example.com"
    assert data["user_info"]["email_verified"] == True


async def test_get_user_info_without_email():
    """Test getting user info when email scope not granted."""
    responses = {
        "GET /userinfo": {
            "sub": "user456",
            "name": "Jane Smith",
            "given_name": "Jane",
            "family_name": "Smith",
            "picture": "https://media.licdn.com/jane.jpg",
            "locale": "en-GB"
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("get_user_info", {}, context)
    data = result.result.data

    assert data["result"] == "User information retrieved successfully"
    assert data["user_info"]["sub"] == "user456"
    assert data["user_info"]["name"] == "Jane Smith"
    assert "email" not in data["user_info"]


async def test_get_user_info_error():
    """Test handling error response from userinfo endpoint."""
    responses = {
        "GET /userinfo": {
            "error": "invalid_token",
            "error_description": "The access token is invalid"
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("get_user_info", {}, context)
    data = result.result.data

    assert data["result"] == "Failed to retrieve user information"
    assert data["user_info"] is None


# =============================================================================
# SHARE CONTENT TESTS
# =============================================================================

async def test_share_content_success():
    """Test sharing content successfully."""
    responses = {
        "GET /userinfo": {
            "sub": "user789",
            "name": "Test User"
        },
        "POST /posts": {
            "id": "urn:li:share:987654321",
            "author": "urn:li:person:user789",
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC",
            "commentary": "Hello LinkedIn!",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("share_content", {
        "content": "Hello LinkedIn!"
    }, context)
    data = result.result.data

    assert data["result"] == "Content shared successfully."
    assert data["post_id"] == "urn:li:share:987654321"
    assert data["post_data"]["author"] == "urn:li:person:user789"
    assert data["post_data"]["lifecycleState"] == "PUBLISHED"


async def test_share_content_with_author_id():
    """Test sharing content with explicit author_id."""
    responses = {
        "POST /posts": {
            "id": "urn:li:share:111222333",
            "author": "urn:li:person:explicit_user",
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC",
            "commentary": "Post with explicit author",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("share_content", {
        "content": "Post with explicit author",
        "author_id": "explicit_user"
    }, context)
    data = result.result.data

    assert data["result"] == "Content shared successfully."
    assert data["post_id"] == "urn:li:share:111222333"

    # Verify userinfo was not called (author_id provided)
    userinfo_calls = [r for r in context._requests if "/userinfo" in r["url"]]
    assert len(userinfo_calls) == 0


async def test_share_content_with_connections_visibility():
    """Test sharing content with CONNECTIONS visibility."""
    responses = {
        "GET /userinfo": {
            "sub": "user_conn",
            "name": "Connections User"
        },
        "POST /posts": {
            "id": "urn:li:share:conn123",
            "author": "urn:li:person:user_conn",
            "lifecycleState": "PUBLISHED",
            "visibility": "CONNECTIONS",
            "commentary": "Only for connections",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("share_content", {
        "content": "Only for connections",
        "visibility": "CONNECTIONS"
    }, context)
    data = result.result.data

    assert data["result"] == "Content shared successfully."

    # Verify the request had CONNECTIONS visibility
    post_calls = [r for r in context._requests if "/rest/posts" in r["url"]]
    assert len(post_calls) == 1
    assert post_calls[0]["json"]["visibility"] == "CONNECTIONS"


async def test_share_content_default_visibility():
    """Test that default visibility is PUBLIC."""
    responses = {
        "GET /userinfo": {
            "sub": "user_pub",
            "name": "Public User"
        },
        "POST /posts": {
            "id": "urn:li:share:pub123",
            "author": "urn:li:person:user_pub",
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC",
            "commentary": "Public post",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("share_content", {
        "content": "Public post"
    }, context)
    data = result.result.data

    assert data["result"] == "Content shared successfully."

    # Verify the request had PUBLIC visibility (default)
    post_calls = [r for r in context._requests if "/rest/posts" in r["url"]]
    assert len(post_calls) == 1
    assert post_calls[0]["json"]["visibility"] == "PUBLIC"


async def test_share_content_userinfo_failure():
    """Test handling when userinfo fails and no author_id provided."""
    responses = {
        "GET /userinfo": {
            "error": "unauthorized"
        }
    }
    context = MockExecutionContext(responses)
    result = await linkedin.execute_action("share_content", {
        "content": "This will fail"
    }, context)
    data = result.result.data

    assert "Failed to share content" in data["result"]
    assert data["post_id"] is None
    assert data["post_data"] is None


async def test_share_content_verifies_headers():
    """Test that correct LinkedIn API headers are sent."""
    responses = {
        "GET /userinfo": {
            "sub": "header_user",
            "name": "Header Test"
        },
        "POST /posts": {
            "id": "urn:li:share:header123",
            "author": "urn:li:person:header_user",
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC",
            "commentary": "Header test",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    await linkedin.execute_action("share_content", {
        "content": "Header test"
    }, context)

    # Verify headers on POST request
    post_calls = [r for r in context._requests if "/rest/posts" in r["url"]]
    assert len(post_calls) == 1
    headers = post_calls[0]["headers"]
    assert headers["LinkedIn-Version"] == "202501"
    assert headers["X-Restli-Protocol-Version"] == "2.0.0"
    assert headers["Content-Type"] == "application/json"


async def test_share_content_payload_structure():
    """Test that the post payload has correct structure."""
    responses = {
        "GET /userinfo": {
            "sub": "struct_user",
            "name": "Structure Test"
        },
        "POST /posts": {
            "id": "urn:li:share:struct123",
            "author": "urn:li:person:struct_user",
            "lifecycleState": "PUBLISHED",
            "visibility": "PUBLIC",
            "commentary": "Structure test content",
            "createdAt": 1705849200000,
            "publishedAt": 1705849200000
        }
    }
    context = MockExecutionContext(responses)
    await linkedin.execute_action("share_content", {
        "content": "Structure test content"
    }, context)

    # Verify payload structure
    post_calls = [r for r in context._requests if "/rest/posts" in r["url"]]
    payload = post_calls[0]["json"]

    assert payload["author"] == "urn:li:person:struct_user"
    assert payload["commentary"] == "Structure test content"
    assert payload["visibility"] == "PUBLIC"
    assert payload["lifecycleState"] == "PUBLISHED"
    assert payload["isReshareDisabledByAuthor"] == False
    assert "distribution" in payload
    assert payload["distribution"]["feedDistribution"] == "MAIN_FEED"


# =============================================================================
# INPUT VALIDATION TESTS
# =============================================================================

async def test_share_content_missing_content():
    """Test that content is required for share_content."""
    context = MockExecutionContext({})

    with pytest.raises(Exception) as exc_info:
        await linkedin.execute_action("share_content", {}, context)

    assert "content" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
