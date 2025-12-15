"""
Shopify Admin API Integration
=============================

Provides access to Shopify's Admin API for store management operations.

Supported Operations:
- Customers: list, get, search, create, update
- Orders: list, get, create, cancel
- Products: list, get, create, update
- Inventory: get levels, set levels
- Locations: list, get
- Fulfillments: list, create, update tracking
- Draft Orders: list, create, complete, delete
- Shop: get info

Authentication:
- OAuth 2.0 with access token
- Header: X-Shopify-Access-Token

Rate Limits:
- GraphQL: 100 points/second (1,000 capacity)
- REST: 40 requests/minute

API Version: 2024-10
"""

from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any

# Create the integration using the config.json
shopify_admin = Integration.load()

# Shopify API version
API_VERSION = "2024-10"


# ============================================================================
# Helper Functions
# ============================================================================

def get_shop_url(context: ExecutionContext) -> str:
    """Extract the shop URL from the context credentials."""
    credentials = context.auth.get('credentials', {})
    shop_url = credentials.get('shop_url', '')
    if shop_url:
        # Remove protocol if present
        shop_url = shop_url.replace('https://', '').replace('http://', '')
        # Remove trailing slash
        shop_url = shop_url.rstrip('/')
    return shop_url


def get_api_url(context: ExecutionContext, endpoint: str = "") -> str:
    """Build Shopify Admin API URL."""
    shop_url = get_shop_url(context)
    return f"https://{shop_url}/admin/api/{API_VERSION}{endpoint}"


def build_headers(context: ExecutionContext) -> Dict[str, str]:
    """Build headers for Shopify API requests with OAuth token."""
    access_token = context.auth['credentials']['access_token']
    return {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }


def build_query_params(inputs: Dict[str, Any], allowed_params: list) -> Dict[str, Any]:
    """Build query parameters from inputs, filtering only allowed params."""
    params = {}
    for param in allowed_params:
        if param in inputs and inputs[param] is not None and inputs[param] != "":
            params[param] = inputs[param]
    return params


def success_response(**kwargs) -> ActionResult:
    """Build a standardized success response."""
    return ActionResult(data={"success": True, **kwargs}, cost_usd=0)


def error_response(message: str, **kwargs) -> ActionResult:
    """Build a standardized error response."""
    data = {"success": False, "message": str(message)}
    data.update(kwargs)
    return ActionResult(data=data, cost_usd=0)


# ============================================================================
# Customer Actions
# ============================================================================

@shopify_admin.action("list_customers")
class ListCustomersHandler(ActionHandler):
    """List customers with optional filtering and pagination."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/customers.json")
            headers = build_headers(context)

            allowed_params = [
                'limit', 'since_id', 'created_at_min', 'created_at_max',
                'updated_at_min', 'updated_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            if 'limit' not in params:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            customers = response.get('customers', [])
            return success_response(customers=customers, count=len(customers))
        except Exception as e:
            return error_response(e, customers=[], count=0)


@shopify_admin.action("get_customer")
class GetCustomerHandler(ActionHandler):
    """Get a single customer by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            customer_id = inputs['customer_id']
            url = get_api_url(context, f"/customers/{customer_id}.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return success_response(customer=response.get('customer', {}))
        except Exception as e:
            return error_response(e, customer=None)


@shopify_admin.action("search_customers")
class SearchCustomersHandler(ActionHandler):
    """Search customers by query string."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/customers/search.json")
            headers = build_headers(context)

            params = {'query': inputs['query']}
            if 'limit' in inputs and inputs['limit']:
                params['limit'] = inputs['limit']
            else:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            customers = response.get('customers', [])
            return success_response(customers=customers, count=len(customers))
        except Exception as e:
            return error_response(e, customers=[], count=0)


@shopify_admin.action("create_customer")
class CreateCustomerHandler(ActionHandler):
    """Create a new customer."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/customers.json")
            headers = build_headers(context)

            customer_data = {}
            field_mapping = {
                'email': 'email',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone': 'phone',
                'verified_email': 'verified_email',
                'send_email_welcome': 'send_email_welcome',
                'tags': 'tags',
                'note': 'note',
                'tax_exempt': 'tax_exempt'
            }

            for input_field, api_field in field_mapping.items():
                if input_field in inputs and inputs[input_field] is not None:
                    customer_data[api_field] = inputs[input_field]

            if 'address' in inputs and inputs['address']:
                customer_data['addresses'] = [inputs['address']]

            payload = {"customer": customer_data}
            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(customer=response.get('customer', {}))
        except Exception as e:
            return error_response(e, customer=None)


@shopify_admin.action("update_customer")
class UpdateCustomerHandler(ActionHandler):
    """Update an existing customer."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            customer_id = inputs['customer_id']
            url = get_api_url(context, f"/customers/{customer_id}.json")
            headers = build_headers(context)

            customer_data = {}
            field_mapping = {
                'email': 'email',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone': 'phone',
                'tags': 'tags',
                'note': 'note',
                'tax_exempt': 'tax_exempt'
            }

            for input_field, api_field in field_mapping.items():
                if input_field in inputs and inputs[input_field] is not None:
                    customer_data[api_field] = inputs[input_field]

            payload = {"customer": customer_data}
            response = await context.fetch(url, method="PUT", json=payload, headers=headers)

            return success_response(customer=response.get('customer', {}))
        except Exception as e:
            return error_response(e, customer=None)


# ============================================================================
# Order Actions
# ============================================================================

@shopify_admin.action("list_orders")
class ListOrdersHandler(ActionHandler):
    """List orders with optional filtering."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/orders.json")
            headers = build_headers(context)

            allowed_params = [
                'limit', 'status', 'financial_status', 'fulfillment_status',
                'since_id', 'created_at_min', 'created_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            if 'limit' not in params:
                params['limit'] = 50
            if 'status' not in params:
                params['status'] = 'any'

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            orders = response.get('orders', [])
            return success_response(orders=orders, count=len(orders))
        except Exception as e:
            return error_response(e, orders=[], count=0)


@shopify_admin.action("get_order")
class GetOrderHandler(ActionHandler):
    """Get a single order by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            order_id = inputs['order_id']
            url = get_api_url(context, f"/orders/{order_id}.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return success_response(order=response.get('order', {}))
        except Exception as e:
            return error_response(e, order=None)


@shopify_admin.action("create_order")
class CreateOrderHandler(ActionHandler):
    """Create a new order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/orders.json")
            headers = build_headers(context)

            order_data = {"line_items": inputs['line_items']}

            optional_fields = [
                'customer_id', 'email', 'financial_status', 'fulfillment_status',
                'send_receipt', 'send_fulfillment_receipt', 'note', 'tags',
                'shipping_address', 'billing_address'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    if field == 'customer_id':
                        order_data['customer'] = {'id': inputs[field]}
                    else:
                        order_data[field] = inputs[field]

            payload = {"order": order_data}
            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(order=response.get('order', {}))
        except Exception as e:
            return error_response(e, order=None)


@shopify_admin.action("cancel_order")
class CancelOrderHandler(ActionHandler):
    """Cancel an existing order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            order_id = inputs['order_id']
            url = get_api_url(context, f"/orders/{order_id}/cancel.json")
            headers = build_headers(context)

            cancel_data = {}
            if 'reason' in inputs and inputs['reason']:
                cancel_data['reason'] = inputs['reason']
            if 'email' in inputs:
                cancel_data['email'] = inputs['email']
            if 'restock' in inputs:
                cancel_data['restock'] = inputs['restock']

            response = await context.fetch(url, method="POST", json=cancel_data, headers=headers)

            return success_response(order=response.get('order', {}))
        except Exception as e:
            return error_response(e, order=None)


# ============================================================================
# Product Actions
# ============================================================================

@shopify_admin.action("list_products")
class ListProductsHandler(ActionHandler):
    """List products with optional filtering."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/products.json")
            headers = build_headers(context)

            allowed_params = [
                'limit', 'since_id', 'title', 'vendor', 'product_type',
                'collection_id', 'status', 'created_at_min', 'created_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            if 'limit' not in params:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            products = response.get('products', [])
            return success_response(products=products, count=len(products))
        except Exception as e:
            return error_response(e, products=[], count=0)


@shopify_admin.action("get_product")
class GetProductHandler(ActionHandler):
    """Get a single product by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            product_id = inputs['product_id']
            url = get_api_url(context, f"/products/{product_id}.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return success_response(product=response.get('product', {}))
        except Exception as e:
            return error_response(e, product=None)


@shopify_admin.action("create_product")
class CreateProductHandler(ActionHandler):
    """Create a new product."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/products.json")
            headers = build_headers(context)

            product_data = {"title": inputs['title']}

            optional_fields = [
                'body_html', 'vendor', 'product_type', 'tags', 'status',
                'variants', 'options', 'images'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    product_data[field] = inputs[field]

            payload = {"product": product_data}
            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(product=response.get('product', {}))
        except Exception as e:
            return error_response(e, product=None)


@shopify_admin.action("update_product")
class UpdateProductHandler(ActionHandler):
    """Update an existing product."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            product_id = inputs['product_id']
            url = get_api_url(context, f"/products/{product_id}.json")
            headers = build_headers(context)

            product_data = {}
            optional_fields = [
                'title', 'body_html', 'vendor', 'product_type', 'tags', 'status'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    product_data[field] = inputs[field]

            payload = {"product": product_data}
            response = await context.fetch(url, method="PUT", json=payload, headers=headers)

            return success_response(product=response.get('product', {}))
        except Exception as e:
            return error_response(e, product=None)


# ============================================================================
# Inventory Actions
# ============================================================================

@shopify_admin.action("get_inventory_levels")
class GetInventoryLevelsHandler(ActionHandler):
    """Get inventory levels by location or inventory item IDs."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/inventory_levels.json")
            headers = build_headers(context)

            params = {}
            if 'inventory_item_ids' in inputs and inputs['inventory_item_ids']:
                params['inventory_item_ids'] = inputs['inventory_item_ids']
            if 'location_ids' in inputs and inputs['location_ids']:
                params['location_ids'] = inputs['location_ids']
            if 'limit' in inputs and inputs['limit']:
                params['limit'] = inputs['limit']
            else:
                params['limit'] = 50

            if not params.get('inventory_item_ids') and not params.get('location_ids'):
                return error_response(
                    "Either inventory_item_ids or location_ids is required",
                    inventory_levels=[], count=0
                )

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            inventory_levels = response.get('inventory_levels', [])
            return success_response(inventory_levels=inventory_levels, count=len(inventory_levels))
        except Exception as e:
            return error_response(e, inventory_levels=[], count=0)


@shopify_admin.action("set_inventory_level")
class SetInventoryLevelHandler(ActionHandler):
    """Set inventory level for an item at a location."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/inventory_levels/set.json")
            headers = build_headers(context)

            payload = {
                "location_id": inputs['location_id'],
                "inventory_item_id": inputs['inventory_item_id'],
                "available": inputs['available']
            }

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(inventory_level=response.get('inventory_level', {}))
        except Exception as e:
            return error_response(e, inventory_level=None)


# ============================================================================
# Location Actions
# ============================================================================

@shopify_admin.action("list_locations")
class ListLocationsHandler(ActionHandler):
    """List all store locations."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/locations.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            locations = response.get('locations', [])
            return success_response(locations=locations, count=len(locations))
        except Exception as e:
            return error_response(e, locations=[], count=0)


@shopify_admin.action("get_location")
class GetLocationHandler(ActionHandler):
    """Get a single location by ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            location_id = inputs['location_id']
            url = get_api_url(context, f"/locations/{location_id}.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return success_response(location=response.get('location', {}))
        except Exception as e:
            return error_response(e, location=None)


# ============================================================================
# Shop Actions
# ============================================================================

@shopify_admin.action("get_shop")
class GetShopHandler(ActionHandler):
    """Get store information."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/shop.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return success_response(shop=response.get('shop', {}))
        except Exception as e:
            return error_response(e, shop=None)


# ============================================================================
# Draft Order Actions
# ============================================================================

@shopify_admin.action("list_draft_orders")
class ListDraftOrdersHandler(ActionHandler):
    """List draft orders."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/draft_orders.json")
            headers = build_headers(context)

            allowed_params = ['limit', 'since_id', 'status']
            params = build_query_params(inputs, allowed_params)

            if 'limit' not in params:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            draft_orders = response.get('draft_orders', [])
            return success_response(draft_orders=draft_orders, count=len(draft_orders))
        except Exception as e:
            return error_response(e, draft_orders=[], count=0)


@shopify_admin.action("create_draft_order")
class CreateDraftOrderHandler(ActionHandler):
    """Create a new draft order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            url = get_api_url(context, "/draft_orders.json")
            headers = build_headers(context)

            draft_order_data = {"line_items": inputs['line_items']}

            optional_fields = [
                'customer_id', 'email', 'note', 'tags',
                'shipping_address', 'billing_address', 'use_customer_default_address'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    if field == 'customer_id':
                        draft_order_data['customer'] = {'id': inputs[field]}
                    else:
                        draft_order_data[field] = inputs[field]

            payload = {"draft_order": draft_order_data}
            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(draft_order=response.get('draft_order', {}))
        except Exception as e:
            return error_response(e, draft_order=None)


@shopify_admin.action("complete_draft_order")
class CompleteDraftOrderHandler(ActionHandler):
    """Complete a draft order, converting it to a real order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            draft_order_id = inputs['draft_order_id']
            url = get_api_url(context, f"/draft_orders/{draft_order_id}/complete.json")
            headers = build_headers(context)

            params = {}
            if 'payment_pending' in inputs:
                params['payment_pending'] = inputs['payment_pending']

            response = await context.fetch(url, method="PUT", params=params, headers=headers)

            return success_response(draft_order=response.get('draft_order', {}))
        except Exception as e:
            return error_response(e, draft_order=None)


@shopify_admin.action("delete_draft_order")
class DeleteDraftOrderHandler(ActionHandler):
    """Delete a draft order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            draft_order_id = inputs['draft_order_id']
            url = get_api_url(context, f"/draft_orders/{draft_order_id}.json")
            headers = build_headers(context)

            await context.fetch(url, method="DELETE", headers=headers)

            return success_response(deleted=True, draft_order_id=draft_order_id)
        except Exception as e:
            return error_response(e, deleted=False)


# ============================================================================
# Fulfillment Actions
# ============================================================================

@shopify_admin.action("list_fulfillments")
class ListFulfillmentsHandler(ActionHandler):
    """List fulfillments for an order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            order_id = inputs['order_id']
            url = get_api_url(context, f"/orders/{order_id}/fulfillments.json")
            headers = build_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            fulfillments = response.get('fulfillments', [])
            return success_response(fulfillments=fulfillments, count=len(fulfillments))
        except Exception as e:
            return error_response(e, fulfillments=[], count=0)


@shopify_admin.action("create_fulfillment")
class CreateFulfillmentHandler(ActionHandler):
    """Create a fulfillment for an order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            order_id = inputs['order_id']
            url = get_api_url(context, f"/orders/{order_id}/fulfillments.json")
            headers = build_headers(context)

            fulfillment_data = {
                "location_id": inputs['location_id']
            }

            optional_fields = [
                'tracking_number', 'tracking_company', 'tracking_url',
                'notify_customer', 'line_items'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    fulfillment_data[field] = inputs[field]

            payload = {"fulfillment": fulfillment_data}
            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(fulfillment=response.get('fulfillment', {}))
        except Exception as e:
            return error_response(e, fulfillment=None)


@shopify_admin.action("update_fulfillment_tracking")
class UpdateFulfillmentTrackingHandler(ActionHandler):
    """Update tracking information for a fulfillment."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        try:
            fulfillment_id = inputs['fulfillment_id']
            url = get_api_url(context, f"/fulfillments/{fulfillment_id}/update_tracking.json")
            headers = build_headers(context)

            tracking_data = {}
            if 'tracking_number' in inputs:
                tracking_data['number'] = inputs['tracking_number']
            if 'tracking_company' in inputs:
                tracking_data['company'] = inputs['tracking_company']
            if 'tracking_url' in inputs:
                tracking_data['url'] = inputs['tracking_url']

            payload = {
                "fulfillment": {
                    "tracking_info": tracking_data,
                    "notify_customer": inputs.get('notify_customer', False)
                }
            }

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return success_response(fulfillment=response.get('fulfillment', {}))
        except Exception as e:
            return error_response(e, fulfillment=None)
