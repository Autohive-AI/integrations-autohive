"""
LinkedIn Integration for Autohive

This module provides comprehensive LinkedIn management including:
- User profile information retrieval
- Text, image, article, video, and document posts
- Organization/company page posting
- Multi-image and poll posts
- Draft post creation and publishing
- Comment and reaction management
- Post retrieval and deletion

All actions use the LinkedIn Marketing API v202510.
"""

from autohive_integrations_sdk import (
    Integration,
    ExecutionContext,
    ActionHandler,
    ActionResult,
    ConnectedAccountHandler,
    ConnectedAccountInfo
)
from typing import Dict, Any, Optional, List
from urllib.parse import quote
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
linkedin = Integration.load(config_path)

LINKEDIN_API_BASE = "https://api.linkedin.com"
LINKEDIN_VERSION = "202510"


def get_rest_headers() -> Dict[str, str]:
    """Build headers for LinkedIn REST API (Marketing API) requests."""
    return {
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }


def get_oidc_headers() -> Dict[str, str]:
    """Build headers for LinkedIn OIDC/userinfo requests."""
    return {
        "Content-Type": "application/json"
    }


def encode_urn(urn: str) -> str:
    """URL-encode a URN for use in URL paths."""
    return quote(urn, safe="")


def normalize_person_urn(value: str) -> str:
    """Normalize a value to a person URN format."""
    if not value:
        raise ValueError("Person ID/URN cannot be empty")
    if value.startswith("urn:li:person:"):
        return value
    return f"urn:li:person:{value}"


def normalize_organization_urn(value: str) -> str:
    """Normalize a value to an organization URN format."""
    if not value:
        raise ValueError("Organization ID/URN cannot be empty")
    if value.startswith("urn:li:organization:"):
        return value
    return f"urn:li:organization:{value}"


class LinkedInAPIClient:
    """Client for interacting with the LinkedIn API."""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.base_url = LINKEDIN_API_BASE

    async def _make_rest_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the LinkedIn REST API."""
        url = f"{self.base_url}/{endpoint}"
        headers = get_rest_headers()

        try:
            if method == "GET":
                response = await self.context.fetch(url, method="GET", params=params, headers=headers)
            elif method == "POST":
                response = await self.context.fetch(url, method="POST", json=json_data, headers=headers)
            elif method == "DELETE":
                response = await self.context.fetch(url, method="DELETE", headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response is None:
                return {"success": True}
            return response if isinstance(response, dict) else {"success": True, "raw": response}
        except Exception as e:
            raise Exception(f"LinkedIn API error on {method} {endpoint}: {str(e)}")

    async def _make_oidc_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to LinkedIn OIDC endpoints (userinfo)."""
        url = f"{self.base_url}/{endpoint}"
        headers = get_oidc_headers()

        try:
            response = await self.context.fetch(url, method=method, params=params, headers=headers)
            return response if isinstance(response, dict) else {}
        except Exception as e:
            raise Exception(f"LinkedIn OIDC error on {method} {endpoint}: {str(e)}")

    async def get_current_user(self) -> Dict[str, Any]:
        """Get the current authenticated user's info via OIDC."""
        return await self._make_oidc_request("v2/userinfo")

    async def initialize_image_upload(self, owner_urn: str) -> Dict[str, Any]:
        """Initialize an image upload to get upload URL."""
        return await self._make_rest_request(
            "rest/images?action=initializeUpload",
            method="POST",
            json_data={"initializeUploadRequest": {"owner": owner_urn}}
        )

    async def upload_image_binary(self, upload_url: str, image_data: bytes) -> None:
        """Upload image binary to the provided URL."""
        await self.context.fetch(
            upload_url,
            method="PUT",
            headers={"Content-Type": "application/octet-stream"},
            data=image_data
        )

    async def initialize_video_upload(self, owner_urn: str, file_size: int) -> Dict[str, Any]:
        """Initialize a video upload."""
        return await self._make_rest_request(
            "rest/videos?action=initializeUpload",
            method="POST",
            json_data={
                "initializeUploadRequest": {
                    "owner": owner_urn,
                    "fileSizeBytes": file_size
                }
            }
        )

    async def finalize_video_upload(self, video_urn: str, upload_token: str, etags: List[str]) -> Dict[str, Any]:
        """Finalize a video upload after all parts are uploaded."""
        return await self._make_rest_request(
            "rest/videos?action=finalizeUpload",
            method="POST",
            json_data={
                "finalizeUploadRequest": {
                    "video": video_urn,
                    "uploadToken": upload_token,
                    "uploadedPartIds": etags
                }
            }
        )

    async def create_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a LinkedIn post."""
        return await self._make_rest_request("rest/posts", method="POST", json_data=payload)

    async def get_post(self, post_urn: str) -> Dict[str, Any]:
        """Get a specific post by URN."""
        encoded_urn = encode_urn(post_urn)
        return await self._make_rest_request(f"rest/posts/{encoded_urn}")

    async def delete_post(self, post_urn: str) -> Dict[str, Any]:
        """Delete a post."""
        encoded_urn = encode_urn(post_urn)
        return await self._make_rest_request(f"rest/posts/{encoded_urn}", method="DELETE")

    async def get_posts_by_author(
        self,
        author_urn: str,
        count: int = 10,
        start: int = 0
    ) -> Dict[str, Any]:
        """Get posts by author."""
        return await self._make_rest_request(
            "rest/posts",
            params={
                "author": author_urn,
                "q": "author",
                "count": count,
                "start": start
            }
        )

    async def create_comment(
        self,
        post_urn: str,
        actor_urn: str,
        message: str
    ) -> Dict[str, Any]:
        """Create a comment on a post."""
        encoded_urn = encode_urn(post_urn)
        return await self._make_rest_request(
            f"rest/socialActions/{encoded_urn}/comments",
            method="POST",
            json_data={
                "actor": actor_urn,
                "message": {"text": message}
            }
        )

    async def get_comments(
        self,
        post_urn: str,
        count: int = 10,
        start: int = 0
    ) -> Dict[str, Any]:
        """Get comments on a post."""
        encoded_urn = encode_urn(post_urn)
        return await self._make_rest_request(
            f"rest/socialActions/{encoded_urn}/comments",
            params={"count": count, "start": start}
        )

    async def add_reaction(
        self,
        post_urn: str,
        actor_urn: str,
        reaction_type: str
    ) -> Dict[str, Any]:
        """Add a reaction to a post."""
        return await self._make_rest_request(
            "rest/reactions",
            method="POST",
            json_data={
                "actor": actor_urn,
                "object": post_urn,
                "reactionType": reaction_type
            }
        )


@linkedin.connected_account()
class LinkedInConnectedAccountHandler(ConnectedAccountHandler):
    """Handler to fetch connected LinkedIn account information."""

    async def get_account_info(self, context: ExecutionContext) -> ConnectedAccountInfo:
        """Fetch LinkedIn user information for the connected account."""
        client = LinkedInAPIClient(context)
        user_data = await client.get_current_user()

        name = user_data.get("name", "")
        name_parts = name.split(maxsplit=1) if name else []

        return ConnectedAccountInfo(
            email=user_data.get("email"),
            username=name,
            first_name=name_parts[0] if len(name_parts) > 0 else None,
            last_name=name_parts[1] if len(name_parts) > 1 else None,
            avatar_url=user_data.get("picture"),
            user_id=user_data.get("sub")
        )


async def get_author_urn(context: ExecutionContext, author_id: Optional[str] = None) -> str:
    """Get author URN, fetching current user if not provided."""
    if author_id:
        return normalize_person_urn(author_id)

    client = LinkedInAPIClient(context)
    user_info = await client.get_current_user()
    user_id = user_info.get("sub")
    if not user_id:
        raise Exception("Could not determine current user ID from LinkedIn")
    return normalize_person_urn(user_id)


def build_base_post_payload(
    author_urn: str,
    commentary: str,
    visibility: str = "PUBLIC",
    lifecycle_state: str = "PUBLISHED"
) -> Dict[str, Any]:
    """Build the base post payload with minimal required fields."""
    return {
        "author": author_urn,
        "commentary": commentary,
        "visibility": visibility,
        "lifecycleState": lifecycle_state
    }


@linkedin.action("get_user_info")
class GetUserInfoAction(ActionHandler):
    """Retrieve profile information for the authenticated LinkedIn user."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            client = LinkedInAPIClient(context)
            user_info = await client.get_current_user()

            return ActionResult(
                data={
                    "result": True,
                    "user_id": user_info.get("sub"),
                    "name": user_info.get("name"),
                    "email": user_info.get("email"),
                    "picture": user_info.get("picture"),
                    "locale": user_info.get("locale")
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("share_content")
class ShareContentAction(ActionHandler):
    """Share text content on LinkedIn as a person."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content")
            if not content:
                raise Exception("Content is required")

            author_urn = await get_author_urn(context, inputs.get("author_id"))
            visibility = inputs.get("visibility", "PUBLIC")

            payload = build_base_post_payload(author_urn, content, visibility)

            client = LinkedInAPIClient(context)
            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", ""),
                    "post_data": response
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("share_image_post")
class ShareImagePostAction(ActionHandler):
    """Share a post with an image attachment on LinkedIn."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content", "")
            image_url = inputs.get("image_url")
            alt_text = inputs.get("alt_text", "")

            if not image_url:
                raise Exception("image_url is required")

            author_urn = await get_author_urn(context, inputs.get("author_id"))
            client = LinkedInAPIClient(context)

            init_response = await client.initialize_image_upload(author_urn)
            upload_url = init_response.get("value", {}).get("uploadUrl")
            image_urn = init_response.get("value", {}).get("image")

            if not upload_url or not image_urn:
                raise Exception("Failed to initialize image upload")

            image_response = await context.fetch(image_url, method="GET")
            if isinstance(image_response, bytes):
                image_data = image_response
            else:
                raise Exception("Failed to download image from URL")

            await client.upload_image_binary(upload_url, image_data)

            payload = build_base_post_payload(author_urn, content)
            payload["content"] = {
                "media": {
                    "id": image_urn,
                    "altText": alt_text
                }
            }

            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", ""),
                    "image_urn": image_urn
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("share_article_post")
class ShareArticlePostAction(ActionHandler):
    """Share an article/link with preview card on LinkedIn."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content", "")
            article_url = inputs.get("article_url")
            article_title = inputs.get("article_title")
            article_description = inputs.get("article_description", "")

            if not article_url or not article_title:
                raise Exception("article_url and article_title are required")

            author_urn = await get_author_urn(context, inputs.get("author_id"))

            payload = build_base_post_payload(author_urn, content)
            payload["content"] = {
                "article": {
                    "source": article_url,
                    "title": article_title,
                    "description": article_description
                }
            }

            client = LinkedInAPIClient(context)
            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", "")
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("share_organization_post")
class ShareOrganizationPostAction(ActionHandler):
    """Post on behalf of a LinkedIn Company Page."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content")
            organization_id = inputs.get("organization_id")

            if not content or not organization_id:
                raise Exception("content and organization_id are required")

            author_urn = normalize_organization_urn(organization_id)

            payload = build_base_post_payload(author_urn, content)

            client = LinkedInAPIClient(context)
            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", "")
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("create_poll_post")
class CreatePollPostAction(ActionHandler):
    """Create a poll post on LinkedIn."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content", "")
            options = inputs.get("options", [])
            duration = inputs.get("duration", "THREE_DAYS")

            if len(options) < 2 or len(options) > 4:
                raise Exception("Poll requires 2-4 options")

            author_urn = await get_author_urn(context, inputs.get("author_id"))

            poll_options = [{"text": opt} for opt in options]

            payload = build_base_post_payload(author_urn, content)
            payload["content"] = {
                "poll": {
                    "question": content,
                    "options": poll_options,
                    "settings": {
                        "duration": duration
                    }
                }
            }

            client = LinkedInAPIClient(context)
            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", "")
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("create_draft_post")
class CreateDraftPostAction(ActionHandler):
    """Create a post as draft for later publishing."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            content = inputs.get("content")
            if not content:
                raise Exception("Content is required")

            author_urn = await get_author_urn(context, inputs.get("author_id"))

            payload = build_base_post_payload(
                author_urn,
                content,
                lifecycle_state="DRAFT"
            )

            client = LinkedInAPIClient(context)
            response = await client.create_post(payload)

            return ActionResult(
                data={
                    "result": True,
                    "post_id": response.get("id", ""),
                    "status": "DRAFT"
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("get_post")
class GetPostAction(ActionHandler):
    """Retrieve a specific post by URN."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            post_urn = inputs.get("post_urn")
            if not post_urn:
                raise Exception("post_urn is required")

            client = LinkedInAPIClient(context)
            response = await client.get_post(post_urn)

            return ActionResult(
                data={
                    "result": True,
                    "post": response
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("get_member_posts")
class GetMemberPostsAction(ActionHandler):
    """Retrieve posts by the authenticated member or specified author."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            author_urn = await get_author_urn(context, inputs.get("author_id"))
            count = min(inputs.get("count", 10), 100)
            start = inputs.get("start", 0)

            client = LinkedInAPIClient(context)
            response = await client.get_posts_by_author(author_urn, count, start)

            posts = response.get("elements", [])

            return ActionResult(
                data={
                    "result": True,
                    "posts": posts,
                    "count": len(posts),
                    "start": start
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "posts": [],
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("delete_post")
class DeletePostAction(ActionHandler):
    """Delete a LinkedIn post."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            post_urn = inputs.get("post_urn")
            if not post_urn:
                raise Exception("post_urn is required")

            client = LinkedInAPIClient(context)
            await client.delete_post(post_urn)

            return ActionResult(
                data={
                    "result": True,
                    "deleted_post_urn": post_urn
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("create_comment")
class CreateCommentAction(ActionHandler):
    """Add a comment to a LinkedIn post."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            post_urn = inputs.get("post_urn")
            message = inputs.get("message")

            if not post_urn or not message:
                raise Exception("post_urn and message are required")

            author_urn = await get_author_urn(context, inputs.get("author_id"))

            client = LinkedInAPIClient(context)
            response = await client.create_comment(post_urn, author_urn, message)

            return ActionResult(
                data={
                    "result": True,
                    "comment_id": response.get("id", ""),
                    "comment": response
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("get_post_comments")
class GetPostCommentsAction(ActionHandler):
    """Retrieve comments on a LinkedIn post."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            post_urn = inputs.get("post_urn")
            if not post_urn:
                raise Exception("post_urn is required")

            count = min(inputs.get("count", 10), 100)
            start = inputs.get("start", 0)

            client = LinkedInAPIClient(context)
            response = await client.get_comments(post_urn, count, start)

            comments = response.get("elements", [])

            return ActionResult(
                data={
                    "result": True,
                    "comments": comments,
                    "count": len(comments)
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "comments": [],
                    "error": str(e)
                },
                cost_usd=0.0
            )


@linkedin.action("add_reaction")
class AddReactionAction(ActionHandler):
    """React to a LinkedIn post."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            post_urn = inputs.get("post_urn")
            reaction_type = inputs.get("reaction_type", "LIKE")

            if not post_urn:
                raise Exception("post_urn is required")

            valid_reactions = ["LIKE", "PRAISE", "APPRECIATION", "EMPATHY", "INTEREST", "ENTERTAINMENT"]
            if reaction_type not in valid_reactions:
                raise Exception(f"Invalid reaction_type. Must be one of: {valid_reactions}")

            author_urn = await get_author_urn(context, inputs.get("author_id"))

            client = LinkedInAPIClient(context)
            await client.add_reaction(post_urn, author_urn, reaction_type)

            return ActionResult(
                data={
                    "result": True,
                    "reaction_type": reaction_type,
                    "post_urn": post_urn
                },
                cost_usd=0.0
            )
        except Exception as e:
            return ActionResult(
                data={
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )
