import asyncio
from typing import Any, Dict, Optional

from context import facebook


class MockExecutionContext:
    def __init__(self, responses: Dict[str, Any]):
        self.auth = {}
        self._responses = responses

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        if "/me/accounts" in url and method == "GET":
            return self._responses.get("GET /me/accounts", {"data": []})
        if "/feed" in url and method == "POST":
            return self._responses.get("POST /feed", {"id": ""})
        return {}


async def test_list_pages_success():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "category": "Business",
                    "access_token": "page_token_123"
                },
                {
                    "id": "987654321",
                    "name": "My Personal Brand",
                    "category": "Personal Blog",
                    "access_token": "page_token_456"
                }
            ]
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("list_pages", {}, context)
    data = result.result.data

    assert "pages" in data
    assert len(data["pages"]) == 2
    assert data["pages"][0]["id"] == "123456789"
    assert data["pages"][0]["name"] == "My Business Page"
    assert data["pages"][0]["category"] == "Business"
    assert data["pages"][0]["access_token"] == "page_token_123"


async def test_list_pages_empty():
    responses = {
        "GET /me/accounts": {"data": []}
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("list_pages", {}, context)
    data = result.result.data

    assert "pages" in data
    assert len(data["pages"]) == 0


async def test_create_post_success():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "access_token": "page_token_123"
                }
            ]
        },
        "POST /feed": {
            "id": "123456789_111222333"
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("create_post", {
        "page_id": "123456789",
        "message": "Hello, this is a test post!"
    }, context)
    data = result.result.data

    assert data["success"] == True
    assert data["post_id"] == "123456789_111222333"
    assert "facebook.com" in data["permalink"]


async def test_create_post_with_link():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "access_token": "page_token_123"
                }
            ]
        },
        "POST /feed": {
            "id": "123456789_444555666"
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("create_post", {
        "page_id": "123456789",
        "message": "Check out our website!",
        "link": "https://example.com"
    }, context)
    data = result.result.data

    assert data["success"] == True
    assert data["post_id"] == "123456789_444555666"


async def test_create_post_page_not_found():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "access_token": "page_token_123"
                }
            ]
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("create_post", {
        "page_id": "nonexistent_page",
        "message": "This should fail"
    }, context)
    data = result.result.data

    assert data["success"] == False
    assert "error" in data
    assert "not found" in data["error"].lower()


async def test_schedule_post_success():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "access_token": "page_token_123"
                }
            ]
        },
        "POST /feed": {
            "id": "123456789_777888999"
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("schedule_post", {
        "page_id": "123456789",
        "message": "This post will be published later!",
        "scheduled_time": "2024-12-25T10:00:00+00:00"
    }, context)
    data = result.result.data

    assert data["success"] == True
    assert data["post_id"] == "123456789_777888999"
    assert data["scheduled_publish_time"] == "2024-12-25T10:00:00+00:00"


async def test_schedule_post_with_link():
    responses = {
        "GET /me/accounts": {
            "data": [
                {
                    "id": "123456789",
                    "name": "My Business Page",
                    "access_token": "page_token_123"
                }
            ]
        },
        "POST /feed": {
            "id": "123456789_101112131"
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("schedule_post", {
        "page_id": "123456789",
        "message": "Holiday sale coming soon!",
        "scheduled_time": "1735120800",
        "link": "https://example.com/sale"
    }, context)
    data = result.result.data

    assert data["success"] == True
    assert data["post_id"] == "123456789_101112131"


async def test_schedule_post_page_not_found():
    responses = {
        "GET /me/accounts": {
            "data": []
        }
    }
    context = MockExecutionContext(responses)
    result = await facebook.execute_action("schedule_post", {
        "page_id": "nonexistent",
        "message": "This should fail",
        "scheduled_time": "2024-12-25T10:00:00+00:00"
    }, context)
    data = result.result.data

    assert data["success"] == False
    assert "error" in data


async def main():
    await test_list_pages_success()
    await test_list_pages_empty()
    await test_create_post_success()
    await test_create_post_with_link()
    await test_create_post_page_not_found()
    await test_schedule_post_success()
    await test_schedule_post_with_link()
    await test_schedule_post_page_not_found()
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
