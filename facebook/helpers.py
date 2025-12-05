"""
Facebook integration helper functions.

This module contains shared utility functions used across multiple action files.
"""

from autohive_integrations_sdk import ExecutionContext

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

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
