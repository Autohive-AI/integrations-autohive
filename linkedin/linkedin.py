from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler
from typing import Dict, Any

linkedin = Integration.load()


@linkedin.action("get_user_info")
class UserInfoActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        url = "https://api.linkedin.com/v2/userinfo"

        headers = {
            "LinkedIn-Version": "202510",
            "Content-Type": "application/json"
        }

        response = await context.fetch(url, method="GET", headers=headers)

        if isinstance(response, dict) and not response.get("error"):
            return {
                "result": "User information retrieved successfully",
                "user_info": response
            }
        else:
            error_details = response.get("error", {}) if isinstance(response, dict) else "Unknown error"
            return {
                "result": "Failed to retrieve user information",
                "details": error_details
            }


@linkedin.action("share_content")
class ShareContentActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        content = inputs.get("content")
        author_id = inputs.get("author_id")

        author_urn = f"urn:li:person:{author_id}" if author_id else None

        if not author_id:
            try:
                user_info_url = "https://api.linkedin.com/v2/userinfo"
                user_response = await context.fetch(user_info_url, method="GET", headers={
                    "LinkedIn-Version": "202510",
                    "Content-Type": "application/json"
                })

                if isinstance(user_response, dict) and user_response.get("sub"):
                    author_id = user_response.get("sub")
                    author_urn = f"urn:li:person:{author_id}"
                else:
                    return {
                        "result": "Failed to share content. Could not determine current user.",
                        "details": "Please provide an author_id or ensure proper authentication."
                    }
            except Exception as e:
                return {
                    "result": "Failed to share content. Error determining author.",
                    "details": str(e)
                }

        posts_url = "https://api.linkedin.com/rest/posts"

        payload = {
            "author": author_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        headers = {
            "LinkedIn-Version": "202510",
            "Content-Type": "application/json"
        }

        try:
            response = await context.fetch(posts_url, method="POST", json=payload, headers=headers)

            # context.fetch returns data directly on success, not a response object
            # For LinkedIn Posts API, successful creation returns the post data
            return {
                "result": "Content shared successfully.",
                "post_data": response
            }
        except Exception as e:
            # Handle any errors during the post creation
            error_message = str(e)
            if hasattr(e, 'response_data'):
                return {
                    "result": f"Failed to share content: {error_message}",
                    "details": e.response_data
                }
            else:
                return {
                    "result": f"Failed to share content: {error_message}"
                }