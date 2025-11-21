from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import asyncio
import hashlib

# Create the integration using the config.json
mailchimp = Integration.load()


# ---- Rate Limiting ----

class MailchimpRateLimitException(Exception):
    """
    Exception raised when Mailchimp API rate limit is exceeded.
    Mailchimp allows max 10 simultaneous connections and returns 429 on rate limit.
    """
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(
            f"Mailchimp API rate limit exceeded. Retry after {retry_after} seconds."
        )


class MailchimpRateLimiter:
    def __init__(self, default_retry_delay: int = 60, max_retries: int = 3):
        """
        Handles Mailchimp API rate limiting by retrying requests on 429 errors.
        Mailchimp has a limit of 10 simultaneous connections.
        """
        self.default_retry_delay = default_retry_delay
        self.max_retries = max_retries

    def _extract_retry_delay(self, error_response) -> int:
        """Extract retry delay from error response headers"""
        if hasattr(error_response, 'headers'):
            retry_after = error_response.headers.get('Retry-After')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        return self.default_retry_delay

    async def make_request(self, context: ExecutionContext, url: str, **kwargs) -> Any:
        """Make request to Mailchimp API with automatic retry on rate limit errors"""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await context.fetch(url, **kwargs)
                return response

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if it's a rate limit error (HTTP 429)
                if '429' in error_str or 'rate limit' in error_str or 'too many requests' in error_str:
                    # Don't retry on the last attempt
                    if attempt >= self.max_retries:
                        delay = self._extract_retry_delay(e)
                        raise MailchimpRateLimitException(delay)

                    # Get delay from response headers or use default
                    delay = self._extract_retry_delay(e)

                    # Wait and retry
                    await asyncio.sleep(delay)
                    continue

                # For non-rate-limit errors, fail immediately
                raise e

        # All retries exhausted, raise the last error
        raise last_error


# Global rate limiter instance
rate_limiter = MailchimpRateLimiter()


# ---- Helper Functions ----

def get_mailchimp_base_url(dc: str) -> str:
    """
    Build Mailchimp API base URL using data center from metadata.
    The dc (data center) must be fetched from the OAuth2 metadata endpoint.
    """
    return f"https://{dc}.api.mailchimp.com/3.0"


async def get_data_center(context: ExecutionContext) -> str:
    """
    Fetch the data center (dc) from Mailchimp OAuth2 metadata endpoint.
    This is critical for Mailchimp OAuth2 - the dc is dynamic and must be
    retrieved after token exchange.

    Returns the dc string (e.g., 'us19')
    """
    try:
        metadata = await context.fetch(
            "https://login.mailchimp.com/oauth2/metadata",
            method="GET"
        )

        if not metadata or 'dc' not in metadata:
            raise ValueError("Failed to retrieve data center from Mailchimp metadata")

        return metadata['dc']

    except Exception as e:
        raise Exception(f"Failed to get Mailchimp data center: {str(e)}")


def get_subscriber_hash(email: str) -> str:
    """
    Generate MD5 hash of lowercase email address.
    Required for Mailchimp member operations.
    """
    return hashlib.md5(email.lower().encode()).hexdigest()


# ---- Action Handlers ----


@mailchimp.action("get_lists")
class GetListsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Retrieve all mailing lists from Mailchimp account
        """
        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL with pagination parameters
            url = f"{base_url}/lists"
            params = {
                "count": inputs.get("count", 10),
                "offset": inputs.get("offset", 0)
            }

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET",
                params=params
            )

            return {
                "result": True,
                "lists": response.get("lists", []),
                "total_items": response.get("total_items", 0)
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds.",
                "lists": [],
                "total_items": 0
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e),
                "lists": [],
                "total_items": 0
            }


@mailchimp.action("get_list")
class GetListAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Get details of a specific mailing list
        """
        # Validate required inputs
        list_id = inputs.get("list_id")
        if not list_id:
            return {
                "result": False,
                "error": "list_id is required"
            }

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL
            url = f"{base_url}/lists/{list_id}"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET"
            )

            return {
                "result": True,
                "list": response
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("create_list")
class CreateListAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Create a new mailing list in Mailchimp
        """
        # Validate required inputs
        name = inputs.get("name")
        permission_reminder = inputs.get("permission_reminder")
        contact = inputs.get("contact")
        campaign_defaults = inputs.get("campaign_defaults")

        if not name:
            return {"result": False, "error": "name is required"}
        if not permission_reminder:
            return {"result": False, "error": "permission_reminder is required"}
        if not contact:
            return {"result": False, "error": "contact is required"}
        if not campaign_defaults:
            return {"result": False, "error": "campaign_defaults is required"}

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build list payload
            list_data = {
                "name": name,
                "permission_reminder": permission_reminder,
                "contact": contact,
                "campaign_defaults": campaign_defaults,
                "email_type_option": inputs.get("email_type_option", True)
            }

            # Build URL
            url = f"{base_url}/lists"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="POST",
                json=list_data
            )

            return {
                "result": True,
                "list": {
                    "id": response.get("id"),
                    "name": response.get("name")
                }
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("add_member")
class AddMemberAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Add a new member to a mailing list
        """
        # Validate required inputs
        list_id = inputs.get("list_id")
        email_address = inputs.get("email_address")
        status = inputs.get("status")

        if not list_id:
            return {"result": False, "error": "list_id is required"}
        if not email_address:
            return {"result": False, "error": "email_address is required"}
        if not status:
            return {"result": False, "error": "status is required"}

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build member payload
            member_data = {
                "email_address": email_address,
                "status": status
            }

            # Add optional fields
            if inputs.get("merge_fields"):
                member_data["merge_fields"] = inputs["merge_fields"]

            if inputs.get("tags"):
                member_data["tags"] = inputs["tags"]

            # Build URL
            url = f"{base_url}/lists/{list_id}/members"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="POST",
                json=member_data
            )

            return {
                "result": True,
                "member": {
                    "id": response.get("id"),
                    "email_address": response.get("email_address"),
                    "status": response.get("status")
                }
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("update_member")
class UpdateMemberAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Update an existing member in a mailing list
        """
        # Validate required inputs
        list_id = inputs.get("list_id")
        if not list_id:
            return {"result": False, "error": "list_id is required"}

        # Get subscriber hash from either direct hash or email
        subscriber_hash = inputs.get("subscriber_hash")
        email_address = inputs.get("email_address")

        if not subscriber_hash and not email_address:
            return {
                "result": False,
                "error": "Either subscriber_hash or email_address is required"
            }

        if not subscriber_hash and email_address:
            subscriber_hash = get_subscriber_hash(email_address)

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build member update payload
            member_data = {}

            # Add optional fields only if provided
            if email_address:
                member_data["email_address"] = email_address
            if inputs.get("status"):
                member_data["status"] = inputs["status"]
            if inputs.get("merge_fields"):
                member_data["merge_fields"] = inputs["merge_fields"]
            if inputs.get("tags"):
                member_data["tags"] = inputs["tags"]

            # Build URL
            url = f"{base_url}/lists/{list_id}/members/{subscriber_hash}"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="PATCH",
                json=member_data
            )

            return {
                "result": True,
                "member": {
                    "id": response.get("id"),
                    "email_address": response.get("email_address"),
                    "status": response.get("status")
                }
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("get_member")
class GetMemberAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Get details of a specific member in a mailing list
        """
        # Validate required inputs
        list_id = inputs.get("list_id")
        if not list_id:
            return {"result": False, "error": "list_id is required"}

        # Get subscriber hash from either direct hash or email
        subscriber_hash = inputs.get("subscriber_hash")
        email_address = inputs.get("email_address")

        if not subscriber_hash and not email_address:
            return {
                "result": False,
                "error": "Either subscriber_hash or email_address is required"
            }

        if not subscriber_hash and email_address:
            subscriber_hash = get_subscriber_hash(email_address)

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL
            url = f"{base_url}/lists/{list_id}/members/{subscriber_hash}"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET"
            )

            return {
                "result": True,
                "member": {
                    "id": response.get("id"),
                    "email_address": response.get("email_address"),
                    "status": response.get("status"),
                    "merge_fields": response.get("merge_fields", {})
                }
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("get_list_members")
class GetListMembersAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Get all members from a mailing list
        """
        # Validate required inputs
        list_id = inputs.get("list_id")
        if not list_id:
            return {
                "result": False,
                "error": "list_id is required",
                "members": [],
                "total_items": 0
            }

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL with pagination and filter parameters
            url = f"{base_url}/lists/{list_id}/members"
            params = {
                "count": inputs.get("count", 10),
                "offset": inputs.get("offset", 0)
            }

            # Add optional status filter
            if inputs.get("status"):
                params["status"] = inputs["status"]

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET",
                params=params
            )

            return {
                "result": True,
                "members": response.get("members", []),
                "total_items": response.get("total_items", 0)
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds.",
                "members": [],
                "total_items": 0
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e),
                "members": [],
                "total_items": 0
            }


@mailchimp.action("get_campaigns")
class GetCampaignsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Retrieve all campaigns from Mailchimp account
        """
        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL with pagination and filter parameters
            url = f"{base_url}/campaigns"
            params = {
                "count": inputs.get("count", 10),
                "offset": inputs.get("offset", 0)
            }

            # Add optional status filter
            if inputs.get("status"):
                params["status"] = inputs["status"]

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET",
                params=params
            )

            return {
                "result": True,
                "campaigns": response.get("campaigns", []),
                "total_items": response.get("total_items", 0)
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds.",
                "campaigns": [],
                "total_items": 0
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e),
                "campaigns": [],
                "total_items": 0
            }


@mailchimp.action("create_campaign")
class CreateCampaignAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Create a new email campaign in Mailchimp
        """
        # Validate required inputs
        campaign_type = inputs.get("type")
        list_id = inputs.get("list_id")
        subject_line = inputs.get("subject_line")
        from_name = inputs.get("from_name")
        reply_to = inputs.get("reply_to")

        if not campaign_type:
            return {"result": False, "error": "type is required"}
        if not list_id:
            return {"result": False, "error": "list_id is required"}
        if not subject_line:
            return {"result": False, "error": "subject_line is required"}
        if not from_name:
            return {"result": False, "error": "from_name is required"}
        if not reply_to:
            return {"result": False, "error": "reply_to is required"}

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build campaign payload
            campaign_data = {
                "type": campaign_type,
                "recipients": {
                    "list_id": list_id
                },
                "settings": {
                    "subject_line": subject_line,
                    "from_name": from_name,
                    "reply_to": reply_to
                }
            }

            # Add optional title
            if inputs.get("title"):
                campaign_data["settings"]["title"] = inputs["title"]

            # Build URL
            url = f"{base_url}/campaigns"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="POST",
                json=campaign_data
            )

            return {
                "result": True,
                "campaign": {
                    "id": response.get("id"),
                    "type": response.get("type"),
                    "status": response.get("status")
                }
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }


@mailchimp.action("get_campaign")
class GetCampaignAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Get details of a specific campaign
        """
        # Validate required inputs
        campaign_id = inputs.get("campaign_id")
        if not campaign_id:
            return {
                "result": False,
                "error": "campaign_id is required"
            }

        try:
            # Get data center from metadata
            dc = await get_data_center(context)
            base_url = get_mailchimp_base_url(dc)

            # Build URL
            url = f"{base_url}/campaigns/{campaign_id}"

            # Make rate-limited request
            response = await rate_limiter.make_request(
                context,
                url,
                method="GET"
            )

            return {
                "result": True,
                "campaign": response
            }

        except MailchimpRateLimitException as e:
            return {
                "result": False,
                "error": f"Rate limit exceeded. Retry after {e.retry_after} seconds."
            }
        except Exception as e:
            return {
                "result": False,
                "error": str(e)
            }
