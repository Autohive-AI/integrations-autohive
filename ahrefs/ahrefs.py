from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any
from datetime import datetime

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


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format for API requests."""
    return datetime.now().strftime("%Y-%m-%d")


# ---- Domain Analysis Handlers ----

@ahrefs.action("get_domain_rating")
class GetDomainRatingAction(ActionHandler):
    """Get the Domain Rating (DR) and Ahrefs Rank for a target domain."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            date = inputs.get("date", get_today_date())

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/domain-rating",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "date": date
                }
            )

            domain_rating_data = response.get("domain_rating", {})

            return ActionResult(
                data={
                    "domain_rating": domain_rating_data.get("domain_rating", 0),
                    "ahrefs_rank": domain_rating_data.get("ahrefs_rank", 0),
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
            date = inputs.get("date", get_today_date())

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/backlinks-stats",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "date": date
                }
            )

            metrics = response.get("metrics", {})

            return ActionResult(
                data={
                    "live_backlinks": metrics.get("live", 0),
                    "all_time_backlinks": metrics.get("all_time", 0),
                    "live_refdomains": metrics.get("live_refdomains", 0),
                    "all_time_refdomains": metrics.get("all_time_refdomains", 0),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "live_backlinks": 0,
                    "all_time_backlinks": 0,
                    "live_refdomains": 0,
                    "all_time_refdomains": 0,
                    "result": False,
                    "error": str(e)
                },
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
            date = inputs.get("date", get_today_date())

            # Default select columns for backlinks
            select = "url_from,url_to,domain_rating_source,anchor,first_seen,is_dofollow"

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/all-backlinks",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "limit": limit,
                    "date": date,
                    "select": select
                }
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
            date = inputs.get("date", get_today_date())

            # Default select columns for referring domains
            select = "domain,domain_rating,backlinks,first_seen,last_visited"

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/refdomains",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "limit": limit,
                    "date": date,
                    "select": select
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
            date = inputs.get("date", get_today_date())

            # Default select columns for organic keywords
            select = "keyword,volume,best_position,keyword_difficulty,cpc,sum_traffic"

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/organic-keywords",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "country": country,
                    "limit": limit,
                    "date": date,
                    "select": select
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
            date = inputs.get("date", get_today_date())

            # Default select columns for top pages
            select = "url,sum_traffic,keywords,referring_domains"

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/top-pages",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "country": country,
                    "limit": limit,
                    "date": date,
                    "select": select
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


# ---- Outgoing Links Handlers ----

@ahrefs.action("get_outlinks_stats")
class GetOutlinksStatsAction(ActionHandler):
    """Get outgoing link statistics for a target domain."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            headers = get_headers(context)
            target = inputs["target"]
            mode = inputs.get("mode", "domain")
            date = inputs.get("date", get_today_date())

            response = await context.fetch(
                f"{AHREFS_API_BASE_URL}/site-explorer/outlinks-stats",
                method="GET",
                headers=headers,
                params={
                    "target": target,
                    "mode": mode,
                    "date": date
                }
            )

            metrics = response.get("metrics", {})

            return ActionResult(
                data={
                    "outgoing_links": metrics.get("outgoing_links", 0),
                    "outgoing_links_dofollow": metrics.get("outgoing_links_dofollow", 0),
                    "linked_domains": metrics.get("linked_domains", 0),
                    "linked_domains_dofollow": metrics.get("linked_domains_dofollow", 0),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "outgoing_links": 0,
                    "outgoing_links_dofollow": 0,
                    "linked_domains": 0,
                    "linked_domains_dofollow": 0,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )
