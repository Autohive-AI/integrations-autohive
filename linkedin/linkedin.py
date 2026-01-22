"""
LinkedIn Integration for Autohive

This module provides comprehensive LinkedIn integration including:
- User profile information retrieval
- Content sharing/posting (text, articles, reshares)
- Post management (get, update, delete)
- Comments management (get, create, delete)
- Reactions management (get, create, delete)

All actions use the LinkedIn API with version 202601.
"""

from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler, ActionResult
from typing import Dict, Any
from urllib.parse import quote
import os

config_path = os.path.join(os.path.dirname(__file__), "config.json")
linkedin = Integration.load(config_path)

# LinkedIn API version - January 2026
LINKEDIN_VERSION = "202601"

# Common headers for LinkedIn REST API
def get_linkedin_headers():
    return {
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }


def encode_urn(urn: str) -> str:
    """URL-encode a LinkedIn URN for use in API paths."""
    return quote(urn, safe="")


async def get_current_user_urn(context: ExecutionContext) -> str:
    """Fetch the current authenticated user's URN."""
    user_info_url = "https://api.linkedin.com/v2/userinfo"
    user_response = await context.fetch(user_info_url, method="GET")

    if isinstance(user_response, dict) and user_response.get("sub"):
        return f"urn:li:person:{user_response.get('sub')}"
    raise ValueError("Could not determine current user. Please ensure proper authentication.")


# =============================================================================
# USER INFO ACTION
# =============================================================================

@linkedin.action("get_user_info")
class UserInfoActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve user profile information via OpenID Connect userinfo endpoint."""
        url = "https://api.linkedin.com/v2/userinfo"

        response = await context.fetch(url, method="GET")

        if isinstance(response, dict) and response.get("sub"):
            return ActionResult(data={
                "result": "User information retrieved successfully.",
                "user_info": response
            })
        else:
            error_details = response.get("error", "Unknown error") if isinstance(response, dict) else "Unknown error"
            return ActionResult(data={
                "result": "Failed to retrieve user information.",
                "user_info": None,
                "details": error_details
            })


# =============================================================================
# POST MANAGEMENT ACTIONS
# =============================================================================

@linkedin.action("share_content")
class ShareContentActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Share a text post on LinkedIn."""
        content = inputs.get("content")
        author_id = inputs.get("author_id")
        visibility = inputs.get("visibility", "PUBLIC")
        disable_reshare = inputs.get("disable_reshare", False)

        # Determine author URN
        if author_id:
            author_urn = f"urn:li:person:{author_id}"
        else:
            try:
                author_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to share content. Could not determine current user.",
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
            "isReshareDisabledByAuthor": disable_reshare
        }

        try:
            response = await context.fetch(
                posts_url,
                method="POST",
                json=payload,
                headers=get_linkedin_headers()
            )

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


@linkedin.action("share_article")
class ShareArticleActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Share an article post on LinkedIn with URL, title, and description."""
        commentary = inputs.get("commentary", "")
        article_url = inputs.get("article_url")
        article_title = inputs.get("article_title")
        article_description = inputs.get("article_description", "")
        author_id = inputs.get("author_id")
        visibility = inputs.get("visibility", "PUBLIC")

        # Determine author URN
        if author_id:
            author_urn = f"urn:li:person:{author_id}"
        else:
            try:
                author_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to share article. Could not determine current user.",
                    "post_id": None,
                    "post_data": None,
                    "details": str(e)
                })

        posts_url = "https://api.linkedin.com/rest/posts"

        payload = {
            "author": author_urn,
            "commentary": commentary,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "content": {
                "article": {
                    "source": article_url,
                    "title": article_title,
                    "description": article_description
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        try:
            response = await context.fetch(
                posts_url,
                method="POST",
                json=payload,
                headers=get_linkedin_headers()
            )

            post_id = response.get("id") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Article shared successfully.",
                "post_id": post_id,
                "post_data": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to share article: {error_message}",
                "post_id": None,
                "post_data": None,
                "details": error_details
            })


@linkedin.action("reshare_post")
class ResharePostActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Reshare an existing LinkedIn post."""
        original_post_urn = inputs.get("original_post_urn")
        commentary = inputs.get("commentary", "")
        author_id = inputs.get("author_id")
        visibility = inputs.get("visibility", "PUBLIC")

        # Determine author URN
        if author_id:
            author_urn = f"urn:li:person:{author_id}"
        else:
            try:
                author_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to reshare post. Could not determine current user.",
                    "post_id": None,
                    "post_data": None,
                    "details": str(e)
                })

        posts_url = "https://api.linkedin.com/rest/posts"

        payload = {
            "author": author_urn,
            "commentary": commentary,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
            "reshareContext": {
                "parent": original_post_urn
            }
        }

        try:
            response = await context.fetch(
                posts_url,
                method="POST",
                json=payload,
                headers=get_linkedin_headers()
            )

            post_id = response.get("id") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Post reshared successfully.",
                "post_id": post_id,
                "post_data": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to reshare post: {error_message}",
                "post_id": None,
                "post_data": None,
                "details": error_details
            })


@linkedin.action("get_post")
class GetPostActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve a single post by its URN."""
        post_urn = inputs.get("post_urn")

        encoded_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/posts/{encoded_urn}"

        try:
            response = await context.fetch(
                url,
                method="GET",
                headers=get_linkedin_headers()
            )

            return ActionResult(data={
                "result": "Post retrieved successfully.",
                "post": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to retrieve post: {error_message}",
                "post": None,
                "details": error_details
            })


@linkedin.action("get_posts")
class GetPostsActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve posts by author."""
        author_id = inputs.get("author_id")
        count = inputs.get("count", 10)
        start = inputs.get("start", 0)
        sort_by = inputs.get("sort_by", "LAST_MODIFIED")

        # Determine author URN
        if author_id:
            author_urn = f"urn:li:person:{author_id}"
        else:
            try:
                author_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to get posts. Could not determine author.",
                    "posts": None,
                    "paging": None,
                    "details": str(e)
                })

        encoded_author = encode_urn(author_urn)
        url = f"https://api.linkedin.com/rest/posts?author={encoded_author}&q=author&count={count}&start={start}&sortBy={sort_by}"

        headers = get_linkedin_headers()
        headers["X-RestLi-Method"] = "FINDER"

        try:
            response = await context.fetch(
                url,
                method="GET",
                headers=headers
            )

            posts = response.get("elements", []) if isinstance(response, dict) else []
            paging = response.get("paging") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Posts retrieved successfully.",
                "posts": posts,
                "paging": paging
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to retrieve posts: {error_message}",
                "posts": None,
                "paging": None,
                "details": error_details
            })


@linkedin.action("update_post")
class UpdatePostActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Update an existing post's commentary."""
        post_urn = inputs.get("post_urn")
        commentary = inputs.get("commentary")

        encoded_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/posts/{encoded_urn}"

        payload = {
            "patch": {
                "$set": {
                    "commentary": commentary
                }
            }
        }

        headers = get_linkedin_headers()
        headers["X-RestLi-Method"] = "PARTIAL_UPDATE"

        try:
            await context.fetch(
                url,
                method="POST",
                json=payload,
                headers=headers
            )

            return ActionResult(data={
                "result": "Post updated successfully.",
                "post_urn": post_urn
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to update post: {error_message}",
                "post_urn": post_urn,
                "details": error_details
            })


@linkedin.action("delete_post")
class DeletePostActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Delete a post."""
        post_urn = inputs.get("post_urn")

        encoded_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/posts/{encoded_urn}"

        headers = get_linkedin_headers()
        headers["X-RestLi-Method"] = "DELETE"

        try:
            await context.fetch(
                url,
                method="DELETE",
                headers=headers
            )

            return ActionResult(data={
                "result": "Post deleted successfully.",
                "post_urn": post_urn
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to delete post: {error_message}",
                "post_urn": post_urn,
                "details": error_details
            })


# =============================================================================
# COMMENTS MANAGEMENT ACTIONS
# =============================================================================

@linkedin.action("get_comments")
class GetCommentsActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve comments on a post or share."""
        post_urn = inputs.get("post_urn")

        encoded_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/socialActions/{encoded_urn}/comments"

        try:
            response = await context.fetch(
                url,
                method="GET",
                headers=get_linkedin_headers()
            )

            comments = response.get("elements", []) if isinstance(response, dict) else []
            paging = response.get("paging") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Comments retrieved successfully.",
                "comments": comments,
                "paging": paging
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to retrieve comments: {error_message}",
                "comments": None,
                "paging": None,
                "details": error_details
            })


@linkedin.action("create_comment")
class CreateCommentActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Create a comment on a post."""
        post_urn = inputs.get("post_urn")
        message = inputs.get("message")
        author_id = inputs.get("author_id")

        # Determine author URN
        if author_id:
            actor_urn = f"urn:li:person:{author_id}"
        else:
            try:
                actor_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to create comment. Could not determine current user.",
                    "comment_id": None,
                    "comment": None,
                    "details": str(e)
                })

        encoded_post_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/socialActions/{encoded_post_urn}/comments"

        payload = {
            "actor": actor_urn,
            "object": post_urn,
            "message": {
                "text": message
            }
        }

        try:
            response = await context.fetch(
                url,
                method="POST",
                json=payload,
                headers=get_linkedin_headers()
            )

            comment_id = response.get("id") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Comment created successfully.",
                "comment_id": comment_id,
                "comment": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to create comment: {error_message}",
                "comment_id": None,
                "comment": None,
                "details": error_details
            })


@linkedin.action("delete_comment")
class DeleteCommentActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Delete a comment."""
        post_urn = inputs.get("post_urn")
        comment_id = inputs.get("comment_id")
        author_id = inputs.get("author_id")

        # Determine actor URN for the deletion
        if author_id:
            actor_urn = f"urn:li:person:{author_id}"
        else:
            try:
                actor_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to delete comment. Could not determine current user.",
                    "details": str(e)
                })

        encoded_post_urn = encode_urn(post_urn)
        encoded_actor = encode_urn(actor_urn)
        encoded_comment_id = quote(str(comment_id), safe="")
        url = f"https://api.linkedin.com/rest/socialActions/{encoded_post_urn}/comments/{encoded_comment_id}?actor={encoded_actor}"

        try:
            await context.fetch(
                url,
                method="DELETE",
                headers=get_linkedin_headers()
            )

            return ActionResult(data={
                "result": "Comment deleted successfully.",
                "comment_id": comment_id
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to delete comment: {error_message}",
                "comment_id": comment_id,
                "details": error_details
            })


# =============================================================================
# REACTIONS MANAGEMENT ACTIONS
# =============================================================================

@linkedin.action("get_reactions")
class GetReactionsActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Retrieve reactions on a post."""
        post_urn = inputs.get("post_urn")
        sort = inputs.get("sort", "REVERSE_CHRONOLOGICAL")

        encoded_urn = encode_urn(post_urn)
        url = f"https://api.linkedin.com/rest/reactions/(entity:{encoded_urn})?q=entity&sort=(value:{sort})"

        try:
            response = await context.fetch(
                url,
                method="GET",
                headers=get_linkedin_headers()
            )

            reactions = response.get("elements", []) if isinstance(response, dict) else []
            paging = response.get("paging") if isinstance(response, dict) else None

            return ActionResult(data={
                "result": "Reactions retrieved successfully.",
                "reactions": reactions,
                "paging": paging
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to retrieve reactions: {error_message}",
                "reactions": None,
                "paging": None,
                "details": error_details
            })


@linkedin.action("create_reaction")
class CreateReactionActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Add a reaction to a post or comment."""
        target_urn = inputs.get("target_urn")
        reaction_type = inputs.get("reaction_type", "LIKE")
        author_id = inputs.get("author_id")

        # Determine actor URN
        if author_id:
            actor_urn = f"urn:li:person:{author_id}"
        else:
            try:
                actor_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to create reaction. Could not determine current user.",
                    "reaction": None,
                    "details": str(e)
                })

        encoded_actor = encode_urn(actor_urn)
        url = f"https://api.linkedin.com/rest/reactions?actor={encoded_actor}"

        payload = {
            "root": target_urn,
            "reactionType": reaction_type
        }

        try:
            response = await context.fetch(
                url,
                method="POST",
                json=payload,
                headers=get_linkedin_headers()
            )

            return ActionResult(data={
                "result": "Reaction created successfully.",
                "reaction": response
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to create reaction: {error_message}",
                "reaction": None,
                "details": error_details
            })


@linkedin.action("delete_reaction")
class DeleteReactionActionHandler(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Remove a reaction from a post or comment."""
        target_urn = inputs.get("target_urn")
        author_id = inputs.get("author_id")

        # Determine actor URN
        if author_id:
            actor_urn = f"urn:li:person:{author_id}"
        else:
            try:
                actor_urn = await get_current_user_urn(context)
            except Exception as e:
                return ActionResult(data={
                    "result": "Failed to delete reaction. Could not determine current user.",
                    "details": str(e)
                })

        encoded_actor = encode_urn(actor_urn)
        encoded_target = encode_urn(target_urn)
        url = f"https://api.linkedin.com/rest/reactions/(actor:{encoded_actor},entity:{encoded_target})"

        try:
            await context.fetch(
                url,
                method="DELETE",
                headers=get_linkedin_headers()
            )

            return ActionResult(data={
                "result": "Reaction removed successfully.",
                "target_urn": target_urn
            })
        except Exception as e:
            error_message = str(e)
            error_details = getattr(e, 'response_data', str(e))
            return ActionResult(data={
                "result": f"Failed to remove reaction: {error_message}",
                "target_urn": target_urn,
                "details": error_details
            })
