from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, Optional

# Create the integration using the config.json
shopify = Integration.load()

# Shopify API version
API_VERSION = "2024-10"


# ---- Helper Functions ----

def get_shop_url(context: ExecutionContext) -> str:
    """Extract the shop URL from the context credentials."""
    credentials = context.auth.get('credentials', {})
    shop_url = credentials.get('shop_url', '')
    # Ensure shop_url has proper format (e.g., "mystore.myshopify.com")
    if shop_url:
        # Remove protocol if present
        shop_url = shop_url.replace('https://', '').replace('http://', '')
        # Remove trailing slash
        shop_url = shop_url.rstrip('/')
    return shop_url


def get_shopify_api_url(context: ExecutionContext, endpoint: str = "") -> str:
    """Build Shopify Admin API URL."""
    shop_url = get_shop_url(context)
    return f"https://{shop_url}/admin/api/{API_VERSION}{endpoint}"


def build_shopify_headers(context: ExecutionContext) -> Dict[str, str]:
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


# ---- Customer Actions ----

@shopify.action("list_customers")
class ListCustomersHandler(ActionHandler):
    """Handler for listing customers."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/customers.json")
            headers = build_shopify_headers(context)

            allowed_params = [
                'limit', 'since_id', 'created_at_min', 'created_at_max',
                'updated_at_min', 'updated_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            # Set default limit if not provided
            if 'limit' not in params:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            customers = response.get('customers', [])
            return {
                "success": True,
                "customers": customers,
                "count": len(customers)
            }
        except Exception as e:
            return {
                "success": False,
                "customers": [],
                "count": 0,
                "message": str(e)
            }


@shopify.action("get_customer")
class GetCustomerHandler(ActionHandler):
    """Handler for getting a single customer."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            customer_id = inputs['customer_id']
            url = get_shopify_api_url(context, f"/customers/{customer_id}.json")
            headers = build_shopify_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return {
                "success": True,
                "customer": response.get('customer', {})
            }
        except Exception as e:
            return {
                "success": False,
                "customer": None,
                "message": str(e)
            }


@shopify.action("search_customers")
class SearchCustomersHandler(ActionHandler):
    """Handler for searching customers."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/customers/search.json")
            headers = build_shopify_headers(context)

            params = {
                'query': inputs['query']
            }
            if 'limit' in inputs and inputs['limit']:
                params['limit'] = inputs['limit']
            else:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            customers = response.get('customers', [])
            return {
                "success": True,
                "customers": customers,
                "count": len(customers)
            }
        except Exception as e:
            return {
                "success": False,
                "customers": [],
                "count": 0,
                "message": str(e)
            }


@shopify.action("create_customer")
class CreateCustomerHandler(ActionHandler):
    """Handler for creating a new customer."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/customers.json")
            headers = build_shopify_headers(context)

            # Build customer data
            customer_data = {}

            # Map input fields to Shopify API fields
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

            # Handle address if provided
            if 'address' in inputs and inputs['address']:
                customer_data['addresses'] = [inputs['address']]

            payload = {"customer": customer_data}

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return {
                "success": True,
                "customer": response.get('customer', {})
            }
        except Exception as e:
            return {
                "success": False,
                "customer": None,
                "message": str(e)
            }


@shopify.action("update_customer")
class UpdateCustomerHandler(ActionHandler):
    """Handler for updating an existing customer."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            customer_id = inputs['customer_id']
            url = get_shopify_api_url(context, f"/customers/{customer_id}.json")
            headers = build_shopify_headers(context)

            # Build customer update data
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

            return {
                "success": True,
                "customer": response.get('customer', {})
            }
        except Exception as e:
            return {
                "success": False,
                "customer": None,
                "message": str(e)
            }


# ---- Order Actions ----

@shopify.action("list_orders")
class ListOrdersHandler(ActionHandler):
    """Handler for listing orders."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/orders.json")
            headers = build_shopify_headers(context)

            allowed_params = [
                'limit', 'status', 'financial_status', 'fulfillment_status',
                'since_id', 'created_at_min', 'created_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            # Set default limit if not provided
            if 'limit' not in params:
                params['limit'] = 50

            # Default status to 'any' to get all orders
            if 'status' not in params:
                params['status'] = 'any'

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            orders = response.get('orders', [])
            return {
                "success": True,
                "orders": orders,
                "count": len(orders)
            }
        except Exception as e:
            return {
                "success": False,
                "orders": [],
                "count": 0,
                "message": str(e)
            }


@shopify.action("get_order")
class GetOrderHandler(ActionHandler):
    """Handler for getting a single order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            order_id = inputs['order_id']
            url = get_shopify_api_url(context, f"/orders/{order_id}.json")
            headers = build_shopify_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return {
                "success": True,
                "order": response.get('order', {})
            }
        except Exception as e:
            return {
                "success": False,
                "order": None,
                "message": str(e)
            }


@shopify.action("create_order")
class CreateOrderHandler(ActionHandler):
    """Handler for creating a new order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/orders.json")
            headers = build_shopify_headers(context)

            # Build order data
            order_data = {
                "line_items": inputs['line_items']
            }

            # Optional fields
            optional_fields = [
                'customer_id', 'email', 'financial_status', 'fulfillment_status',
                'send_receipt', 'send_fulfillment_receipt', 'note', 'tags',
                'shipping_address', 'billing_address'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    # Handle customer_id specially - needs to be nested
                    if field == 'customer_id':
                        order_data['customer'] = {'id': inputs[field]}
                    else:
                        order_data[field] = inputs[field]

            payload = {"order": order_data}

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return {
                "success": True,
                "order": response.get('order', {})
            }
        except Exception as e:
            return {
                "success": False,
                "order": None,
                "message": str(e)
            }


@shopify.action("cancel_order")
class CancelOrderHandler(ActionHandler):
    """Handler for cancelling an order."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            order_id = inputs['order_id']
            url = get_shopify_api_url(context, f"/orders/{order_id}/cancel.json")
            headers = build_shopify_headers(context)

            # Build cancel data
            cancel_data = {}

            if 'reason' in inputs and inputs['reason']:
                cancel_data['reason'] = inputs['reason']

            if 'email' in inputs:
                cancel_data['email'] = inputs['email']

            if 'restock' in inputs:
                cancel_data['restock'] = inputs['restock']

            response = await context.fetch(url, method="POST", json=cancel_data, headers=headers)

            return {
                "success": True,
                "order": response.get('order', {})
            }
        except Exception as e:
            return {
                "success": False,
                "order": None,
                "message": str(e)
            }


# ---- Product Actions ----

@shopify.action("list_products")
class ListProductsHandler(ActionHandler):
    """Handler for listing products."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/products.json")
            headers = build_shopify_headers(context)

            allowed_params = [
                'limit', 'since_id', 'title', 'vendor', 'product_type',
                'collection_id', 'status', 'created_at_min', 'created_at_max'
            ]
            params = build_query_params(inputs, allowed_params)

            # Set default limit if not provided
            if 'limit' not in params:
                params['limit'] = 50

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            products = response.get('products', [])
            return {
                "success": True,
                "products": products,
                "count": len(products)
            }
        except Exception as e:
            return {
                "success": False,
                "products": [],
                "count": 0,
                "message": str(e)
            }


@shopify.action("get_product")
class GetProductHandler(ActionHandler):
    """Handler for getting a single product."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            product_id = inputs['product_id']
            url = get_shopify_api_url(context, f"/products/{product_id}.json")
            headers = build_shopify_headers(context)

            response = await context.fetch(url, method="GET", headers=headers)

            return {
                "success": True,
                "product": response.get('product', {})
            }
        except Exception as e:
            return {
                "success": False,
                "product": None,
                "message": str(e)
            }


@shopify.action("create_product")
class CreateProductHandler(ActionHandler):
    """Handler for creating a new product."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/products.json")
            headers = build_shopify_headers(context)

            # Build product data
            product_data = {
                "title": inputs['title']
            }

            # Optional fields
            optional_fields = [
                'body_html', 'vendor', 'product_type', 'tags', 'status',
                'variants', 'options', 'images'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    product_data[field] = inputs[field]

            payload = {"product": product_data}

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return {
                "success": True,
                "product": response.get('product', {})
            }
        except Exception as e:
            return {
                "success": False,
                "product": None,
                "message": str(e)
            }


@shopify.action("update_product")
class UpdateProductHandler(ActionHandler):
    """Handler for updating an existing product."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            product_id = inputs['product_id']
            url = get_shopify_api_url(context, f"/products/{product_id}.json")
            headers = build_shopify_headers(context)

            # Build product update data
            product_data = {}

            optional_fields = [
                'title', 'body_html', 'vendor', 'product_type', 'tags', 'status'
            ]

            for field in optional_fields:
                if field in inputs and inputs[field] is not None:
                    product_data[field] = inputs[field]

            payload = {"product": product_data}

            response = await context.fetch(url, method="PUT", json=payload, headers=headers)

            return {
                "success": True,
                "product": response.get('product', {})
            }
        except Exception as e:
            return {
                "success": False,
                "product": None,
                "message": str(e)
            }


# ---- Inventory Actions ----

@shopify.action("get_inventory_levels")
class GetInventoryLevelsHandler(ActionHandler):
    """Handler for getting inventory levels."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/inventory_levels.json")
            headers = build_shopify_headers(context)

            params = {}

            if 'inventory_item_ids' in inputs and inputs['inventory_item_ids']:
                params['inventory_item_ids'] = inputs['inventory_item_ids']

            if 'location_ids' in inputs and inputs['location_ids']:
                params['location_ids'] = inputs['location_ids']

            if 'limit' in inputs and inputs['limit']:
                params['limit'] = inputs['limit']
            else:
                params['limit'] = 50

            # At least one of inventory_item_ids or location_ids is required
            if not params.get('inventory_item_ids') and not params.get('location_ids'):
                return {
                    "success": False,
                    "inventory_levels": [],
                    "count": 0,
                    "message": "Either inventory_item_ids or location_ids is required"
                }

            response = await context.fetch(url, method="GET", params=params, headers=headers)

            inventory_levels = response.get('inventory_levels', [])
            return {
                "success": True,
                "inventory_levels": inventory_levels,
                "count": len(inventory_levels)
            }
        except Exception as e:
            return {
                "success": False,
                "inventory_levels": [],
                "count": 0,
                "message": str(e)
            }


@shopify.action("set_inventory_level")
class SetInventoryLevelHandler(ActionHandler):
    """Handler for setting inventory level."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        try:
            url = get_shopify_api_url(context, "/inventory_levels/set.json")
            headers = build_shopify_headers(context)

            payload = {
                "location_id": inputs['location_id'],
                "inventory_item_id": inputs['inventory_item_id'],
                "available": inputs['available']
            }

            response = await context.fetch(url, method="POST", json=payload, headers=headers)

            return {
                "success": True,
                "inventory_level": response.get('inventory_level', {})
            }
        except Exception as e:
            return {
                "success": False,
                "inventory_level": None,
                "message": str(e)
            }
