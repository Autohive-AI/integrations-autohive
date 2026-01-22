from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any
import hashlib

# Create the integration
netlify = Integration.load()

# Base URL for Netlify API
NETLIFY_API_BASE_URL = "https://api.netlify.com/api/v1"


# ---- Helper Functions ----

def get_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """Get authorization headers from context."""
    credentials = context.auth.get("credentials", {})
    access_token = credentials.get("access_token")

    if not access_token:
        raise ValueError("Missing required access_token")

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


# ---- Site Handlers ----

@netlify.action("list_sites")
class ListSitesAction(ActionHandler):
    """List all sites for the authenticated user."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites",
                method="GET",
                headers=headers
            )

            sites = response if isinstance(response, list) else []

            return ActionResult(
                data={"sites": sites, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"sites": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("create_site")
class CreateSiteAction(ActionHandler):
    """Create a new site."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            name = inputs["name"]

            payload = {"name": name}

            if inputs.get("custom_domain"):
                payload["custom_domain"] = inputs["custom_domain"]

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites",
                method="POST",
                headers=headers,
                json=payload
            )

            return ActionResult(
                data={"site": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"site": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("get_site")
class GetSiteAction(ActionHandler):
    """Get details of a specific site."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            site_id = inputs["site_id"]

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites/{site_id}",
                method="GET",
                headers=headers
            )

            return ActionResult(
                data={"site": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"site": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("update_site")
class UpdateSiteAction(ActionHandler):
    """Update site settings."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            site_id = inputs["site_id"]

            payload = {}
            if inputs.get("name"):
                payload["name"] = inputs["name"]
            if inputs.get("custom_domain"):
                payload["custom_domain"] = inputs["custom_domain"]

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites/{site_id}",
                method="PATCH",
                headers=headers,
                json=payload
            )

            return ActionResult(
                data={"site": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"site": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("delete_site")
class DeleteSiteAction(ActionHandler):
    """Delete a site."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            site_id = inputs["site_id"]

            await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites/{site_id}",
                method="DELETE",
                headers=headers
            )

            return ActionResult(
                data={"deleted": True, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deleted": False, "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Deploy Handlers ----

@netlify.action("list_deploys")
class ListDeploysAction(ActionHandler):
    """List all deploys for a site."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            site_id = inputs["site_id"]

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites/{site_id}/deploys",
                method="GET",
                headers=headers
            )

            deploys = response if isinstance(response, list) else []

            return ActionResult(
                data={"deploys": deploys, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deploys": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("create_deploy")
class CreateDeployAction(ActionHandler):
    """Create a new deploy for a site with files."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            site_id = inputs["site_id"]
            files = inputs["files"]

            # Prepare files dictionary with SHA1 hashes
            files_dict = {}
            hash_to_content = {}

            for path, content in files.items():
                sha1 = hashlib.sha1(content.encode()).hexdigest()
                files_dict[path] = sha1
                hash_to_content[sha1] = content

            # Create deploy with file digests
            deploy = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/sites/{site_id}/deploys",
                method="POST",
                headers=headers,
                json={"files": files_dict}
            )

            # Upload required files
            required_hashes = deploy.get("required", [])
            deploy_id = deploy.get("id")

            for sha1_hash in required_hashes:
                if sha1_hash in hash_to_content:
                    file_content = hash_to_content[sha1_hash]

                    upload_headers = get_auth_headers(context)
                    upload_headers["Content-Type"] = "application/octet-stream"

                    await context.fetch(
                        f"{NETLIFY_API_BASE_URL}/deploys/{deploy_id}/files/{sha1_hash}",
                        method="PUT",
                        headers=upload_headers,
                        data=file_content.encode()
                    )

            # Get final deploy info
            final_deploy = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/deploys/{deploy_id}",
                method="GET",
                headers=headers
            )

            deploy_url = (
                final_deploy.get("deploy_ssl_url") or
                final_deploy.get("ssl_url") or
                final_deploy.get("url", "")
            )

            return ActionResult(
                data={
                    "deploy": final_deploy,
                    "deploy_url": deploy_url,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deploy": {}, "deploy_url": "", "result": False, "error": str(e)},
                cost_usd=0.0
            )


@netlify.action("get_deploy")
class GetDeployAction(ActionHandler):
    """Get details of a specific deploy."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_auth_headers(context)
            deploy_id = inputs["deploy_id"]

            response = await context.fetch(
                f"{NETLIFY_API_BASE_URL}/deploys/{deploy_id}",
                method="GET",
                headers=headers
            )

            return ActionResult(
                data={"deploy": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"deploy": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )
