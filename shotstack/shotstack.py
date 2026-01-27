from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any
from urllib.parse import quote

# Create the integration using the config.json
shotstack = Integration.load()

# Base URLs for Shotstack APIs
EDIT_API_BASE = "https://api.shotstack.io/edit"
SERVE_API_BASE = "https://api.shotstack.io/serve"
INGEST_API_BASE = "https://api.shotstack.io/ingest"
CREATE_API_BASE = "https://api.shotstack.io/create"


def get_api_key(context: ExecutionContext) -> str:
    """Get API key from context credentials."""
    credentials = context.auth.get("credentials", {})
    return credentials.get("api_key", "")


def get_environment(context: ExecutionContext) -> str:
    """Get environment from context credentials (v1 or stage)."""
    credentials = context.auth.get("credentials", {})
    return credentials.get("environment", "stage")


def get_headers(context: ExecutionContext) -> Dict[str, str]:
    """Get headers with API key for authentication."""
    return {
        "x-api-key": get_api_key(context),
        "Content-Type": "application/json"
    }


# ---- Edit API: Render Handlers ----

@shotstack.action("render_video")
class RenderVideoAction(ActionHandler):
    """Submit a video render job."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            # Build the edit payload
            payload = {
                "timeline": inputs["timeline"],
                "output": inputs["output"]
            }

            # Add optional fields
            if "merge" in inputs and inputs["merge"]:
                payload["merge"] = inputs["merge"]
            if "callback" in inputs and inputs["callback"]:
                payload["callback"] = inputs["callback"]

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            # Extract render ID from response
            render_id = response.get("response", {}).get("id")
            message = response.get("response", {}).get("message", "Render job queued")

            return ActionResult(
                data={
                    "render_id": render_id,
                    "message": message,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"render_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_render_status")
class GetRenderStatusAction(ActionHandler):
    """Check the status of a render job."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            render_id = inputs["render_id"]

            params = {}
            if "data" in inputs and inputs["data"]:
                params["data"] = "true"
            if "merged" in inputs and inputs["merged"]:
                params["merged"] = "true"

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/render/{render_id}",
                method="GET",
                headers=get_headers(context),
                params=params if params else None
            )

            render_data = response.get("response", {})
            status = render_data.get("status")
            url = render_data.get("url")

            return ActionResult(
                data={
                    "render": render_data,
                    "status": status,
                    "url": url,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"render": {}, "status": None, "url": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Edit API: Template Handlers ----

@shotstack.action("create_template")
class CreateTemplateAction(ActionHandler):
    """Create a reusable template."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            payload = {
                "name": inputs["name"],
                "template": inputs["template"]
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            template_id = response.get("response", {}).get("id")
            message = response.get("response", {}).get("message", "Template created")

            return ActionResult(
                data={
                    "template_id": template_id,
                    "message": message,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"template_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("list_templates")
class ListTemplatesAction(ActionHandler):
    """List all saved templates."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates",
                method="GET",
                headers=get_headers(context)
            )

            templates = response.get("response", {}).get("templates", [])

            return ActionResult(
                data={
                    "templates": templates,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"templates": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_template")
class GetTemplateAction(ActionHandler):
    """Get a template by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            template_id = inputs["template_id"]

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates/{template_id}",
                method="GET",
                headers=get_headers(context)
            )

            template = response.get("response", {})

            return ActionResult(
                data={
                    "template": template,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"template": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("update_template")
class UpdateTemplateAction(ActionHandler):
    """Update an existing template."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            template_id = inputs["template_id"]

            payload = {
                "name": inputs["name"],
                "template": inputs["template"]
            }

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates/{template_id}",
                method="PUT",
                headers=get_headers(context),
                json=payload
            )

            message = response.get("response", {}).get("message", "Template updated")

            return ActionResult(
                data={
                    "template_id": template_id,
                    "message": message,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"template_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("delete_template")
class DeleteTemplateAction(ActionHandler):
    """Delete a template by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            template_id = inputs["template_id"]

            await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates/{template_id}",
                method="DELETE",
                headers=get_headers(context)
            )

            return ActionResult(
                data={
                    "deleted": True,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deleted": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("render_template")
class RenderTemplateAction(ActionHandler):
    """Render a video using a saved template."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            payload = {
                "id": inputs["template_id"]
            }

            # Add optional fields
            if "merge" in inputs and inputs["merge"]:
                payload["merge"] = inputs["merge"]
            if "callback" in inputs and inputs["callback"]:
                payload["callback"] = inputs["callback"]

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/templates/render",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            render_id = response.get("response", {}).get("id")
            message = response.get("response", {}).get("message", "Render job queued")

            return ActionResult(
                data={
                    "render_id": render_id,
                    "message": message,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"render_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("probe_media")
class ProbeMediaAction(ActionHandler):
    """Inspect a media file to get metadata."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            url = inputs["url"]

            # URL encode the media URL for the path parameter
            encoded_url = quote(url, safe="")

            response = await context.fetch(
                f"{EDIT_API_BASE}/{env}/probe/{encoded_url}",
                method="GET",
                headers=get_headers(context)
            )

            metadata = response.get("response", {})

            return ActionResult(
                data={
                    "metadata": metadata,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metadata": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Serve API: Asset Handlers ----

@shotstack.action("get_asset")
class GetAssetAction(ActionHandler):
    """Get details of a hosted asset."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            asset_id = inputs["asset_id"]

            response = await context.fetch(
                f"{SERVE_API_BASE}/{env}/assets/{asset_id}",
                method="GET",
                headers=get_headers(context)
            )

            asset = response.get("data", {})

            return ActionResult(
                data={
                    "asset": asset,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"asset": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("delete_asset")
class DeleteAssetAction(ActionHandler):
    """Delete a hosted asset."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            asset_id = inputs["asset_id"]

            await context.fetch(
                f"{SERVE_API_BASE}/{env}/assets/{asset_id}",
                method="DELETE",
                headers=get_headers(context)
            )

            return ActionResult(
                data={
                    "deleted": True,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deleted": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_render_assets")
class GetRenderAssetsAction(ActionHandler):
    """Get all assets from a render job."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            render_id = inputs["render_id"]

            response = await context.fetch(
                f"{SERVE_API_BASE}/{env}/assets/render/{render_id}",
                method="GET",
                headers=get_headers(context)
            )

            assets = response.get("data", [])
            if not isinstance(assets, list):
                assets = [assets] if assets else []

            return ActionResult(
                data={
                    "assets": assets,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"assets": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("transfer_asset")
class TransferAssetAction(ActionHandler):
    """Transfer an asset to external storage."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            payload = {
                "url": inputs["url"],
                "destinations": inputs["destinations"]
            }

            response = await context.fetch(
                f"{SERVE_API_BASE}/{env}/assets",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            transfer = response.get("data", {})

            return ActionResult(
                data={
                    "transfer": transfer,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"transfer": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Ingest API: Source Handlers ----

@shotstack.action("ingest_source")
class IngestSourceAction(ActionHandler):
    """Ingest a source file for video editing."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            payload = {
                "url": inputs["url"]
            }

            # Add optional fields
            if "outputs" in inputs and inputs["outputs"]:
                payload["outputs"] = inputs["outputs"]
            if "callback" in inputs and inputs["callback"]:
                payload["callback"] = inputs["callback"]

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/sources",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            source_id = response.get("data", {}).get("id")
            message = response.get("data", {}).get("message", "Source ingestion started")

            return ActionResult(
                data={
                    "source_id": source_id,
                    "message": message,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"source_id": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("list_sources")
class ListSourcesAction(ActionHandler):
    """List all ingested sources."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/sources",
                method="GET",
                headers=get_headers(context)
            )

            sources = response.get("data", [])
            if not isinstance(sources, list):
                sources = [sources] if sources else []

            return ActionResult(
                data={
                    "sources": sources,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"sources": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_source")
class GetSourceAction(ActionHandler):
    """Get details of an ingested source."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            source_id = inputs["source_id"]

            response = await context.fetch(
                f"{INGEST_API_BASE}/{env}/sources/{source_id}",
                method="GET",
                headers=get_headers(context)
            )

            source = response.get("data", {})

            return ActionResult(
                data={
                    "source": source,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"source": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("delete_source")
class DeleteSourceAction(ActionHandler):
    """Delete an ingested source."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            source_id = inputs["source_id"]

            await context.fetch(
                f"{INGEST_API_BASE}/{env}/sources/{source_id}",
                method="DELETE",
                headers=get_headers(context)
            )

            return ActionResult(
                data={
                    "deleted": True,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deleted": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Create API: AI Generation Handlers ----

@shotstack.action("create_generated_asset")
class CreateGeneratedAssetAction(ActionHandler):
    """Generate an asset using AI."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)

            payload = {
                "provider": inputs["provider"],
                "options": inputs["options"]
            }

            response = await context.fetch(
                f"{CREATE_API_BASE}/{env}/assets",
                method="POST",
                headers=get_headers(context),
                json=payload
            )

            data = response.get("data", {})
            asset_id = data.get("id")
            status = data.get("status")

            return ActionResult(
                data={
                    "asset_id": asset_id,
                    "status": status,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"asset_id": None, "status": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@shotstack.action("get_generated_asset")
class GetGeneratedAssetAction(ActionHandler):
    """Get the status of an AI-generated asset."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            env = get_environment(context)
            asset_id = inputs["asset_id"]

            response = await context.fetch(
                f"{CREATE_API_BASE}/{env}/assets/{asset_id}",
                method="GET",
                headers=get_headers(context)
            )

            data = response.get("data", {})
            status = data.get("status")
            url = data.get("url")

            return ActionResult(
                data={
                    "asset": data,
                    "status": status,
                    "url": url,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"asset": {}, "status": None, "url": None, "result": False, "error": str(e)},
                cost_usd=0.0
            )
