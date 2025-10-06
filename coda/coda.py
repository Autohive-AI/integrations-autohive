from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional

# Create the integration using the config.json
coda = Integration.load()

# Base URL for Coda API
CODA_API_BASE_URL = "https://coda.io/apis/v1"


# ---- Helper Functions ----

def get_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """
    Build authentication headers for Coda API requests.

    Args:
        context: ExecutionContext containing auth credentials

    Returns:
        Dictionary with Authorization and Content-Type headers
    """
    credentials = context.auth.get("credentials", {})
    api_token = credentials.get("api_token", "")

    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }


# ---- Action Handlers ----

@coda.action("list_docs")
class ListDocsAction(ActionHandler):
    """
    Lists all Coda docs accessible by the authenticated user.
    Returns docs in reverse chronological order by latest relevant event.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build query parameters
            params = {}

            if "is_owner" in inputs and inputs["is_owner"] is not None:
                params["isOwner"] = str(inputs["is_owner"]).lower()

            if "query" in inputs and inputs["query"]:
                params["query"] = inputs["query"]

            if "source_doc" in inputs and inputs["source_doc"]:
                params["sourceDoc"] = inputs["source_doc"]

            if "is_published" in inputs and inputs["is_published"] is not None:
                params["isPublished"] = str(inputs["is_published"]).lower()

            if "is_starred" in inputs and inputs["is_starred"] is not None:
                params["isStarred"] = str(inputs["is_starred"]).lower()

            if "limit" in inputs and inputs["limit"]:
                params["limit"] = inputs["limit"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs"
            response = await context.fetch(
                url,
                method="GET",
                headers=headers,
                params=params
            )

            # Extract docs from response
            docs = response.get("items", [])

            return {
                "docs": docs,
                "result": True
            }

        except Exception as e:
            return {
                "docs": [],
                "result": False,
                "error": str(e)
            }


@coda.action("get_doc")
class GetDocAction(ActionHandler):
    """
    Retrieves metadata for a specific Coda doc by its ID.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required doc_id
            doc_id = inputs["doc_id"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}"
            response = await context.fetch(
                url,
                method="GET",
                headers=headers
            )

            return {
                "data": response,
                "result": True
            }

        except Exception as e:
            return {
                "data": {},
                "result": False,
                "error": str(e)
            }


@coda.action("create_doc")
class CreateDocAction(ActionHandler):
    """
    Creates a new Coda doc with the specified title.
    Optionally copies content from an existing doc.
    Returns HTTP 202 (Accepted) as doc creation is processed asynchronously.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build request body
            body = {
                "title": inputs["title"]
            }

            # Add optional fields if provided
            if "source_doc" in inputs and inputs["source_doc"]:
                body["sourceDoc"] = inputs["source_doc"]

            if "timezone" in inputs and inputs["timezone"]:
                body["timezone"] = inputs["timezone"]

            if "folder_id" in inputs and inputs["folder_id"]:
                body["folderId"] = inputs["folder_id"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs"
            response = await context.fetch(
                url,
                method="POST",
                headers=headers,
                json=body
            )

            return {
                "data": response,
                "result": True
            }

        except Exception as e:
            return {
                "data": {},
                "result": False,
                "error": str(e)
            }
