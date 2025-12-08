from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler,
    ActionResult
)
from typing import Dict, Any
import base64


stripe_integration = Integration.load()

# Base URL for Stripe API
STRIPE_API_BASE_URL = "https://api.stripe.com"
API_VERSION = "v1"


# ---- Helper Functions ----

def get_auth_headers(context: ExecutionContext) -> Dict[str, str]:
    """
    Build authentication headers for Stripe API requests.
    Stripe uses HTTP Basic Auth with the API key as username.

    Args:
        context: ExecutionContext containing auth credentials

    Returns:
        Dictionary with Authorization header
    """
    credentials = context.auth.get("credentials", {})
    api_key = credentials.get("api_key", "")

    # Stripe uses Basic Auth: base64(api_key:)
    auth_string = base64.b64encode(f"{api_key}:".encode()).decode()

    return {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }


def build_form_data(data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """
    Convert nested dict to Stripe's form-encoded format.
    Stripe requires nested objects as key[subkey]=value format.

    Args:
        data: Dictionary to convert
        prefix: Prefix for nested keys

    Returns:
        Flattened dictionary for form encoding
    """
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}[{key}]" if prefix else key

        if isinstance(value, dict):
            result.update(build_form_data(value, full_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    result.update(build_form_data(item, f"{full_key}[{i}]"))
                else:
                    result[f"{full_key}[{i}]"] = str(item)
        elif value is not None:
            if isinstance(value, bool):
                result[full_key] = "true" if value else "false"
            else:
                result[full_key] = str(value)

    return result


def build_list_params(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Build query parameters for list endpoints."""
    params = {}

    if 'limit' in inputs and inputs['limit']:
        params['limit'] = min(inputs['limit'], 100)
    if 'starting_after' in inputs and inputs['starting_after']:
        params['starting_after'] = inputs['starting_after']
    if 'ending_before' in inputs and inputs['ending_before']:
        params['ending_before'] = inputs['ending_before']

    return params


# ---- Customer Action Handlers ----

@stripe_integration.action("list_customers")
class ListCustomersAction(ActionHandler):
    """Retrieve a paginated list of customers from Stripe."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            params = build_list_params(inputs)

            # Add optional filters
            if 'email' in inputs and inputs['email']:
                params['email'] = inputs['email']
            if 'created_gte' in inputs and inputs['created_gte']:
                params['created[gte]'] = inputs['created_gte']
            if 'created_lte' in inputs and inputs['created_lte']:
                params['created[lte]'] = inputs['created_lte']

            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/customers",
                method="GET",
                headers=headers,
                params=params
            )

            customers = response.get('data', [])

            return ActionResult(
                data={
                    "customers": customers,
                    "has_more": response.get('has_more', False),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "customers": [],
                    "has_more": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("get_customer")
class GetCustomerAction(ActionHandler):
    """Retrieve details of a specific customer by their ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            customer_id = inputs['customer_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/customers/{customer_id}",
                method="GET",
                headers=headers
            )

            return ActionResult(
                data={
                    "customer": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "customer": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("create_customer")
class CreateCustomerAction(ActionHandler):
    """Create a new customer in Stripe."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            body = {}

            # Add optional fields
            if 'email' in inputs and inputs['email']:
                body['email'] = inputs['email']
            if 'name' in inputs and inputs['name']:
                body['name'] = inputs['name']
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'phone' in inputs and inputs['phone']:
                body['phone'] = inputs['phone']
            if 'address' in inputs and inputs['address']:
                body['address'] = inputs['address']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/customers",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "customer": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "customer": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("update_customer")
class UpdateCustomerAction(ActionHandler):
    """Update an existing customer's information."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            customer_id = inputs['customer_id']
            body = {}

            # Add only provided fields
            if 'email' in inputs and inputs['email']:
                body['email'] = inputs['email']
            if 'name' in inputs and inputs['name']:
                body['name'] = inputs['name']
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'phone' in inputs and inputs['phone']:
                body['phone'] = inputs['phone']
            if 'address' in inputs and inputs['address']:
                body['address'] = inputs['address']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/customers/{customer_id}",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "customer": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "customer": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("delete_customer")
class DeleteCustomerAction(ActionHandler):
    """Permanently delete a customer from Stripe."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            customer_id = inputs['customer_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/customers/{customer_id}",
                method="DELETE",
                headers=headers
            )

            return ActionResult(
                data={
                    "id": response.get('id', customer_id),
                    "deleted": response.get('deleted', True),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "id": inputs.get('customer_id', ''),
                    "deleted": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


# ---- Invoice Action Handlers ----

@stripe_integration.action("list_invoices")
class ListInvoicesAction(ActionHandler):
    """Retrieve a paginated list of invoices from Stripe."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            params = build_list_params(inputs)

            # Add optional filters
            if 'customer' in inputs and inputs['customer']:
                params['customer'] = inputs['customer']
            if 'status' in inputs and inputs['status']:
                params['status'] = inputs['status']
            if 'created_gte' in inputs and inputs['created_gte']:
                params['created[gte]'] = inputs['created_gte']
            if 'created_lte' in inputs and inputs['created_lte']:
                params['created[lte]'] = inputs['created_lte']

            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices",
                method="GET",
                headers=headers,
                params=params
            )

            invoices = response.get('data', [])

            return ActionResult(
                data={
                    "invoices": invoices,
                    "has_more": response.get('has_more', False),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoices": [],
                    "has_more": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("get_invoice")
class GetInvoiceAction(ActionHandler):
    """Retrieve details of a specific invoice by its ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}",
                method="GET",
                headers=headers
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("create_invoice")
class CreateInvoiceAction(ActionHandler):
    """Create a new draft invoice in Stripe."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            body = {
                "customer": inputs['customer']
            }

            # Add optional fields
            if 'currency' in inputs and inputs['currency']:
                body['currency'] = inputs['currency']
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'auto_advance' in inputs:
                body['auto_advance'] = inputs['auto_advance']
            if 'collection_method' in inputs and inputs['collection_method']:
                body['collection_method'] = inputs['collection_method']
            if 'days_until_due' in inputs and inputs['days_until_due']:
                body['days_until_due'] = inputs['days_until_due']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("update_invoice")
class UpdateInvoiceAction(ActionHandler):
    """Update a draft invoice's details."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            body = {}

            # Add only provided fields
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'auto_advance' in inputs:
                body['auto_advance'] = inputs['auto_advance']
            if 'collection_method' in inputs and inputs['collection_method']:
                body['collection_method'] = inputs['collection_method']
            if 'days_until_due' in inputs and inputs['days_until_due']:
                body['days_until_due'] = inputs['days_until_due']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("delete_invoice")
class DeleteInvoiceAction(ActionHandler):
    """Permanently delete a draft invoice."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}",
                method="DELETE",
                headers=headers
            )

            return ActionResult(
                data={
                    "id": response.get('id', invoice_id),
                    "deleted": response.get('deleted', True),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "id": inputs.get('invoice_id', ''),
                    "deleted": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("finalize_invoice")
class FinalizeInvoiceAction(ActionHandler):
    """Finalize a draft invoice, making it ready for payment."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            body = {}

            if 'auto_advance' in inputs:
                body['auto_advance'] = inputs['auto_advance']

            headers = get_auth_headers(context)
            form_data = build_form_data(body) if body else {}

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}/finalize",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("send_invoice")
class SendInvoiceAction(ActionHandler):
    """Send a finalized invoice to the customer via email."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}/send",
                method="POST",
                headers=headers
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("pay_invoice")
class PayInvoiceAction(ActionHandler):
    """Pay an open invoice using the customer's default payment method."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            body = {}

            if 'payment_method' in inputs and inputs['payment_method']:
                body['payment_method'] = inputs['payment_method']

            headers = get_auth_headers(context)
            form_data = build_form_data(body) if body else {}

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}/pay",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("void_invoice")
class VoidInvoiceAction(ActionHandler):
    """Void an open invoice, marking it as uncollectible."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_id = inputs['invoice_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoices/{invoice_id}/void",
                method="POST",
                headers=headers
            )

            return ActionResult(
                data={
                    "invoice": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


# ---- Invoice Item Action Handlers ----

@stripe_integration.action("list_invoice_items")
class ListInvoiceItemsAction(ActionHandler):
    """Retrieve a paginated list of invoice items."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            params = build_list_params(inputs)

            # Add optional filters
            if 'customer' in inputs and inputs['customer']:
                params['customer'] = inputs['customer']
            if 'invoice' in inputs and inputs['invoice']:
                params['invoice'] = inputs['invoice']
            if 'pending' in inputs:
                params['pending'] = 'true' if inputs['pending'] else 'false'

            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoiceitems",
                method="GET",
                headers=headers,
                params=params
            )

            invoice_items = response.get('data', [])

            return ActionResult(
                data={
                    "invoice_items": invoice_items,
                    "has_more": response.get('has_more', False),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice_items": [],
                    "has_more": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("get_invoice_item")
class GetInvoiceItemAction(ActionHandler):
    """Retrieve details of a specific invoice item by its ID."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_item_id = inputs['invoice_item_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoiceitems/{invoice_item_id}",
                method="GET",
                headers=headers
            )

            return ActionResult(
                data={
                    "invoice_item": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice_item": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("create_invoice_item")
class CreateInvoiceItemAction(ActionHandler):
    """Create a new invoice item and optionally attach to a draft invoice."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            body = {
                "customer": inputs['customer']
            }

            # Add optional fields
            if 'invoice' in inputs and inputs['invoice']:
                body['invoice'] = inputs['invoice']
            if 'amount' in inputs and inputs['amount'] is not None:
                body['amount'] = inputs['amount']
            if 'currency' in inputs and inputs['currency']:
                body['currency'] = inputs['currency']
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'quantity' in inputs and inputs['quantity'] is not None:
                body['quantity'] = inputs['quantity']
            if 'unit_amount' in inputs and inputs['unit_amount'] is not None:
                body['unit_amount_decimal'] = inputs['unit_amount']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoiceitems",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice_item": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice_item": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("update_invoice_item")
class UpdateInvoiceItemAction(ActionHandler):
    """Update an existing invoice item."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_item_id = inputs['invoice_item_id']
            body = {}

            # Add only provided fields
            if 'amount' in inputs and inputs['amount'] is not None:
                body['amount'] = inputs['amount']
            if 'description' in inputs and inputs['description']:
                body['description'] = inputs['description']
            if 'quantity' in inputs and inputs['quantity'] is not None:
                body['quantity'] = inputs['quantity']
            if 'unit_amount' in inputs and inputs['unit_amount'] is not None:
                body['unit_amount_decimal'] = inputs['unit_amount']
            if 'metadata' in inputs and inputs['metadata']:
                body['metadata'] = inputs['metadata']

            headers = get_auth_headers(context)
            form_data = build_form_data(body)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoiceitems/{invoice_item_id}",
                method="POST",
                headers=headers,
                data=form_data
            )

            return ActionResult(
                data={
                    "invoice_item": response,
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "invoice_item": {},
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )


@stripe_integration.action("delete_invoice_item")
class DeleteInvoiceItemAction(ActionHandler):
    """Delete an invoice item that hasn't been attached to an invoice."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            invoice_item_id = inputs['invoice_item_id']
            headers = get_auth_headers(context)

            response = await context.fetch(
                f"{STRIPE_API_BASE_URL}/{API_VERSION}/invoiceitems/{invoice_item_id}",
                method="DELETE",
                headers=headers
            )

            return ActionResult(
                data={
                    "id": response.get('id', invoice_item_id),
                    "deleted": response.get('deleted', True),
                    "result": True
                },
                cost_usd=0.0
            )

        except Exception as e:
            return ActionResult(
                data={
                    "id": inputs.get('invoice_item_id', ''),
                    "deleted": False,
                    "result": False,
                    "error": str(e)
                },
                cost_usd=0.0
            )
