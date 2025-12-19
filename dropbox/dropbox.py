from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any
import aiohttp
import json
import base64

# Create the integration using the config.json
dropbox = Integration.load()

# Base URLs for Dropbox API
DROPBOX_API_BASE_URL = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT_BASE_URL = "https://content.dropboxapi.com/2"


# Note: Authentication is handled automatically by the platform OAuth integration.
# The context.fetch method automatically includes the OAuth token in requests.


# ---- Action Handlers ----

# ---- File and Folder Listing Handlers ----

@dropbox.action("list_folder")
class ListFolderAction(ActionHandler):
    """List contents of a folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build request body
            data = {
                "path": inputs.get('path', ''),
                "recursive": inputs.get('recursive', False),
                "include_deleted": inputs.get('include_deleted', False),
                "include_has_explicit_shared_members": inputs.get('include_has_explicit_shared_members', False),
                "include_mounted_folders": inputs.get('include_mounted_folders', True)
            }

            if 'limit' in inputs:
                data['limit'] = inputs['limit']

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/list_folder",
                method="POST",
                json=data
            )

            entries = response.get('entries', [])
            cursor = response.get('cursor')
            has_more = response.get('has_more', False)

            return ActionResult(
                data={
                    "entries": entries,
                    "cursor": cursor,
                    "has_more": has_more,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"entries": [], "cursor": None, "has_more": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@dropbox.action("list_folder_continue")
class ListFolderContinueAction(ActionHandler):
    """Continue listing folder contents using a cursor from list_folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {"cursor": inputs['cursor']}

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/list_folder/continue",
                method="POST",
                json=data
            )

            entries = response.get('entries', [])
            cursor = response.get('cursor')
            has_more = response.get('has_more', False)

            return ActionResult(
                data={
                    "entries": entries,
                    "cursor": cursor,
                    "has_more": has_more,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"entries": [], "cursor": None, "has_more": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Metadata Handlers ----

@dropbox.action("get_metadata")
class GetMetadataAction(ActionHandler):
    """Get metadata for a file or folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {
                "path": inputs['path'],
                "include_deleted": inputs.get('include_deleted', False),
                "include_has_explicit_shared_members": inputs.get('include_has_explicit_shared_members', False)
            }

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/get_metadata",
                method="POST",
                json=data
            )

            return ActionResult(
                data={"metadata": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Download Handlers ----

@dropbox.action("get_temporary_link")
class GetTemporaryLinkAction(ActionHandler):
    """Get a temporary link to stream content of a file."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {"path": inputs['path']}

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/get_temporary_link",
                method="POST",
                json=data
            )

            link = response.get('link')
            metadata = response.get('metadata', {})

            return ActionResult(
                data={
                    "link": link,
                    "metadata": metadata,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"link": None, "metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Write Operations ----

@dropbox.action("upload_file")
class UploadFileAction(ActionHandler):
    """Upload a file to Dropbox."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Build Dropbox-API-Arg header with upload parameters
            api_arg = {
                "path": inputs['path'],
                "mode": inputs.get('mode', 'add'),
                "autorename": inputs.get('autorename', False),
                "mute": inputs.get('mute', False)
            }

            # Get file content - expected as base64 or bytes
            content = inputs.get('content', b'')
            if isinstance(content, str):
                content = base64.b64decode(content)

            # Use aiohttp directly for content upload (context.fetch doesn't handle this properly)
            url = f"{DROPBOX_CONTENT_BASE_URL}/files/upload"

            async with context:
                session = context._session
                if not session:
                    session = aiohttp.ClientSession()
                    context._session = session

                # Get auth headers from context
                headers = {
                    "Dropbox-API-Arg": json.dumps(api_arg),
                    "Content-Type": "application/octet-stream"
                }
                if context.auth and "credentials" in context.auth:
                    credentials = context.auth["credentials"]
                    if "access_token" in credentials:
                        headers["Authorization"] = f"Bearer {credentials['access_token']}"

                async with session.post(url, headers=headers, data=content) as response:
                    if response.status not in [200, 201]:
                        error_text = await response.text()
                        return ActionResult(
                            data={"file": {}, "result": False, "error": f"Dropbox upload error: {response.status} - {error_text}"},
                            cost_usd=0.0
                        )

                    upload_result = await response.json()
                    return ActionResult(
                        data={"file": upload_result, "result": True},
                        cost_usd=0.0
                    )

        except Exception as e:
            return ActionResult(
                data={"file": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@dropbox.action("create_folder")
class CreateFolderAction(ActionHandler):
    """Create a new folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {
                "path": inputs['path'],
                "autorename": inputs.get('autorename', False)
            }

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/create_folder_v2",
                method="POST",
                json=data
            )

            return ActionResult(
                data={"folder": response.get('metadata', {}), "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"folder": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@dropbox.action("delete")
class DeleteAction(ActionHandler):
    """Delete a file or folder."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {"path": inputs['path']}

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/delete_v2",
                method="POST",
                json=data
            )

            return ActionResult(
                data={"metadata": response.get('metadata', {}), "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@dropbox.action("move")
class MoveAction(ActionHandler):
    """Move a file or folder to a different location."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {
                "from_path": inputs['from_path'],
                "to_path": inputs['to_path'],
                "autorename": inputs.get('autorename', False),
                "allow_ownership_transfer": inputs.get('allow_ownership_transfer', False)
            }

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/move_v2",
                method="POST",
                json=data
            )

            return ActionResult(
                data={"metadata": response.get('metadata', {}), "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@dropbox.action("copy")
class CopyAction(ActionHandler):
    """Copy a file or folder to a different location."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            data = {
                "from_path": inputs['from_path'],
                "to_path": inputs['to_path'],
                "autorename": inputs.get('autorename', False)
            }

            response = await context.fetch(
                f"{DROPBOX_API_BASE_URL}/files/copy_v2",
                method="POST",
                json=data
            )

            return ActionResult(
                data={"metadata": response.get('metadata', {}), "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


