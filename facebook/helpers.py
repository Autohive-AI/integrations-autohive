"""
Facebook integration helper functions.

This module contains utility functions for working with the Facebook Graph API,
including authentication helpers and response normalization.
"""

from autohive_integrations_sdk import ExecutionContext
from typing import Dict, Any, Union
from datetime import datetime, timezone
import time

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

MIN_SCHEDULE_MINUTES = 10
MAX_SCHEDULE_DAYS = 75


def extract_page_id(compound_id: str) -> str:
    """
    Extract the page ID from a compound ID (e.g., post_id or comment_id).
    
    Facebook compound IDs are formatted as "PAGEID_ITEMID". This function
    extracts the page ID portion. If no underscore is present, returns
    the original ID (assumes it's already a page ID).
    
    Args:
        compound_id: A Facebook ID that may be compound (PAGEID_ITEMID) or simple
        
    Returns:
        The page ID portion of the compound ID
    """
    if "_" in compound_id:
        return compound_id.split("_")[0]
    return compound_id


def parse_scheduled_time(scheduled_time: Union[str, int]) -> int:
    """
    Parse and validate a scheduled time value.
    
    Accepts either:
    - Unix timestamp (int or string of digits)
    - ISO 8601 datetime string (e.g., "2024-12-25T10:00:00Z")
    
    Validates that the time is between 10 minutes and 75 days from now.
    
    Args:
        scheduled_time: The scheduled time as Unix timestamp or ISO 8601 string
        
    Returns:
        Unix timestamp as integer (seconds since epoch)
        
    Raises:
        ValueError: If the format is invalid or time is outside allowed window
    """
    now = int(time.time())
    min_time = now + (MIN_SCHEDULE_MINUTES * 60)
    max_time = now + (MAX_SCHEDULE_DAYS * 24 * 60 * 60)
    
    timestamp: int
    
    if isinstance(scheduled_time, int):
        timestamp = scheduled_time
    elif isinstance(scheduled_time, str):
        if scheduled_time.isdigit():
            timestamp = int(scheduled_time)
        else:
            try:
                dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                timestamp = int(dt.timestamp())
            except ValueError:
                raise ValueError(
                    f"Invalid scheduled_time format: '{scheduled_time}'. "
                    "Use Unix timestamp or ISO 8601 format (e.g., 2024-12-25T10:00:00Z)"
                )
    else:
        raise ValueError(
            f"scheduled_time must be a string or integer, got {type(scheduled_time).__name__}"
        )
    
    if timestamp < min_time:
        raise ValueError(
            f"scheduled_time must be at least {MIN_SCHEDULE_MINUTES} minutes in the future"
        )
    
    if timestamp > max_time:
        raise ValueError(
            f"scheduled_time must be within {MAX_SCHEDULE_DAYS} days from now"
        )
    
    return timestamp


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
        params={"fields": "id,access_token", "limit": 1000}
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
            media_url = (
                attachment.get("media", {}).get("source")
                or attachment.get("url")
            )
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
