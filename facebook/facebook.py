from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
facebook = Integration.load(config_path)

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


async def get_page_access_token(context: ExecutionContext, page_id: str) -> str:
    """
    Retrieve the Page Access Token for a specific page.
    
    When posting to a Facebook Page, we need to use the Page Access Token
    (not the User Access Token). This function fetches the user's pages
    and returns the access token for the specified page.
    """
    response = await context.fetch(
        f"{GRAPH_API_BASE}/me/accounts",
        method="GET",
        params={"fields": "id,name,access_token"}
    )
    
    pages = response.get("data", [])
    for page in pages:
        if page["id"] == page_id:
            return page["access_token"]
    
    raise Exception(f"Page with ID '{page_id}' not found or you don't have permission to manage it")


@facebook.action("list_pages")
class ListPagesAction(ActionHandler):
    """Get all Facebook Pages the authenticated user can manage."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            response = await context.fetch(
                f"{GRAPH_API_BASE}/me/accounts",
                method="GET",
                params={"fields": "id,name,category,access_token"}
            )
            
            pages = []
            for page in response.get("data", []):
                pages.append({
                    "id": page.get("id", ""),
                    "name": page.get("name", ""),
                    "category": page.get("category", ""),
                    "access_token": page.get("access_token", "")
                })
            
            return ActionResult(data={"pages": pages})
            
        except Exception as e:
            raise Exception(f"Failed to list Facebook Pages: {str(e)}")


@facebook.action("create_post")
class CreatePostAction(ActionHandler):
    """Publish a post immediately to a Facebook Page."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        page_id = inputs["page_id"]
        message = inputs["message"]
        link = inputs.get("link")
        
        try:
            page_access_token = await get_page_access_token(context, page_id)
            
            data = {
                "message": message,
                "access_token": page_access_token
            }
            
            if link:
                data["link"] = link
            
            response = await context.fetch(
                f"{GRAPH_API_BASE}/{page_id}/feed",
                method="POST",
                data=data
            )
            
            post_id = response.get("id", "")
            
            return ActionResult(data={
                "post_id": post_id,
                "success": True,
                "permalink": f"https://www.facebook.com/{post_id}"
            })
            
        except Exception as e:
            return ActionResult(data={
                "post_id": "",
                "success": False,
                "error": str(e)
            })


@facebook.action("schedule_post")
class SchedulePostAction(ActionHandler):
    """Schedule a post to be published at a future time on a Facebook Page."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        page_id = inputs["page_id"]
        message = inputs["message"]
        scheduled_time = inputs["scheduled_time"]
        link = inputs.get("link")
        
        try:
            page_access_token = await get_page_access_token(context, page_id)
            
            data = {
                "message": message,
                "published": "false",
                "scheduled_publish_time": scheduled_time,
                "access_token": page_access_token
            }
            
            if link:
                data["link"] = link
            
            response = await context.fetch(
                f"{GRAPH_API_BASE}/{page_id}/feed",
                method="POST",
                data=data
            )
            
            post_id = response.get("id", "")
            
            return ActionResult(data={
                "post_id": post_id,
                "success": True,
                "scheduled_publish_time": scheduled_time
            })
            
        except Exception as e:
            return ActionResult(data={
                "post_id": "",
                "success": False,
                "error": str(e)
            })
