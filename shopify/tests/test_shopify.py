"""
Shopify Integration Testbed
===========================

Real API integration testing against Shopify Admin API with placeholder credentials.

Prerequisites:
1. Shopify Partner account or store with API access
2. OAuth 2.0 access token from Shopify
3. Store URL (e.g., your-store.myshopify.com)

Credential Setup:
- Create a custom app in Shopify Admin or use OAuth flow
- Get the Admin API Access Token
- Note your store's myshopify.com URL

Running Tests:
    cd shopify/tests
    python test_shopify.py

Notes:
- Makes real API calls - review Shopify rate limits (40 requests/app/store/minute)
- Some tests require existing data in your store
- Create operations add records to your Shopify store
"""

import asyncio
import time
from context import shopify
from autohive_integrations_sdk import ExecutionContext


# =============================================================================
# CONFIGURATION - Update these values with your Shopify credentials
# =============================================================================
AUTH = {
    "auth_type": "PlatformOauth2",
    "credentials": {
        "access_token": "<your-shopify-access-token>",
        "shop_url": "your-store.myshopify.com"  # Your Shopify store URL
    }
}

# Test IDs - Replace with actual IDs from your Shopify store
TEST_CUSTOMER_ID = "<customer-id>"  # Use list_customers to find one
TEST_ORDER_ID = "<order-id>"  # Use list_orders to find one
TEST_PRODUCT_ID = "<product-id>"  # Use list_products to find one
TEST_LOCATION_ID = "<location-id>"  # Your store's location ID
TEST_INVENTORY_ITEM_ID = "<inventory-item-id>"  # From a product variant
# =============================================================================


async def test_list_customers():
    """Test listing customers with pagination."""
    inputs = {
        "limit": 10
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("list_customers", inputs, context)
            print(f"List Customers Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'customers' in result, "Response missing 'customers' field"
            assert 'count' in result, "Response missing 'count' field"
            print(f"✓ test_list_customers passed - Found {result['count']} customers")
            return result
        except Exception as e:
            print(f"✗ Error testing list_customers: {e}")
            return None


async def test_get_customer():
    """Test getting a specific customer by ID."""
    inputs = {
        "customer_id": TEST_CUSTOMER_ID
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("get_customer", inputs, context)
            print(f"Get Customer Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'customer' in result, "Response missing 'customer' field"
            print(f"✓ test_get_customer passed - Customer: {result['customer'].get('email', 'N/A')}")
            return result
        except Exception as e:
            print(f"✗ Error testing get_customer: {e}")
            return None


async def test_search_customers():
    """Test searching customers by query."""
    inputs = {
        "query": "email:*@*",  # Search for any customer with email
        "limit": 5
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("search_customers", inputs, context)
            print(f"Search Customers Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'customers' in result, "Response missing 'customers' field"
            print(f"✓ test_search_customers passed - Found {result['count']} customers")
            return result
        except Exception as e:
            print(f"✗ Error testing search_customers: {e}")
            return None


async def test_create_customer():
    """Test creating a new customer."""
    timestamp = int(time.time())
    inputs = {
        "email": f"test.customer.{timestamp}@example.com",
        "first_name": "Test",
        "last_name": "Customer",
        "phone": "+64211234567",
        "verified_email": True,
        "send_email_welcome": False,
        "tags": "test,automated",
        "note": "Created by automated test"
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("create_customer", inputs, context)
            print(f"Create Customer Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'customer' in result, "Response missing 'customer' field"
            assert result['customer'].get('id'), "Customer ID not returned"
            print(f"✓ test_create_customer passed - Customer ID: {result['customer']['id']}")
            return result
        except Exception as e:
            print(f"✗ Error testing create_customer: {e}")
            return None


async def test_update_customer():
    """Test updating an existing customer."""
    inputs = {
        "customer_id": TEST_CUSTOMER_ID,
        "note": f"Updated by test at {int(time.time())}",
        "tags": "test,updated"
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("update_customer", inputs, context)
            print(f"Update Customer Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'customer' in result, "Response missing 'customer' field"
            print(f"✓ test_update_customer passed")
            return result
        except Exception as e:
            print(f"✗ Error testing update_customer: {e}")
            return None


async def test_list_orders():
    """Test listing orders with filters."""
    inputs = {
        "limit": 10,
        "status": "any"
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("list_orders", inputs, context)
            print(f"List Orders Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'orders' in result, "Response missing 'orders' field"
            assert 'count' in result, "Response missing 'count' field"
            print(f"✓ test_list_orders passed - Found {result['count']} orders")
            return result
        except Exception as e:
            print(f"✗ Error testing list_orders: {e}")
            return None


async def test_get_order():
    """Test getting a specific order by ID."""
    inputs = {
        "order_id": TEST_ORDER_ID
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("get_order", inputs, context)
            print(f"Get Order Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'order' in result, "Response missing 'order' field"
            print(f"✓ test_get_order passed - Order: #{result['order'].get('order_number', 'N/A')}")
            return result
        except Exception as e:
            print(f"✗ Error testing get_order: {e}")
            return None


async def test_create_order():
    """Test creating a new order (custom line items, no payment)."""
    inputs = {
        "line_items": [
            {
                "title": "Test Product",
                "price": "10.00",
                "quantity": 1
            }
        ],
        "financial_status": "pending",
        "send_receipt": False,
        "note": "Test order created via API",
        "tags": "test,automated"
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("create_order", inputs, context)
            print(f"Create Order Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'order' in result, "Response missing 'order' field"
            assert result['order'].get('id'), "Order ID not returned"
            print(f"✓ test_create_order passed - Order ID: {result['order']['id']}")
            return result
        except Exception as e:
            print(f"✗ Error testing create_order: {e}")
            return None


async def test_list_products():
    """Test listing products with filters."""
    inputs = {
        "limit": 10
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("list_products", inputs, context)
            print(f"List Products Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'products' in result, "Response missing 'products' field"
            assert 'count' in result, "Response missing 'count' field"
            print(f"✓ test_list_products passed - Found {result['count']} products")
            return result
        except Exception as e:
            print(f"✗ Error testing list_products: {e}")
            return None


async def test_get_product():
    """Test getting a specific product by ID."""
    inputs = {
        "product_id": TEST_PRODUCT_ID
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("get_product", inputs, context)
            print(f"Get Product Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'product' in result, "Response missing 'product' field"
            print(f"✓ test_get_product passed - Product: {result['product'].get('title', 'N/A')}")
            return result
        except Exception as e:
            print(f"✗ Error testing get_product: {e}")
            return None


async def test_create_product():
    """Test creating a new product."""
    timestamp = int(time.time())
    inputs = {
        "title": f"Test Product {timestamp}",
        "body_html": "<p>This is a test product created via the API.</p>",
        "vendor": "Test Vendor",
        "product_type": "Test",
        "tags": "test,automated",
        "status": "draft",
        "variants": [
            {
                "price": "19.99",
                "sku": f"TEST-{timestamp}",
                "inventory_quantity": 100
            }
        ]
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("create_product", inputs, context)
            print(f"Create Product Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'product' in result, "Response missing 'product' field"
            assert result['product'].get('id'), "Product ID not returned"
            print(f"✓ test_create_product passed - Product ID: {result['product']['id']}")
            return result
        except Exception as e:
            print(f"✗ Error testing create_product: {e}")
            return None


async def test_update_product():
    """Test updating an existing product."""
    inputs = {
        "product_id": TEST_PRODUCT_ID,
        "title": f"Updated Product Title {int(time.time())}",
        "tags": "test,updated"
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("update_product", inputs, context)
            print(f"Update Product Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'product' in result, "Response missing 'product' field"
            print(f"✓ test_update_product passed")
            return result
        except Exception as e:
            print(f"✗ Error testing update_product: {e}")
            return None


async def test_get_inventory_levels():
    """Test getting inventory levels."""
    inputs = {
        "location_ids": TEST_LOCATION_ID,
        "limit": 10
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("get_inventory_levels", inputs, context)
            print(f"Get Inventory Levels Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'inventory_levels' in result, "Response missing 'inventory_levels' field"
            print(f"✓ test_get_inventory_levels passed - Found {result['count']} levels")
            return result
        except Exception as e:
            print(f"✗ Error testing get_inventory_levels: {e}")
            return None


async def test_set_inventory_level():
    """Test setting inventory level for an item at a location."""
    inputs = {
        "inventory_item_id": TEST_INVENTORY_ITEM_ID,
        "location_id": TEST_LOCATION_ID,
        "available": 50
    }

    async with ExecutionContext(auth=AUTH) as context:
        try:
            result = await shopify.execute_action("set_inventory_level", inputs, context)
            print(f"Set Inventory Level Result: {result}")

            assert result.get('success') == True, f"Action failed: {result.get('message', 'Unknown error')}"
            assert 'inventory_level' in result, "Response missing 'inventory_level' field"
            print(f"✓ test_set_inventory_level passed")
            return result
        except Exception as e:
            print(f"✗ Error testing set_inventory_level: {e}")
            return None


# =============================================================================
# Test Runners
# =============================================================================

async def run_safe_tests():
    """
    Run tests that only READ data (safe for production stores).
    These tests don't create, update, or delete any data.
    """
    print("\n" + "=" * 60)
    print("RUNNING SAFE (READ-ONLY) TESTS")
    print("=" * 60 + "\n")

    tests = [
        ("List Customers", test_list_customers),
        ("Search Customers", test_search_customers),
        ("List Orders", test_list_orders),
        ("List Products", test_list_products),
    ]

    results = {"passed": 0, "failed": 0}

    for name, test_func in tests:
        print(f"\n--- Testing: {name} ---")
        try:
            result = await test_func()
            if result and result.get('success'):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results["failed"] += 1

    print("\n" + "=" * 60)
    print(f"SAFE TESTS COMPLETE: {results['passed']} passed, {results['failed']} failed")
    print("=" * 60 + "\n")

    return results


async def run_get_by_id_tests():
    """
    Run tests that GET specific records by ID.
    Requires valid TEST_*_ID values to be set.
    """
    print("\n" + "=" * 60)
    print("RUNNING GET-BY-ID TESTS")
    print("=" * 60 + "\n")

    tests = [
        ("Get Customer", test_get_customer),
        ("Get Order", test_get_order),
        ("Get Product", test_get_product),
        ("Get Inventory Levels", test_get_inventory_levels),
    ]

    results = {"passed": 0, "failed": 0}

    for name, test_func in tests:
        print(f"\n--- Testing: {name} ---")
        try:
            result = await test_func()
            if result and result.get('success'):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results["failed"] += 1

    print("\n" + "=" * 60)
    print(f"GET-BY-ID TESTS COMPLETE: {results['passed']} passed, {results['failed']} failed")
    print("=" * 60 + "\n")

    return results


async def run_write_tests():
    """
    Run tests that CREATE or UPDATE data.
    WARNING: These tests will create/modify records in your Shopify store!
    """
    print("\n" + "=" * 60)
    print("RUNNING WRITE TESTS (CREATES/UPDATES DATA)")
    print("=" * 60 + "\n")

    tests = [
        ("Create Customer", test_create_customer),
        ("Create Product", test_create_product),
        ("Create Order", test_create_order),
    ]

    results = {"passed": 0, "failed": 0}

    for name, test_func in tests:
        print(f"\n--- Testing: {name} ---")
        try:
            result = await test_func()
            if result and result.get('success'):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results["failed"] += 1

    print("\n" + "=" * 60)
    print(f"WRITE TESTS COMPLETE: {results['passed']} passed, {results['failed']} failed")
    print("=" * 60 + "\n")

    return results


async def run_update_tests():
    """
    Run tests that UPDATE existing data.
    Requires valid TEST_*_ID values to be set.
    """
    print("\n" + "=" * 60)
    print("RUNNING UPDATE TESTS")
    print("=" * 60 + "\n")

    tests = [
        ("Update Customer", test_update_customer),
        ("Update Product", test_update_product),
        ("Set Inventory Level", test_set_inventory_level),
    ]

    results = {"passed": 0, "failed": 0}

    for name, test_func in tests:
        print(f"\n--- Testing: {name} ---")
        try:
            result = await test_func()
            if result and result.get('success'):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results["failed"] += 1

    print("\n" + "=" * 60)
    print(f"UPDATE TESTS COMPLETE: {results['passed']} passed, {results['failed']} failed")
    print("=" * 60 + "\n")

    return results


async def run_all_tests():
    """Run all tests - use with caution on production stores!"""
    print("\n" + "=" * 60)
    print("RUNNING ALL SHOPIFY INTEGRATION TESTS")
    print("=" * 60)

    all_results = {"passed": 0, "failed": 0}

    # Safe tests (read-only)
    safe_results = await run_safe_tests()
    all_results["passed"] += safe_results["passed"]
    all_results["failed"] += safe_results["failed"]

    # Get-by-ID tests
    get_results = await run_get_by_id_tests()
    all_results["passed"] += get_results["passed"]
    all_results["failed"] += get_results["failed"]

    # Write tests (create)
    write_results = await run_write_tests()
    all_results["passed"] += write_results["passed"]
    all_results["failed"] += write_results["failed"]

    # Update tests
    update_results = await run_update_tests()
    all_results["passed"] += update_results["passed"]
    all_results["failed"] += update_results["failed"]

    print("\n" + "=" * 60)
    print(f"ALL TESTS COMPLETE: {all_results['passed']} passed, {all_results['failed']} failed")
    print("=" * 60 + "\n")

    return all_results


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys

    print("""
╔═══════════════════════════════════════════════════════════════╗
║           SHOPIFY INTEGRATION TEST SUITE                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Usage:                                                        ║
║    python test_shopify.py [option]                             ║
║                                                                ║
║  Options:                                                      ║
║    safe     - Run read-only tests (list operations)            ║
║    get      - Run get-by-ID tests (requires TEST_*_ID)         ║
║    write    - Run create tests (adds data to store)            ║
║    update   - Run update tests (modifies existing data)        ║
║    all      - Run all tests                                    ║
║                                                                ║
║  Default: safe                                                 ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    option = sys.argv[1] if len(sys.argv) > 1 else "safe"

    if option == "safe":
        asyncio.run(run_safe_tests())
    elif option == "get":
        asyncio.run(run_get_by_id_tests())
    elif option == "write":
        asyncio.run(run_write_tests())
    elif option == "update":
        asyncio.run(run_update_tests())
    elif option == "all":
        asyncio.run(run_all_tests())
    else:
        print(f"Unknown option: {option}")
        print("Use: safe, get, write, update, or all")
