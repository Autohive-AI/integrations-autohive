from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any

# Create the integration
ahrefs = Integration.load()

# Base URL for Ahrefs API v3
AHREFS_API_BASE_URL = "https://api.ahrefs.com/v3"


def get_headers(context: ExecutionContext) -> Dict[str, str]:
    """Get authorization headers for Ahrefs API requests."""
    api_key = context.auth.get("api_key", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


# ---- Domain Analysis Handlers ----

@ahrefs.action("get_domain_rating")
class GetDomainRatingAction(ActionHandler):
    """Get the Domain Rating (DR) and Ahrefs Rank for a target domain."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/domain-rating",
                method="GET",
                headers=headers,
                params={"target": target}
            )

            return ActionResult(
                data={
                    "domain_rating": response.get("domain_rating", 0),
                    "ahrefs_rank": response.get("ahrefs_rank", 0),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "domain_rating": 0,
                    "ahrefs_rank": 0,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


# ---- Backlinks Handlers ----

@ahrefs.action("get_backlinks_stats")
class GetBacklinksStatsAction(ActionHandler):
    """Get backlink statistics for a target domain."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            mode = inputs.get("mode", "domain")

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/backlinks-stats",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode
                }
            )

            return ActionResult(
                data={"stats": response, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"stats": {}, "result": False, "error": str(e)},
                cost_usd=0.0
            )


@ahrefs.action("get_backlinks")
class GetBacklinksAction(ActionHandler):
    """Get a list of backlinks pointing to a target domain or URL."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            mode = inputs.get("mode", "domain")
            limit = inputs.get("limit", 100)
            order_by = inputs.get("order_by")

            params = {
                "target": target,
                "mode": mode,
                "limit": limit
            }

            if order_by:
                params["order_by"] = order_by

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/backlinks",
                method="GET",
                headers=headers,
                params=params
            )

            backlinks = response.get("backlinks", [])

            return ActionResult(
                data={"backlinks": backlinks, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"backlinks": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@ahrefs.action("get_referring_domains")
class GetReferringDomainsAction(ActionHandler):
    """Get a list of domains that link to the target."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            mode = inputs.get("mode", "domain")
            limit = inputs.get("limit", 100)

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/refdomains",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "limit": limit
                }
            )

            refdomains = response.get("refdomains", [])

            return ActionResult(
                data={"referring_domains": refdomains, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"referring_domains": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Organic Search Handlers ----

@ahrefs.action("get_organic_keywords")
class GetOrganicKeywordsAction(ActionHandler):
    """Get organic keywords that a domain ranks for in search results."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            country = inputs.get("country", "us")
            limit = inputs.get("limit", 100)

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/organic-keywords",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "country": country,
                    "limit": limit
                }
            )

            keywords = response.get("keywords", [])

            return ActionResult(
                data={"keywords": keywords, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"keywords": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


@ahrefs.action("get_top_pages")
class GetTopPagesAction(ActionHandler):
    """Get the top pages of a domain by organic traffic."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            country = inputs.get("country", "us")
            limit = inputs.get("limit", 100)

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/top-pages",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "country": country,
                    "limit": limit
                }
            )

            pages = response.get("pages", [])

            return ActionResult(
                data={"pages": pages, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"pages": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Keywords Explorer Handlers ----

@ahrefs.action("get_keyword_metrics")
class GetKeywordMetricsAction(ActionHandler):
    """Get search metrics for specific keywords."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            keywords = inputs["keywords"]
            country = inputs.get("country", "us")

            # Limit to 10 keywords max
            keywords = keywords[:10] if len(keywords) > 10 else keywords

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/keywords-explorer/metrics",
                method="POST",
                headers=headers,
                json={
                    "keywords": keywords,
                    "country": country
                }
            )

            metrics = response.get("metrics", [])

            return ActionResult(
                data={"metrics": metrics, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"metrics": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )


# ---- Outgoing Links Handlers ----

@ahrefs.action("get_outgoing_links")
class GetOutgoingLinksAction(ActionHandler):
    """Get external links from a target domain or page."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            mode = inputs.get("mode", "domain")
            limit = inputs.get("limit", 100)

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/outlinks",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "limit": limit
                }
            )

            outlinks = response.get("outlinks", [])

            return ActionResult(
                data={"outgoing_links": outlinks, "result": True},
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={"outgoing_links": [], "result": False, "error": str(e)},
                cost_usd=0.0
            )
