from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler
from typing import Dict, Any, List, Optional

tripadvisor = Integration.load()


def get_tripadvisor_api(context: ExecutionContext) -> 'TripAdvisorAPI':
    """Get TripAdvisorAPI instance with credentials from context"""
    if not hasattr(context, 'auth') or not context.auth:
        raise ValueError("No authentication credentials provided in context")

    credentials = context.auth.get("credentials", {})
    api_key = credentials.get("api_key")

    if not api_key:
        raise ValueError("Missing required api_key in credentials")

    return TripAdvisorAPI(api_key)


class TripAdvisorAPI:
    """Helper class for TripAdvisor Content API operations"""
    BASE_URL = "https://api.content.tripadvisor.com/api/v1"

    def __init__(self, api_key: str):
        """Initialize with API key from context"""
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for TripAdvisor API requests"""
        return {
            "accept": "application/json"
        }

    def _get_params(self, language: str = "en", **kwargs) -> Dict[str, Any]:
        """Get common parameters including API key"""
        params = {
            "key": self.api_key,
            "language": language
        }
        params.update(kwargs)
        return params


@tripadvisor.action("search_locations")
class SearchLocations(ActionHandler):
    """
    Search for hotels, restaurants, or attractions on TripAdvisor
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api = get_tripadvisor_api(context)

        search_query = inputs.get("search_query")
        category = inputs.get("category", "hotels")
        language = inputs.get("language", "en")

        url = f"{api.BASE_URL}/location/search"

        params = api._get_params(
            language=language,
            searchQuery=search_query,
            category=category
        )

        try:
            response = await context.fetch(
                url,
                params=params,
                headers=api._get_headers()
            )
            return response
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to search locations"
            }


@tripadvisor.action("get_location_details")
class GetLocationDetails(ActionHandler):
    """
    Get detailed information about a specific TripAdvisor location
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api = get_tripadvisor_api(context)

        location_id = inputs.get("location_id")
        language = inputs.get("language", "en")
        currency = inputs.get("currency", "USD")

        url = f"{api.BASE_URL}/location/{location_id}/details"

        params = api._get_params(
            language=language,
            currency=currency
        )

        try:
            response = await context.fetch(
                url,
                params=params,
                headers=api._get_headers()
            )
            return response
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to get details for location {location_id}"
            }


@tripadvisor.action("get_location_reviews")
class GetLocationReviews(ActionHandler):
    """
    Get reviews for a specific TripAdvisor location (up to 5 most recent reviews)
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api = get_tripadvisor_api(context)

        location_id = inputs.get("location_id")
        language = inputs.get("language", "en")

        url = f"{api.BASE_URL}/location/{location_id}/reviews"

        params = api._get_params(language=language)

        try:
            response = await context.fetch(
                url,
                params=params,
                headers=api._get_headers()
            )
            return response
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to get reviews for location {location_id}"
            }


@tripadvisor.action("get_location_photos")
class GetLocationPhotos(ActionHandler):
    """
    Get photos for a specific TripAdvisor location (up to 5 most recent photos)
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api = get_tripadvisor_api(context)

        location_id = inputs.get("location_id")
        language = inputs.get("language", "en")

        url = f"{api.BASE_URL}/location/{location_id}/photos"

        params = api._get_params(language=language)

        try:
            response = await context.fetch(
                url,
                params=params,
                headers=api._get_headers()
            )
            return response
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to get photos for location {location_id}"
            }


@tripadvisor.action("search_nearby_locations")
class SearchNearbyLocations(ActionHandler):
    """
    Search for locations near specified coordinates (latitude/longitude)
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api = get_tripadvisor_api(context)

        latitude = inputs.get("latitude")
        longitude = inputs.get("longitude")
        category = inputs.get("category", "hotels")
        radius = inputs.get("radius", 5)
        radius_unit = inputs.get("radius_unit", "km")
        language = inputs.get("language", "en")

        url = f"{api.BASE_URL}/location/nearby_search"

        params = api._get_params(
            language=language,
            latLong=f"{latitude},{longitude}",
            category=category,
            radius=radius,
            radiusUnit=radius_unit
        )

        try:
            response = await context.fetch(
                url,
                params=params,
                headers=api._get_headers()
            )
            return response
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to search nearby locations"
            }


if __name__ == "__main__":
    tripadvisor.run()
