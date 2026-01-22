from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler,
    ActionResult
)
from typing import Dict, Any, Optional, Tuple


uber = Integration.load()

UBER_API_BASE_URL = "https://api.uber.com"
API_VERSION = "v1.2"


# ---- Helper Functions ----

def get_common_headers() -> Dict[str, str]:
    """Return common headers for Uber API requests.
    Note: Auth headers are automatically added by the SDK when using OAuth.
    """
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Language": "en_US"
    }


def validate_coordinates(
    lat: Optional[float],
    lng: Optional[float],
    field_prefix: str = ""
) -> Optional[str]:
    """Validate latitude and longitude values.
    
    Returns error message if invalid, None if valid.
    """
    if lat is None or lng is None:
        return f"{field_prefix}latitude and longitude are required"
    
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return f"{field_prefix}latitude and longitude must be numbers"
    
    if lat < -90 or lat > 90:
        return f"{field_prefix}latitude must be between -90 and 90"
    
    if lng < -180 or lng > 180:
        return f"{field_prefix}longitude must be between -180 and 180"
    
    return None


def validate_seat_count(seat_count: Optional[int]) -> int:
    """Validate and normalize seat count for POOL products."""
    if seat_count is None:
        return 2
    if not isinstance(seat_count, int):
        return 2
    return max(1, min(seat_count, 2))


def validate_limit(limit: Optional[int], max_limit: int = 50) -> int:
    """Validate and normalize limit parameter."""
    if limit is None:
        return 10
    if not isinstance(limit, int):
        return 10
    return max(1, min(limit, max_limit))


def validate_offset(offset: Optional[int]) -> int:
    """Validate and normalize offset parameter."""
    if offset is None:
        return 0
    if not isinstance(offset, int):
        return 0
    return max(0, offset)


def validate_required_string(value: Any, field_name: str) -> Optional[str]:
    """Validate that a value is a non-empty string.
    
    Returns error message if invalid, None if valid.
    """
    if value is None:
        return f"{field_name} is required"
    if not isinstance(value, str) or not value.strip():
        return f"{field_name} must be a non-empty string"
    return None


def parse_uber_error(response: Any, default_message: str = "Unknown error") -> Dict[str, Any]:
    """Parse Uber API error response into a consistent format."""
    if isinstance(response, dict):
        return {
            "code": response.get("code", "unknown"),
            "message": response.get("message", default_message)
        }
    return {"code": "unknown", "message": default_message}


async def uber_fetch(
    context: ExecutionContext,
    path: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    """
    Centralized Uber API request handler.
    
    Returns:
        Tuple of (response_data, error_dict)
        - On success: (data, None)
        - On failure: (None, {"message": "...", "error_type": "..."})
    """
    try:
        url = f"{UBER_API_BASE_URL}/{API_VERSION}/{path.lstrip('/')}"
        
        kwargs: Dict[str, Any] = {
            "method": method,
            "headers": get_common_headers(),
        }
        
        if params:
            kwargs["params"] = params
        if json_body:
            kwargs["json"] = json_body
        
        response = await context.fetch(url, **kwargs)
        return response, None
        
    except Exception as e:
        error_str = str(e)
        
        error_type = "api_error"
        if "401" in error_str or "unauthorized" in error_str.lower():
            error_type = "auth_error"
        elif "429" in error_str or "rate" in error_str.lower():
            error_type = "rate_limited"
        elif "400" in error_str or "422" in error_str:
            error_type = "validation_error"
        elif "404" in error_str:
            error_type = "not_found"
        elif "5" in error_str[:3]:
            error_type = "server_error"
        
        return None, {
            "message": error_str,
            "error_type": error_type
        }


def success_result(data: Dict[str, Any]) -> ActionResult:
    """Create a successful ActionResult."""
    return ActionResult(
        data={**data, "result": True},
        cost_usd=0.0
    )


def error_result(
    error: str,
    error_type: str = "api_error",
    default_data: Optional[Dict[str, Any]] = None
) -> ActionResult:
    """Create an error ActionResult with consistent structure."""
    data = default_data or {}
    return ActionResult(
        data={
            **data,
            "result": False,
            "error": error,
            "error_type": error_type
        },
        cost_usd=0.0
    )


# ---- Product Action Handlers ----

@uber.action("get_products")
class GetProductsAction(ActionHandler):
    """Get available Uber products at a given location."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        coord_error = validate_coordinates(
            inputs.get("latitude"),
            inputs.get("longitude")
        )
        if coord_error:
            return error_result(coord_error, "validation_error", {"products": []})

        params = {
            "latitude": inputs["latitude"],
            "longitude": inputs["longitude"]
        }

        response, err = await uber_fetch(context, "products", params=params)
        
        if err:
            return error_result(err["message"], err["error_type"], {"products": []})

        return success_result({
            "products": response.get("products", [])
        })


# ---- Estimate Action Handlers ----

@uber.action("get_price_estimate")
class GetPriceEstimateAction(ActionHandler):
    """Get price estimates for a trip between two locations."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        start_error = validate_coordinates(
            inputs.get("start_latitude"),
            inputs.get("start_longitude"),
            "start_"
        )
        if start_error:
            return error_result(start_error, "validation_error", {"prices": []})

        end_error = validate_coordinates(
            inputs.get("end_latitude"),
            inputs.get("end_longitude"),
            "end_"
        )
        if end_error:
            return error_result(end_error, "validation_error", {"prices": []})

        params = {
            "start_latitude": inputs["start_latitude"],
            "start_longitude": inputs["start_longitude"],
            "end_latitude": inputs["end_latitude"],
            "end_longitude": inputs["end_longitude"]
        }

        if inputs.get("seat_count") is not None:
            params["seat_count"] = validate_seat_count(inputs["seat_count"])

        response, err = await uber_fetch(context, "estimates/price", params=params)
        
        if err:
            return error_result(err["message"], err["error_type"], {"prices": []})

        return success_result({
            "prices": response.get("prices", [])
        })


@uber.action("get_time_estimate")
class GetTimeEstimateAction(ActionHandler):
    """Get ETA estimates for available products at a location."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        coord_error = validate_coordinates(
            inputs.get("start_latitude"),
            inputs.get("start_longitude"),
            "start_"
        )
        if coord_error:
            return error_result(coord_error, "validation_error", {"times": []})

        params = {
            "start_latitude": inputs["start_latitude"],
            "start_longitude": inputs["start_longitude"]
        }

        product_id = inputs.get("product_id")
        if product_id and isinstance(product_id, str) and product_id.strip():
            params["product_id"] = product_id.strip()

        response, err = await uber_fetch(context, "estimates/time", params=params)
        
        if err:
            return error_result(err["message"], err["error_type"], {"times": []})

        return success_result({
            "times": response.get("times", [])
        })


@uber.action("get_ride_estimate")
class GetRideEstimateAction(ActionHandler):
    """Get a detailed fare estimate for a specific ride request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        product_error = validate_required_string(inputs.get("product_id"), "product_id")
        if product_error:
            return error_result(product_error, "validation_error", {"estimate": {}})

        start_error = validate_coordinates(
            inputs.get("start_latitude"),
            inputs.get("start_longitude"),
            "start_"
        )
        if start_error:
            return error_result(start_error, "validation_error", {"estimate": {}})

        end_error = validate_coordinates(
            inputs.get("end_latitude"),
            inputs.get("end_longitude"),
            "end_"
        )
        if end_error:
            return error_result(end_error, "validation_error", {"estimate": {}})

        body = {
            "product_id": inputs["product_id"].strip(),
            "start_latitude": inputs["start_latitude"],
            "start_longitude": inputs["start_longitude"],
            "end_latitude": inputs["end_latitude"],
            "end_longitude": inputs["end_longitude"]
        }

        if inputs.get("seat_count") is not None:
            body["seat_count"] = validate_seat_count(inputs["seat_count"])

        response, err = await uber_fetch(
            context, "requests/estimate", method="POST", json_body=body
        )
        
        if err:
            return error_result(err["message"], err["error_type"], {"estimate": {}})

        return success_result({"estimate": response})


# ---- Ride Request Action Handlers ----

@uber.action("request_ride")
class RequestRideAction(ActionHandler):
    """Request an Uber ride on behalf of the user."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        product_error = validate_required_string(inputs.get("product_id"), "product_id")
        if product_error:
            return error_result(product_error, "validation_error", {
                "request_id": None, "status": None
            })

        start_error = validate_coordinates(
            inputs.get("start_latitude"),
            inputs.get("start_longitude"),
            "start_"
        )
        if start_error:
            return error_result(start_error, "validation_error", {
                "request_id": None, "status": None
            })

        end_error = validate_coordinates(
            inputs.get("end_latitude"),
            inputs.get("end_longitude"),
            "end_"
        )
        if end_error:
            return error_result(end_error, "validation_error", {
                "request_id": None, "status": None
            })

        body: Dict[str, Any] = {
            "product_id": inputs["product_id"].strip(),
            "start_latitude": inputs["start_latitude"],
            "start_longitude": inputs["start_longitude"],
            "end_latitude": inputs["end_latitude"],
            "end_longitude": inputs["end_longitude"]
        }

        optional_string_fields = [
            "start_address", "start_nickname", "end_address", "end_nickname",
            "fare_id", "surge_confirmation_id", "payment_method_id"
        ]
        for field in optional_string_fields:
            value = inputs.get(field)
            if value and isinstance(value, str) and value.strip():
                body[field] = value.strip()

        if inputs.get("seat_count") is not None:
            body["seat_count"] = validate_seat_count(inputs["seat_count"])

        response, err = await uber_fetch(
            context, "requests", method="POST", json_body=body
        )
        
        if err:
            return error_result(err["message"], err["error_type"], {
                "request_id": None, "status": None
            })

        return success_result({
            "request_id": response.get("request_id"),
            "status": response.get("status"),
            "eta": response.get("eta"),
            "surge_multiplier": response.get("surge_multiplier"),
            "driver": response.get("driver"),
            "vehicle": response.get("vehicle")
        })


@uber.action("get_ride_status")
class GetRideStatusAction(ActionHandler):
    """Get the current status and details of an active ride request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        request_id_error = validate_required_string(inputs.get("request_id"), "request_id")
        if request_id_error:
            return error_result(request_id_error, "validation_error", {"ride": {}})

        request_id = inputs["request_id"].strip()
        
        response, err = await uber_fetch(context, f"requests/{request_id}")
        
        if err:
            return error_result(err["message"], err["error_type"], {"ride": {}})

        return success_result({"ride": response})


@uber.action("get_ride_map")
class GetRideMapAction(ActionHandler):
    """Get a map URL showing the real-time location of an active ride."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        request_id_error = validate_required_string(inputs.get("request_id"), "request_id")
        if request_id_error:
            return error_result(request_id_error, "validation_error", {"href": None})

        request_id = inputs["request_id"].strip()
        
        response, err = await uber_fetch(context, f"requests/{request_id}/map")
        
        if err:
            return error_result(err["message"], err["error_type"], {"href": None})

        return success_result({"href": response.get("href")})


@uber.action("cancel_ride")
class CancelRideAction(ActionHandler):
    """Cancel an active ride request."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        request_id_error = validate_required_string(inputs.get("request_id"), "request_id")
        if request_id_error:
            return error_result(request_id_error, "validation_error")

        request_id = inputs["request_id"].strip()
        
        _, err = await uber_fetch(context, f"requests/{request_id}", method="DELETE")
        
        if err:
            return error_result(err["message"], err["error_type"])

        return success_result({})


@uber.action("get_ride_receipt")
class GetRideReceiptAction(ActionHandler):
    """Get the receipt for a completed ride."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        request_id_error = validate_required_string(inputs.get("request_id"), "request_id")
        if request_id_error:
            return error_result(request_id_error, "validation_error", {"receipt": {}})

        request_id = inputs["request_id"].strip()
        
        response, err = await uber_fetch(context, f"requests/{request_id}/receipt")
        
        if err:
            return error_result(err["message"], err["error_type"], {"receipt": {}})

        return success_result({"receipt": response})


# ---- User Action Handlers ----

@uber.action("get_user_profile")
class GetUserProfileAction(ActionHandler):
    """Get the authenticated user's Uber profile information."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        response, err = await uber_fetch(context, "me")
        
        if err:
            return error_result(err["message"], err["error_type"], {"user": {}})

        return success_result({"user": response})


@uber.action("get_ride_history")
class GetRideHistoryAction(ActionHandler):
    """Get the user's ride history."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        params: Dict[str, Any] = {}

        limit = validate_limit(inputs.get("limit"), max_limit=50)
        params["limit"] = limit

        offset = validate_offset(inputs.get("offset"))
        if offset > 0:
            params["offset"] = offset

        response, err = await uber_fetch(context, "history", params=params)
        
        if err:
            return error_result(err["message"], err["error_type"], {
                "history": [], "count": 0
            })

        return success_result({
            "history": response.get("history", []),
            "count": response.get("count", 0)
        })


@uber.action("get_payment_methods")
class GetPaymentMethodsAction(ActionHandler):
    """Get the user's available payment methods."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        response, err = await uber_fetch(context, "payment-methods")
        
        if err:
            return error_result(err["message"], err["error_type"], {
                "payment_methods": [], "last_used": None
            })

        return success_result({
            "payment_methods": response.get("payment_methods", []),
            "last_used": response.get("last_used")
        })
