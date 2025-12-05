"""
Facebook integration helper functions.

This module contains utility functions for working with the Facebook Graph API,
including authentication helpers and response normalization.
"""

from autohive_integrations_sdk import ExecutionContext
from typing import Dict, Any

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


async def get_page_access_token(context: ExecutionContext, page_id: str) -> str:
    """
    Retrieve the Page Access Token for a specific page.
    
    Facebook requires Page Access Tokens (not User Access Tokens) for 
    page-specific operations. This helper fetches the token for the given page.
    
    Args:
        context: The execution context with authentication
        page_id: The Facebook Page ID
        
    Returns:
        The page access token string
        
    Raises:
        Exception: If the page is not found or user lacks permission
    """
    response = await context.fetch(
        f"{GRAPH_API_BASE}/me/accounts",
        method="GET",
        params={"fields": "id,access_token"}
    )
    
    pages = response.get("data", [])
    for page in pages:
        if page["id"] == page_id:
            return page["access_token"]
    
    raise Exception(
        f"Page '{page_id}' not found. Ensure you have admin access to this page."
    )


def build_post_response(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a post object from the Graph API into a consistent response format.
    
    Args:
        post: Raw post data from Facebook Graph API
        
    Returns:
        Normalized post dictionary with consistent field names
    """
    shares = post.get("shares", {})
    likes = post.get("likes", {}).get("summary", {})
    comments = post.get("comments", {}).get("summary", {})
    
    attachments = post.get("attachments", {}).get("data", [])
    media_type = "text"
    media_url = None
    
    if attachments:
        attachment = attachments[0]
        attach_type = attachment.get("type", "")
        if "photo" in attach_type:
            media_type = "photo"
            media_url = attachment.get("media", {}).get("image", {}).get("src")
        elif "video" in attach_type:
            media_type = "video"
            media_url = attachment.get("url")
        elif "share" in attach_type or attachment.get("url"):
            media_type = "link"
            media_url = attachment.get("url")
    
    return {
        "id": post.get("id", ""),
        "message": post.get("message", ""),
        "created_time": post.get("created_time", ""),
        "permalink_url": post.get("permalink_url", ""),
        "shares_count": shares.get("count", 0),
        "likes_count": likes.get("total_count", 0),
        "comments_count": comments.get("total_count", 0),
        "media_type": media_type,
        "media_url": media_url
    }


def build_comment_response(comment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a comment object from the Graph API into a consistent response format.
    
    Args:
        comment: Raw comment data from Facebook Graph API
        
    Returns:
        Normalized comment dictionary
    """
    from_data = comment.get("from", {})
    return {
        "id": comment.get("id", ""),
        "message": comment.get("message", ""),
        "from_name": from_data.get("name", ""),
        "from_id": from_data.get("id", ""),
        "created_time": comment.get("created_time", ""),
        "is_hidden": comment.get("is_hidden", False),
        "reply_count": comment.get("comment_count", 0)
    }
