"""
Facebook Posts actions - Create, retrieve, and delete posts.
"""

from autohive_integrations_sdk import ActionHandler, ActionResult, ExecutionContext
from typing import Dict, Any

try:
    from ..facebook import facebook
    from ..helpers import GRAPH_API_BASE, get_page_access_token, build_post_response
except ImportError:
    from facebook import facebook
    from helpers import GRAPH_API_BASE, get_page_access_token, build_post_response


@facebook.action("get_posts")
class GetPostsAction(ActionHandler):
    """
    Retrieve posts from a Facebook Page.
    
    Can fetch a single post by ID or list recent posts. Includes engagement
    metrics (likes, comments, shares) and media information.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        page_id = inputs["page_id"]
        post_id = inputs.get("post_id")
        limit = min(inputs.get("limit", 25), 100)
        
        page_token = await get_page_access_token(context, page_id)
        
        fields = (
            "id,message,created_time,permalink_url,"
            "shares,likes.summary(true),comments.summary(true),"
            "attachments{type,url,media}"
        )
        
        if post_id:
            response = await context.fetch(
                f"{GRAPH_API_BASE}/{post_id}",
                method="GET",
                params={"fields": fields, "access_token": page_token}
            )
            posts = [build_post_response(response)]
        else:
            response = await context.fetch(
                f"{GRAPH_API_BASE}/{page_id}/posts",
                method="GET",
                params={
                    "fields": fields,
                    "limit": limit,
                    "access_token": page_token
                }
            )
            posts = [build_post_response(p) for p in response.get("data", [])]
        
        return ActionResult(data={"posts": posts})


@facebook.action("create_post")
class CreatePostAction(ActionHandler):
    """
    Publish content to a Facebook Page.
    
    Supports multiple content types:
    - text: Simple text post
    - photo: Image post with caption
    - video: Video post with caption  
    - link: Link share with message
    
    Posts can be published immediately or scheduled for future publication.
    Scheduled posts must be between 10 minutes and 30 days from now.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        page_id = inputs["page_id"]
        message = inputs["message"]
        media_type = inputs.get("media_type", "text")
        media_url = inputs.get("media_url")
        scheduled_time = inputs.get("scheduled_time")
        
        page_token = await get_page_access_token(context, page_id)
        
        if media_type in ("photo", "video") and not media_url:
            raise Exception(f"media_url is required for {media_type} posts")
        
        if media_type == "link" and not media_url:
            raise Exception("media_url is required for link posts")
        
        is_scheduled = scheduled_time is not None
        
        if media_type == "photo":
            endpoint = f"{GRAPH_API_BASE}/{page_id}/photos"
            data = {
                "caption": message,
                "url": media_url,
                "access_token": page_token
            }
            if is_scheduled:
                data["published"] = "false"
                data["scheduled_publish_time"] = scheduled_time
                
        elif media_type == "video":
            endpoint = f"{GRAPH_API_BASE}/{page_id}/videos"
            data = {
                "description": message,
                "file_url": media_url,
                "access_token": page_token
            }
            if is_scheduled:
                data["published"] = "false"
                data["scheduled_publish_time"] = scheduled_time
                
        else:
            endpoint = f"{GRAPH_API_BASE}/{page_id}/feed"
            data = {
                "message": message,
                "access_token": page_token
            }
            if media_type == "link":
                data["link"] = media_url
            if is_scheduled:
                data["published"] = "false"
                data["scheduled_publish_time"] = scheduled_time
        
        response = await context.fetch(endpoint, method="POST", data=data)
        
        post_id = response.get("id") or response.get("post_id", "")
        
        result = {
            "post_id": post_id,
            "permalink_url": f"https://www.facebook.com/{post_id}",
            "is_scheduled": is_scheduled
        }
        
        if is_scheduled:
            result["scheduled_time"] = scheduled_time
            
        return ActionResult(data=result)


@facebook.action("delete_post")
class DeletePostAction(ActionHandler):
    """
    Permanently delete a post from a Facebook Page.
    
    This action cannot be undone. The post and all its comments, 
    likes, and shares will be permanently removed.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        page_id = inputs["page_id"]
        post_id = inputs["post_id"]
        
        page_token = await get_page_access_token(context, page_id)
        
        await context.fetch(
            f"{GRAPH_API_BASE}/{post_id}",
            method="DELETE",
            params={"access_token": page_token}
        )
        
        return ActionResult(data={
            "success": True,
            "deleted_post_id": post_id
        })
