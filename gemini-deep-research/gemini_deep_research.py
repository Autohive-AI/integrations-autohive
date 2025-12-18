"""
Gemini Deep Research Integration for Autohive

This integration provides access to Google's Gemini Deep Research agent,
which autonomously plans, executes, and synthesizes multi-step research tasks.
"""

import os
from autohive_integrations_sdk import (
    Integration,
    ExecutionContext,
    ActionHandler,
    ActionResult,
)
from typing import Dict, Any, List, Optional

# Load integration configuration with explicit config path
config_path = os.path.join(os.path.dirname(__file__), "config.json")
integration = Integration.load(config_path)

# API Configuration
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
AGENT_ID = "deep-research-pro-preview-12-2025"


def get_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """Get authentication headers for Gemini API requests."""
    # Handle both auth structures:
    # 1. Direct: {"api_key": "..."} (SDK validation format)
    # 2. Nested: {"credentials": {"api_key": "..."}} (runtime format)
    api_key = context.auth.get("api_key", "")
    if not api_key:
        credentials = context.auth.get("credentials", {})
        api_key = credentials.get("api_key", "")
    return {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }


def build_research_prompt(query: str, output_format: Optional[str] = None) -> str:
    """Build the full research prompt with optional formatting instructions."""
    full_query = query
    if output_format:
        full_query += f"\n\nPlease format the output as follows: {output_format}"
    return full_query


def extract_research_output(response: Dict[str, Any]) -> Optional[str]:
    """Extract the research output text from the API response."""
    outputs = response.get("outputs", [])
    if outputs:
        # Get the last output which contains the final research result
        return outputs[-1].get("text")
    return None


def extract_thought_summaries(response: Dict[str, Any]) -> List[str]:
    """Extract intermediate thinking summaries from the API response."""
    summaries = []
    outputs = response.get("outputs", [])
    for output in outputs:
        if output.get("type") == "thought_summary":
            summaries.append(output.get("text", ""))
        elif "thought" in output:
            summaries.append(output.get("thought", ""))
    return summaries


@integration.action("start_deep_research")
class StartDeepResearchAction(ActionHandler):
    """Start an autonomous deep research task using Gemini 2.0 Pro."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            # Extract inputs
            query = inputs["query"]
            output_format = inputs.get("output_format")
            enable_file_search = inputs.get("enable_file_search", False)

            # Build the research prompt
            full_query = build_research_prompt(query, output_format)

            # Build request body
            body = {
                "input": full_query,
                "agent": AGENT_ID,
                "background": True,
                "store": True
            }

            # Add file search tool if enabled
            if enable_file_search:
                body["tools"] = [{"file_search": {}}]

            # Make API request
            headers = get_auth_headers(context)
            response = await context.fetch(
                f"{API_BASE_URL}/interactions",
                method="POST",
                headers=headers,
                json=body
            )

            # Extract interaction ID and status
            interaction_id = response.get("id") or response.get("name", "").split("/")[-1]
            status = response.get("status", "in_progress")

            return ActionResult(
                data={
                    "interaction_id": interaction_id,
                    "status": status,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "interaction_id": None,
                    "status": "failed",
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@integration.action("get_research_status")
class GetResearchStatusAction(ActionHandler):
    """Check the status of a deep research task and retrieve results when complete."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            interaction_id = inputs["interaction_id"]
            headers = get_auth_headers(context)

            # Fetch interaction status
            response = await context.fetch(
                f"{API_BASE_URL}/interactions/{interaction_id}",
                method="GET",
                headers=headers
            )

            status = response.get("status", "in_progress")
            research_output = None

            # Extract research output if completed
            if status == "completed":
                research_output = extract_research_output(response)

            return ActionResult(
                data={
                    "status": status,
                    "research_output": research_output,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "status": "failed",
                    "research_output": None,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@integration.action("continue_research")
class ContinueResearchAction(ActionHandler):
    """Ask follow-up questions or request additional research on a completed task."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            previous_id = inputs["previous_interaction_id"]
            follow_up_query = inputs["follow_up_query"]
            output_format = inputs.get("output_format")

            # Build the follow-up prompt
            full_query = build_research_prompt(follow_up_query, output_format)

            # Build request body with previous interaction reference
            body = {
                "input": full_query,
                "agent": AGENT_ID,
                "background": True,
                "store": True,
                "previous_interaction_id": previous_id
            }

            headers = get_auth_headers(context)
            response = await context.fetch(
                f"{API_BASE_URL}/interactions",
                method="POST",
                headers=headers,
                json=body
            )

            # Extract new interaction ID and status
            interaction_id = response.get("id") or response.get("name", "").split("/")[-1]
            status = response.get("status", "in_progress")

            return ActionResult(
                data={
                    "interaction_id": interaction_id,
                    "status": status,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "interaction_id": None,
                    "status": "failed",
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@integration.action("get_research_with_streaming")
class GetResearchWithStreamingAction(ActionHandler):
    """Get research status with intermediate thinking summaries."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            interaction_id = inputs["interaction_id"]
            include_thoughts = inputs.get("include_thoughts", True)
            headers = get_auth_headers(context)

            # Build URL with streaming parameter for thought summaries
            url = f"{API_BASE_URL}/interactions/{interaction_id}"
            params = {}

            if include_thoughts:
                # Request agent config for thinking summaries
                params["includeThinkingSummaries"] = "true"

            response = await context.fetch(
                url,
                method="GET",
                headers=headers,
                params=params if params else None
            )

            status = response.get("status", "in_progress")
            research_output = None
            thought_summaries = []

            # Extract research output if completed
            if status == "completed":
                research_output = extract_research_output(response)

            # Extract thought summaries if available
            if include_thoughts:
                thought_summaries = extract_thought_summaries(response)

            return ActionResult(
                data={
                    "status": status,
                    "research_output": research_output,
                    "thought_summaries": thought_summaries,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "status": "failed",
                    "research_output": None,
                    "thought_summaries": [],
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )
