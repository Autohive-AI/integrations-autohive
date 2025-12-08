"""
Test suite for Stripe integration.

These tests require a valid Stripe API key to run.
Set your test key before running: export STRIPE_TEST_API_KEY=sk_test_xxx
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the module directly to avoid package name conflict with 'stripe' package
import importlib.util
spec = importlib.util.spec_from_file_location("stripe_module", os.path.join(parent_dir, "stripe.py"))
stripe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stripe_module)
stripe_integration = stripe_module.stripe_integration
from autohive_integrations_sdk import ExecutionContext


# Test API key - replace with your test key or set via environment variable
# Can also be passed as command line argument: python test_stripe.py sk_test_xxx
API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("STRIPE_TEST_API_KEY", "sk_test_your_key_here")


async def test_list_customers():
    """Test listing customers."""
    print("\n=== Test: List Customers ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "list_customers",
                {"limit": 5},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            print(f"Customers found: {len(data.get('customers', []))}")
            print(f"Has more: {data.get('has_more')}")

            if data.get('customers'):
                customer = data['customers'][0]
                print(f"First customer ID: {customer.get('id')}")
                print(f"First customer email: {customer.get('email')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_create_customer():
    """Test creating a customer."""
    print("\n=== Test: Create Customer ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "create_customer",
                {
                    "email": "test@example.com",
                    "name": "Test Customer",
                    "description": "Created by integration test",
                    "metadata": {"test": "true"}
                },
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            customer = data.get('customer', {})
            print(f"Customer ID: {customer.get('id')}")
            print(f"Customer email: {customer.get('email')}")

            return customer.get('id')
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_get_customer(customer_id: str):
    """Test getting a specific customer."""
    print("\n=== Test: Get Customer ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "get_customer",
                {"customer_id": customer_id},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            customer = data.get('customer', {})
            print(f"Customer ID: {customer.get('id')}")
            print(f"Customer name: {customer.get('name')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_update_customer(customer_id: str):
    """Test updating a customer."""
    print("\n=== Test: Update Customer ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "update_customer",
                {
                    "customer_id": customer_id,
                    "name": "Updated Test Customer",
                    "description": "Updated by integration test"
                },
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            customer = data.get('customer', {})
            print(f"Updated name: {customer.get('name')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_create_invoice(customer_id: str):
    """Test creating a draft invoice."""
    print("\n=== Test: Create Invoice ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "create_invoice",
                {
                    "customer": customer_id,
                    "currency": "nzd",
                    "description": "Test Invoice - RUC Purchase",
                    "auto_advance": False,
                    "collection_method": "send_invoice",
                    "days_until_due": 30
                },
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            invoice = data.get('invoice', {})
            print(f"Invoice ID: {invoice.get('id')}")
            print(f"Invoice status: {invoice.get('status')}")

            return invoice.get('id')
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_create_invoice_item(customer_id: str, invoice_id: str):
    """Test creating an invoice item."""
    print("\n=== Test: Create Invoice Item ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "create_invoice_item",
                {
                    "customer": customer_id,
                    "invoice": invoice_id,
                    "unit_amount": 6609,  # $66.09 in cents
                    "currency": "nzd",
                    "quantity": 5,
                    "description": "RUC - 5 units (5,000km)"
                },
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            item = data.get('invoice_item', {})
            print(f"Invoice Item ID: {item.get('id')}")
            print(f"Amount: {item.get('amount')}")

            return item.get('id')
        except Exception as e:
            print(f"Error: {e}")
            return None


async def test_list_invoices():
    """Test listing invoices."""
    print("\n=== Test: List Invoices ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "list_invoices",
                {"limit": 5, "status": "draft"},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            print(f"Invoices found: {len(data.get('invoices', []))}")
        except Exception as e:
            print(f"Error: {e}")


async def test_get_invoice(invoice_id: str):
    """Test getting a specific invoice."""
    print("\n=== Test: Get Invoice ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "get_invoice",
                {"invoice_id": invoice_id},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            invoice = data.get('invoice', {})
            print(f"Invoice ID: {invoice.get('id')}")
            print(f"Invoice total: {invoice.get('total')}")
            print(f"Invoice status: {invoice.get('status')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_update_invoice(invoice_id: str):
    """Test updating an invoice."""
    print("\n=== Test: Update Invoice ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "update_invoice",
                {
                    "invoice_id": invoice_id,
                    "description": "Updated: RUC Purchase - GTR680 (Test Vehicle)\n5 units (5,000km)"
                },
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            invoice = data.get('invoice', {})
            print(f"Updated description: {invoice.get('description')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_delete_invoice(invoice_id: str):
    """Test deleting a draft invoice."""
    print("\n=== Test: Delete Invoice ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "delete_invoice",
                {"invoice_id": invoice_id},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            print(f"Deleted: {data.get('deleted')}")
        except Exception as e:
            print(f"Error: {e}")


async def test_delete_customer(customer_id: str):
    """Test deleting a customer."""
    print("\n=== Test: Delete Customer ===")
    auth = {"credentials": {"api_key": API_KEY}}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await stripe_integration.execute_action(
                "delete_customer",
                {"customer_id": customer_id},
                context
            )

            data = result.result.data
            print(f"Result: {data.get('result')}")
            print(f"Deleted: {data.get('deleted')}")
        except Exception as e:
            print(f"Error: {e}")


async def run_all_tests():
    """Run all tests in sequence."""
    print("=" * 60)
    print("STRIPE INTEGRATION TEST SUITE")
    print("=" * 60)

    if API_KEY == "sk_test_your_key_here":
        print("\nWARNING: Using placeholder API key. Tests will fail.")
        print("Set STRIPE_TEST_API_KEY environment variable with your test key.")
        print("=" * 60)

    # Test customer CRUD
    await test_list_customers()

    customer_id = await test_create_customer()
    if customer_id:
        await test_get_customer(customer_id)
        await test_update_customer(customer_id)

        # Test invoice CRUD
        invoice_id = await test_create_invoice(customer_id)
        if invoice_id:
            await test_create_invoice_item(customer_id, invoice_id)
            await test_get_invoice(invoice_id)
            await test_update_invoice(invoice_id)
            await test_list_invoices()

            # Clean up - delete invoice
            await test_delete_invoice(invoice_id)

        # Clean up - delete customer
        await test_delete_customer(customer_id)

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
