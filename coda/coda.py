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


@coda.action("update_doc")
class UpdateDocAction(ActionHandler):
    """
    Updates metadata for a Coda doc (title and icon).
    Requires Doc Maker permissions for updating the title.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required doc_id
            doc_id = inputs["doc_id"]

            # Build request body with only provided fields
            body = {}

            if "title" in inputs and inputs["title"]:
                body["title"] = inputs["title"]

            if "icon_name" in inputs and inputs["icon_name"]:
                body["iconName"] = inputs["icon_name"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}"
            response = await context.fetch(
                url,
                method="PATCH",
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


@coda.action("delete_doc")
class DeleteDocAction(ActionHandler):
    """
    Deletes a Coda doc.
    Returns HTTP 202 (Accepted) as deletion is queued for processing.
    This action is permanent and cannot be undone.
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
                method="DELETE",
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


@coda.action("list_pages")
class ListPagesAction(ActionHandler):
    """
    Lists all pages in a Coda doc.
    Returns pages with metadata including name, subtitle, icon, and parent/child relationships.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required doc_id
            doc_id = inputs["doc_id"]

            # Build query parameters
            params = {}

            if "limit" in inputs and inputs["limit"]:
                params["limit"] = inputs["limit"]

            if "page_token" in inputs and inputs["page_token"]:
                params["pageToken"] = inputs["page_token"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}/pages"
            response = await context.fetch(
                url,
                method="GET",
                headers=headers,
                params=params
            )

            # Extract pages from response
            pages = response.get("items", [])
            next_page_token = response.get("nextPageToken")

            result = {
                "pages": pages,
                "result": True
            }

            if next_page_token:
                result["next_page_token"] = next_page_token

            return result

        except Exception as e:
            return {
                "pages": [],
                "result": False,
                "error": str(e)
            }


@coda.action("get_page")
class GetPageAction(ActionHandler):
    """
    Retrieves detailed metadata for a specific page in a Coda doc.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required parameters
            doc_id = inputs["doc_id"]
            page_id_or_name = inputs["page_id_or_name"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}/pages/{page_id_or_name}"
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


@coda.action("create_page")
class CreatePageAction(ActionHandler):
    """
    Creates a new page in a Coda doc with optional content, subtitle, icon, and parent page.
    Returns HTTP 202 (Accepted) as page creation is processed asynchronously.
    Requires Doc Maker permissions.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required parameters
            doc_id = inputs["doc_id"]
            name = inputs["name"]

            # Build request body
            body = {
                "name": name
            }

            # Add optional fields
            if "subtitle" in inputs and inputs["subtitle"]:
                body["subtitle"] = inputs["subtitle"]

            if "icon_name" in inputs and inputs["icon_name"]:
                body["iconName"] = inputs["icon_name"]

            if "image_url" in inputs and inputs["image_url"]:
                body["imageUrl"] = inputs["image_url"]

            if "parent_page_id" in inputs and inputs["parent_page_id"]:
                body["parentPageId"] = inputs["parent_page_id"]

            # Add page content if provided
            if "content" in inputs and inputs["content"]:
                content_format = inputs.get("content_format", "html")
                body["pageContent"] = {
                    "type": "canvas",
                    "canvasContent": {
                        "format": content_format,
                        "content": inputs["content"]
                    }
                }

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}/pages"
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


@coda.action("update_page")
class UpdatePageAction(ActionHandler):
    """
    Updates a page's metadata (name, subtitle, icon, image).
    Cannot update page content after creation.
    Returns HTTP 202 (Accepted) as update is processed asynchronously.
    Requires Doc Maker permissions for updating title/icon.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required parameters
            doc_id = inputs["doc_id"]
            page_id_or_name = inputs["page_id_or_name"]

            # Build request body with only provided fields
            body = {}

            if "name" in inputs and inputs["name"]:
                body["name"] = inputs["name"]

            if "subtitle" in inputs and inputs["subtitle"]:
                body["subtitle"] = inputs["subtitle"]

            if "icon_name" in inputs and inputs["icon_name"]:
                body["iconName"] = inputs["icon_name"]

            if "image_url" in inputs and inputs["image_url"]:
                body["imageUrl"] = inputs["image_url"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}/pages/{page_id_or_name}"
            response = await context.fetch(
                url,
                method="PUT",
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


@coda.action("delete_page")
class DeletePageAction(ActionHandler):
    """
    Deletes the specified page from a Coda doc.
    Returns HTTP 202 (Accepted) as deletion is queued for processing.
    Use page IDs rather than names when possible.
    """

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract required parameters
            doc_id = inputs["doc_id"]
            page_id_or_name = inputs["page_id_or_name"]

            # Get auth headers
            headers = get_auth_headers(context)

            # Make API request
            url = f"{CODA_API_BASE_URL}/docs/{doc_id}/pages/{page_id_or_name}"
            response = await context.fetch(
                url,
                method="DELETE",
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
