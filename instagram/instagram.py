from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional

# Create the integration using the config.json
instagram = Integration.load()

# ---- Action Handlers ----

@instagram.action("get_recent_posts")
class GetRecentPostsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        limit = inputs.get("limit", 10)
        
        try:
            # First, get the Instagram Business Account ID
            # We need to get pages first, then find the Instagram account
            pages_response = await context.fetch(
                "https://graph.facebook.com/v18.0/me/accounts",
                method="GET",
                params={"access_token": context.auth.get("access_token")}
            )
            
            if not pages_response.get("data"):
                return {"posts": []}
            
            page_id = pages_response["data"][0]["id"]
            page_access_token = pages_response["data"][0]["access_token"]
            
            # Get Instagram Business Account connected to this page
            ig_account_response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{page_id}",
                method="GET",
                params={
                    "fields": "instagram_business_account",
                    "access_token": page_access_token
                }
            )
            
            if not ig_account_response.get("instagram_business_account"):
                return {"posts": []}
            
            ig_account_id = ig_account_response["instagram_business_account"]["id"]
            
            # Get recent media from Instagram Business Account
            media_response = await context.fetch(
                f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
                method="GET",
                params={
                    "fields": "id,media_type,media_url,caption,timestamp,permalink",
                    "limit": limit,
                    "access_token": page_access_token
                }
            )
            
            posts = []
            if media_response.get("data"):
                for post in media_response["data"]:
                    posts.append({
                        "id": post.get("id", ""),
                        "media_type": post.get("media_type", ""),
                        "media_url": post.get("media_url", ""),
                        "caption": post.get("caption", ""),
                        "timestamp": post.get("timestamp", ""),
                        "permalink": post.get("permalink", "")
                    })
            
            return {"posts": posts}
            
        except Exception as e:
            # Log error and return empty result
            print(f"Error fetching Instagram posts: {str(e)}")
            return {"posts": []}
