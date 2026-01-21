"""
LinkedIn Integration for Autohive

This module provides LinkedIn integration including:
- User profile information retrieval
- Content sharing/posting to LinkedIn

All actions use the LinkedIn API v2.
"""

from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler, ActionResult
from typing import Dict, Any
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
linkedin = Integration.load(config_path)


@linkedin.action("get_user_info")
class UserInfoActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve user profile information via OpenID Connect userinfo endpoint."""
        url = "https://api.linkedin.com/v2/userinfo"

        response = await context.fetch(url, method="GET")

        if isinstance(response, dict) and response.get("sub"):
            return ActionResult(data={
                "result": "User information retrieved successfully",
                "user_info": response
            })
        else:
            error_details = response.get("error", "Unknown error") if isinstance(response, dict) else "Unknown error"
            return ActionResult(data={
                "result": "Failed to retrieve user information",
                "user_info": None,
                "details": error_details
            })


@linkedin.action("share_content")
class ShareContentActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        content = inputs.get("content")
        author_id = inputs.get("author_id")
        visibility = inputs.get("visibility", "PUBLIC")

        author_urn = f"urn:li:person:{author_id}" if author_id else None

        # If no author_id provided, fetch from userinfo endpoint
        if not author_id:
            try:
                user_info_url = "https://api.linkedin.com/v2/userinfo"
                user_response = await context.fetch(user_info_url, method="GET")

                if isinstance(user_response, dict) and user_response.get("sub"):
                    author_id = user_response.get("sub")
                    author_urn = f"urn:li:person:{author_id}"
                else:
                    return ActionResult(data={
                        "result": "Failed to share content. Could not determine current user.",
                        "post_id": None,
                        "post_data": None,
                        "details": "Please provide an author_id or ensure proper authentication."
                    })
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to share content. Error determining author.",
                    "post_id": None,
                    "post_data": None,
                    "details": str(e)
                })

        posts_url = "https://api.linkedin.com/rest/posts"

        payload = {
            "author": author_urn,
            "commentary": content,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        headers = {
            "LinkedIn-Version": "202501",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        try:
            response = await context.fetch(posts_url, method="POST", json=payload, headers=headers)

            # Extract post ID from response
            post_id = response.get("id") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Content shared successfully.",
                "post_id": post_id,
                "post_data": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to share content: {error_message}",
                "post_id": None,
                "post_data": None,
                "details": error_details
            })