from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any, Optional
import aiohttp
import time
import os

# Create the integration using the config.json from the same directory as this file
config_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_dir, 'config.json')
grammarly = Integration.load(config_path)

# Base URLs for Grammarly API
GRAMMARLY_TOKEN_URL = "https://auth.grammarly.com/v4/api/oauth2/token"
GRAMMARLY_WRITING_SCORE_URL = "https://api.grammarly.com/ecosystem/api/v2/scores"
GRAMMARLY_ANALYTICS_URL = "https://api.grammarly.com/ecosystem/api/v2/analytics/users"
GRAMMARLY_AI_DETECTION_URL = "https://api.grammarly.com/ecosystem/api/v1/ai-detection"
GRAMMARLY_PLAGIARISM_URL = "https://api.grammarly.com/ecosystem/api/v1/plagiarism"


# ---- Helper Functions ----

async def get_access_token(context: ExecutionContext) -> str:
    """
    Get or refresh OAuth2 access token using client credentials flow.

    Args:
        context: ExecutionContext containing auth credentials

    Returns:
        Valid access token
    """
    credentials = context.auth.get("credentials", {})
    client_id = credentials.get("client_id", "")
    client_secret = credentials.get("client_secret", "")

    # Hardcoded scopes for all API access
    scopes = "scores-api:read scores-api:write analytics-api:read ai-detection-api:read ai-detection-api:write plagiarism-api:read plagiarism-api:write"

    # Check if we have a cached token
    cached_token = credentials.get("access_token")
    token_expiry = credentials.get("token_expiry", 0)

    # If token exists and hasn't expired (with 5 min buffer), use it
    if cached_token and time.time() < (token_expiry - 300):
        return cached_token

    # Request new token using form-encoded data
    body = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scopes
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GRAMMARLY_TOKEN_URL, data=body, headers=headers) as resp:
            if resp.status == 200:
                token_data = await resp.json()
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour

                # Cache token and expiry time
                credentials["access_token"] = access_token
                credentials["token_expiry"] = time.time() + expires_in

                return access_token
            else:
                error_text = await resp.text()
                raise Exception(f"Failed to obtain access token: HTTP {resp.status}: {error_text}")


async def api_request(
    context: ExecutionContext,
    method: str,
    url: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute an API request to Grammarly API.

    Args:
        context: ExecutionContext with auth credentials
        method: HTTP method (GET, POST, etc.)
        url: Full API endpoint URL
        json_data: Optional JSON body for the request
        params: Optional query parameters

    Returns:
        API response data
    """
    access_token = await get_access_token(context)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, json=json_data, params=params) as resp:
            if resp.status in [200, 201, 202]:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"API request failed: HTTP {resp.status}: {error_text}")


async def upload_file(upload_url: str, file_content: str) -> bool:
    """
    Upload a file to a pre-signed URL.

    Args:
        upload_url: The pre-signed upload URL
        file_content: The content to upload

    Returns:
        True if upload was successful
    """
    headers = {
        "Content-Type": "text/plain"
    }

    # Use yarl.URL with encoded=True to prevent aiohttp from modifying the pre-signed URL
    # This is critical for S3 pre-signed URLs which have query parameters with signatures
    from yarl import URL
    url = URL(upload_url, encoded=True)

    async with aiohttp.ClientSession() as session:
        async with session.put(url, data=file_content.encode('utf-8'), headers=headers) as resp:
            if resp.status in [200, 201, 204]:
                return True
            else:
                error_text = await resp.text()
                raise Exception(f"File upload failed: HTTP {resp.status}: {error_text}")


# ---- Writing Score API Actions ----

@grammarly.action("create_writing_score_request")
class CreateWritingScoreRequestAction(ActionHandler):
    """Create a writing score request and get upload URL."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            payload = {
                "filename": inputs["filename"]
            }

            response = await api_request(context, "POST", GRAMMARLY_WRITING_SCORE_URL, json_data=payload)

            return ActionResult(
                data={
                    "score_request_id": response.get("score_request_id"),
                    "file_upload_url": response.get("file_upload_url"),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("upload_document_for_writing_score")
class UploadDocumentForWritingScoreAction(ActionHandler):
    """Upload a document to the pre-signed URL for writing score analysis."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            upload_url = inputs["upload_url"]
            file_content = inputs["file_content"]

            await upload_file(upload_url, file_content)

            return ActionResult(data={"result": True}, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("get_writing_score_results")
class GetWritingScoreResultsAction(ActionHandler):
    """Get the writing score results for a score request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            score_request_id = inputs["score_request_id"]
            url = f"{GRAMMARLY_WRITING_SCORE_URL}/{score_request_id}"

            response = await api_request(context, "GET", url)

            result = {
                "status": response.get("status"),
                "result": True
            }

            # Add score data if available
            if response.get("status") == "COMPLETED" and "score" in response:
                score_data = response["score"]
                result["general_score"] = score_data.get("generalScore")
                result["engagement"] = score_data.get("engagement")
                result["correctness"] = score_data.get("correctness")
                result["delivery"] = score_data.get("delivery")
                result["clarity"] = score_data.get("clarity")

            return ActionResult(data=result, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


# ---- Analytics API Actions ----

@grammarly.action("get_user_analytics")
class GetUserAnalyticsAction(ActionHandler):
    """Get user analytics data for a date range."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            params = {
                "date_from": inputs["date_from"],
                "date_to": inputs["date_to"]
            }

            if "cursor" in inputs and inputs["cursor"]:
                params["cursor"] = inputs["cursor"]

            if "limit" in inputs and inputs["limit"]:
                params["limit"] = inputs["limit"]

            response = await api_request(context, "GET", GRAMMARLY_ANALYTICS_URL, params=params)

            return ActionResult(
                data={
                    "data": response.get("data", []),
                    "paging": response.get("paging", {}),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(data={"data": [], "paging": {}, "result": False, "error": str(e)}, cost_usd=0.0)


# ---- AI Detection API Actions ----

@grammarly.action("create_ai_detection_request")
class CreateAIDetectionRequestAction(ActionHandler):
    """Create an AI detection request and get upload URL."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            payload = {
                "filename": inputs["filename"]
            }

            response = await api_request(context, "POST", GRAMMARLY_AI_DETECTION_URL, json_data=payload)

            return ActionResult(
                data={
                    "score_request_id": response.get("score_request_id"),
                    "file_upload_url": response.get("file_upload_url"),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("upload_document_for_ai_detection")
class UploadDocumentForAIDetectionAction(ActionHandler):
    """Upload a document to the pre-signed URL for AI detection analysis."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            upload_url = inputs["upload_url"]
            file_content = inputs["file_content"]

            await upload_file(upload_url, file_content)

            return ActionResult(data={"result": True}, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("get_ai_detection_results")
class GetAIDetectionResultsAction(ActionHandler):
    """Get the AI detection results for a score request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            score_request_id = inputs["score_request_id"]
            url = f"{GRAMMARLY_AI_DETECTION_URL}/{score_request_id}"

            response = await api_request(context, "GET", url)

            result = {
                "status": response.get("status"),
                "result": True
            }

            # Add score data if available
            if response.get("status") == "COMPLETED" and "score" in response:
                score_data = response["score"]
                result["average_confidence"] = score_data.get("average_confidence")
                result["ai_generated_percentage"] = score_data.get("ai_generated_percentage")
                result["updated_at"] = response.get("updated_at")

            return ActionResult(data=result, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


# ---- Plagiarism Detection API Actions ----

@grammarly.action("create_plagiarism_detection_request")
class CreatePlagiarismDetectionRequestAction(ActionHandler):
    """Create a plagiarism detection request and get upload URL."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            payload = {
                "filename": inputs["filename"]
            }

            response = await api_request(context, "POST", GRAMMARLY_PLAGIARISM_URL, json_data=payload)

            return ActionResult(
                data={
                    "score_request_id": response.get("score_request_id"),
                    "file_upload_url": response.get("file_upload_url"),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("upload_document_for_plagiarism_detection")
class UploadDocumentForPlagiarismDetectionAction(ActionHandler):
    """Upload a document to the pre-signed URL for plagiarism detection analysis."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            upload_url = inputs["upload_url"]
            file_content = inputs["file_content"]

            await upload_file(upload_url, file_content)

            return ActionResult(data={"result": True}, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)


@grammarly.action("get_plagiarism_detection_results")
class GetPlagiarismDetectionResultsAction(ActionHandler):
    """Get the plagiarism detection results for a score request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            score_request_id = inputs["score_request_id"]
            url = f"{GRAMMARLY_PLAGIARISM_URL}/{score_request_id}"

            response = await api_request(context, "GET", url)

            result = {
                "status": response.get("status"),
                "result": True
            }

            # Add score data if available
            if response.get("status") == "COMPLETED" and "score" in response:
                score_data = response["score"]
                # Calculate plagiarism percentage from originality score
                originality = score_data.get("originality_score", 100)
                result["originality_score"] = originality
                result["plagiarism_percentage"] = max(0, 100 - originality)
                result["updated_at"] = response.get("updated_at")

            return ActionResult(data=result, cost_usd=0.0)

        except Exception as e:
            return ActionResult(data={"result": False, "error": str(e)}, cost_usd=0.0)
