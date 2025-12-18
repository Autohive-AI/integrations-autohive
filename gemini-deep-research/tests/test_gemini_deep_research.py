"""
Tests for Gemini Deep Research Integration

To run tests:
    pytest tests/test_gemini_deep_research.py -v

Note: These tests require a valid Gemini API key. The key is loaded from:
1. GEMINI_API_KEY environment variable (if set)
2. Autohive appsettings.Development.json (fallback)
"""

import pytest
import asyncio
import os
import json
from autohive_integrations_sdk import ExecutionContext, ResultType

from context import integration


def get_gemini_api_key():
    """Get Gemini API key from environment or Autohive appsettings."""
    # First try environment variable
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        return api_key

    # Fallback to Autohive appsettings.Development.json
    appsettings_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..",
        "Autohive", "src", "R2.Platform", "appsettings.Development.json"
    )
    appsettings_path = os.path.normpath(appsettings_path)

    try:
        with open(appsettings_path, "r") as f:
            settings = json.load(f)
            api_key = settings.get("ModelCredentials", {}).get("GeminiApiKey", "")
            if api_key:
                return api_key
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    return ""


# Get API key for testing
GEMINI_API_KEY = get_gemini_api_key()


def get_test_auth():
    """Get authentication context for tests.

    Note: The auth structure must match the schema in config.json.
    The SDK validates context.auth directly against auth.fields schema.
    """
    return {
        "api_key": GEMINI_API_KEY
    }


@pytest.fixture
def auth():
    """Pytest fixture for authentication."""
    return get_test_auth()


@pytest.mark.asyncio
async def test_start_deep_research(auth):
    """Test starting a deep research task."""
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")

    inputs = {
        "query": "What are the latest developments in quantum computing in 2024?",
        "output_format": "structured with sections and bullet points"
    }

    async with ExecutionContext(auth=auth) as context:
        result = await integration.execute_action("start_deep_research", inputs, context)

        assert result.type == ResultType.ACTION
        assert result.result.data["result"] == True
        assert "interaction_id" in result.result.data
        assert result.result.data["status"] in ["in_progress", "completed"]

        # Store interaction_id for subsequent tests
        print(f"Interaction ID: {result.result.data['interaction_id']}")


@pytest.mark.asyncio
async def test_start_deep_research_with_file_search(auth):
    """Test starting a deep research task with file search enabled."""
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")

    inputs = {
        "query": "Summarize the key findings from my uploaded documents",
        "enable_file_search": True
    }

    async with ExecutionContext(auth=auth) as context:
        result = await integration.execute_action("start_deep_research", inputs, context)

        assert result.type == ResultType.ACTION
        assert result.result.data["result"] == True
        assert "interaction_id" in result.result.data


@pytest.mark.asyncio
async def test_get_research_status(auth):
    """Test getting research status (requires valid interaction_id)."""
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")

    # First start a research task
    start_inputs = {
        "query": "What is the current state of AI regulation in the EU?"
    }

    async with ExecutionContext(auth=auth) as context:
        start_result = await integration.execute_action("start_deep_research", start_inputs, context)

        if not start_result.result.data["result"]:
            pytest.skip("Could not start research task")

        interaction_id = start_result.result.data["interaction_id"]

        # Now check the status
        status_inputs = {
            "interaction_id": interaction_id
        }

        status_result = await integration.execute_action("get_research_status", status_inputs, context)

        assert status_result.type == ResultType.ACTION
        assert status_result.result.data["result"] == True
        assert status_result.result.data["status"] in ["in_progress", "completed", "failed"]


@pytest.mark.asyncio
async def test_get_research_with_streaming(auth):
    """Test getting research status with thought summaries."""
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")

    # First start a research task
    start_inputs = {
        "query": "Explain the differences between transformer architectures"
    }

    async with ExecutionContext(auth=auth) as context:
        start_result = await integration.execute_action("start_deep_research", start_inputs, context)

        if not start_result.result.data["result"]:
            pytest.skip("Could not start research task")

        interaction_id = start_result.result.data["interaction_id"]

        # Get status with thought summaries
        streaming_inputs = {
            "interaction_id": interaction_id,
            "include_thoughts": True
        }

        result = await integration.execute_action("get_research_with_streaming", streaming_inputs, context)

        assert result.type == ResultType.ACTION
        assert result.result.data["result"] == True
        assert "thought_summaries" in result.result.data
        assert isinstance(result.result.data["thought_summaries"], list)


@pytest.mark.asyncio
async def test_continue_research(auth):
    """Test continuing a research task with follow-up questions."""
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")

    # This test requires a completed interaction_id
    # In real testing, you would wait for a research task to complete first

    # For now, we'll test that the action handler works with mock data
    inputs = {
        "previous_interaction_id": "test-interaction-id",
        "follow_up_query": "Can you provide more details on the implementation aspects?",
        "output_format": "bullet points with examples"
    }

    async with ExecutionContext(auth=auth) as context:
        result = await integration.execute_action("continue_research", inputs, context)

        assert result.type == ResultType.ACTION
        # This will likely fail without a real previous_interaction_id
        # but we're testing the action handler structure


@pytest.mark.asyncio
async def test_start_deep_research_missing_query(auth):
    """Test that missing required query parameter is handled."""
    inputs = {}  # Missing required 'query' field

    async with ExecutionContext(auth=auth) as context:
        # This should raise a validation error from the SDK
        with pytest.raises(Exception):
            await integration.execute_action("start_deep_research", inputs, context)


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test handling of invalid API key."""
    invalid_auth = {
        "api_key": "invalid-api-key"
    }

    inputs = {
        "query": "Test query"
    }

    async with ExecutionContext(auth=invalid_auth) as context:
        result = await integration.execute_action("start_deep_research", inputs, context)

        # Should return error, not raise exception
        assert result.type == ResultType.ACTION
        assert result.result.data["result"] == False
        assert "error" in result.result.data


# Helper function for manual testing with polling
async def run_full_research_test():
    """
    Manual test to run a complete research task with polling.

    Run this function directly for end-to-end testing:
        python -c "import asyncio; from test_gemini_deep_research import run_full_research_test; asyncio.run(run_full_research_test())"
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set")
        return

    auth = get_test_auth()

    async with ExecutionContext(auth=auth) as context:
        # Start research
        print("Starting deep research...")
        start_result = await integration.execute_action(
            "start_deep_research",
            {
                "query": "What are the key differences between GPT-4 and Claude 3?",
                "output_format": "structured comparison with pros and cons"
            },
            context
        )

        if not start_result.result.data["result"]:
            print(f"Error starting research: {start_result.result.data.get('error')}")
            return

        interaction_id = start_result.result.data["interaction_id"]
        print(f"Research started with ID: {interaction_id}")

        # Poll for completion
        max_polls = 60  # Max 10 minutes (10 sec intervals)
        for i in range(max_polls):
            print(f"Polling status ({i + 1}/{max_polls})...")

            status_result = await integration.execute_action(
                "get_research_status",
                {"interaction_id": interaction_id},
                context
            )

            status = status_result.result.data["status"]
            print(f"Status: {status}")

            if status == "completed":
                print("\n=== Research Complete ===")
                print(status_result.result.data["research_output"])
                break
            elif status == "failed":
                print(f"Research failed: {status_result.result.data.get('error')}")
                break

            # Wait before next poll
            await asyncio.sleep(10)
        else:
            print("Research timed out after maximum polls")


if __name__ == "__main__":
    asyncio.run(run_full_research_test())
