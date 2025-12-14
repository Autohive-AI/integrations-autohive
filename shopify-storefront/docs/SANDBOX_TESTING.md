---
integration: shopify-storefront
type: testing-guide
format: llm-optimized
---

# Shopify Storefront API Testing Guide

## QUICK_START

### 1. Get Credentials
```yaml
required:
  - public_token: From Headless channel
  - shop_url: your-store.myshopify.com

optional:
  - private_token: For server-side testing
```

### 2. Configure Test File
```python
AUTH = {
    "auth_type": "StorefrontPublic",
    "credentials": {
        "public_token": "your-public-storefront-token",
        "shop_url": "your-store.myshopify.com"
    }
}
```

### 3. Run Tests
```bash
cd shopify-storefront/tests
python test_shopify_storefront.py safe
python test_shopify_storefront.py all
```

---

## GETTING_CREDENTIALS

### Install Headless Channel
```yaml
steps:
  1: Go to Store Admin > Sales channels
  2: Click "Add channel"
  3: Search for "Headless"
  4: Install "Headless" by Shopify
```

### Create Storefront Access
```yaml
steps:
  1: Go to Sales channels > Headless
  2: Click "Create storefront"
  3: Enter a name (e.g., "Test Storefront")
  4: Click Create
  5: Copy the Public access token
  6: Optionally copy Private access token (server-side)
```

### Configure Storefront API Permissions
```yaml
location: Headless > Storefront > Manage > Storefront API access

enable_scopes:
  - unauthenticated_read_product_listings
  - unauthenticated_read_product_inventory
  - unauthenticated_read_checkouts
  - unauthenticated_write_checkouts
  - unauthenticated_read_customers
  - unauthenticated_write_customers
```

---

## TEST_CONFIGURATION

### Environment Variables
```bash
# .env
SHOPIFY_STOREFRONT_PUBLIC_TOKEN=xxxxx
SHOPIFY_STOREFRONT_PRIVATE_TOKEN=shpat_xxxxx
SHOPIFY_STORE_URL=your-store.myshopify.com
```

### Using Environment Variables
```python
import os

AUTH = {
    "auth_type": "StorefrontPublic",
    "credentials": {
        "public_token": os.getenv("SHOPIFY_STOREFRONT_PUBLIC_TOKEN", ""),
        "shop_url": os.getenv("SHOPIFY_STORE_URL", "")
    }
}
```

---

## TEST_CATEGORIES

### Safe Tests (Read-Only)
```yaml
tests:
  - storefront_list_products
  - storefront_get_product
  - storefront_list_collections
  - storefront_get_collection
  - storefront_search_products

risk: None
data_modification: No
```

### Cart Tests
```yaml
tests:
  - storefront_create_cart
  - storefront_add_to_cart
  - storefront_update_cart_line
  - storefront_remove_from_cart

risk: Low
data_modification: Creates temporary carts
cleanup: Carts expire automatically
```

### Customer Tests
```yaml
tests:
  - storefront_create_customer
  - storefront_customer_login
  - storefront_get_customer

risk: Medium
data_modification: Creates test customer accounts
cleanup: Manual deletion via Admin API
```

---

## RUNNING_TESTS

### Commands
```bash
# Safe product queries
python test_shopify_storefront.py safe

# Cart operations
python test_shopify_storefront.py cart

# Customer operations
python test_shopify_storefront.py customer

# All tests
python test_shopify_storefront.py all
```

### Expected Output
```
============================================================
RUNNING SAFE (READ-ONLY) TESTS
============================================================

--- Testing: List Products ---
✓ test_list_products passed - Found 10 products

--- Testing: Get Product ---
✓ test_get_product passed - Product: Classic T-Shirt

============================================================
SAFE TESTS: 5 passed, 0 failed
============================================================
```

---

## FINDING_TEST_DATA

### Get Product Handle
```python
# List products and note a handle
result = await storefront.execute_action("storefront_list_products", {"first": 1}, context)
handle = result["products"][0]["handle"]
print(f"Product handle: {handle}")
```

### Get Variant ID (for cart operations)
```python
# Get a product with variants
result = await storefront.execute_action("storefront_get_product", {"handle": "some-product"}, context)
variant_id = result["product"]["variants"]["edges"][0]["node"]["id"]
print(f"Variant ID: {variant_id}")
```

---

## TROUBLESHOOTING

### Authentication Errors
```yaml
error: "Access denied"
causes:
  - Invalid or missing token
  - Wrong header used

solutions:
  - Verify token is from Headless channel
  - Use correct header for token type
  - Check token hasn't been regenerated
```

### Scope Errors
```yaml
error: "Access denied for this field"
causes:
  - Missing required scope

solutions:
  - Go to Headless > Storefront > Manage
  - Enable required Storefront API scopes
  - Wait a few minutes for propagation
```

### GraphQL Errors
```yaml
error: "Field 'x' doesn't exist on type 'Y'"
causes:
  - Wrong API version
  - Deprecated field

solutions:
  - Check current API version
  - Update query to current schema
  - Review Shopify changelog
```

---

## CART_TESTING_NOTES

### Cart Lifecycle
```yaml
creation: Carts are created on demand
persistence: Carts persist for customer session
expiration: Carts expire after inactivity (varies)
checkout: checkoutUrl leads to Shopify checkout
```

### Test Cart Pattern
```python
# Create cart
cart = await create_cart(context)
cart_id = cart["id"]

# Add items
await add_to_cart(context, cart_id, variant_id, quantity=2)

# Update quantity
await update_cart_line(context, cart_id, line_id, quantity=3)

# Remove items
await remove_from_cart(context, cart_id, [line_id])

# Cart automatically expires - no cleanup needed
```

---

## CUSTOMER_TESTING_NOTES

### Test Customer Pattern
```python
# Create unique test customer
timestamp = int(time.time())
email = f"test.customer.{timestamp}@example.com"

# Create customer
result = await create_customer(context, email, "TestPassword123!")

# Login to get access token
login = await customer_login(context, email, "TestPassword123!")
access_token = login["customerAccessToken"]["accessToken"]

# Use access token for authenticated queries
customer = await get_customer(context, access_token)
```

### Cleanup Test Customers
```yaml
option_1: Delete via Admin API (write_customers scope)
option_2: Leave as test data (tagged appropriately)
option_3: Use disposable email addresses
```

---

## RATE_LIMIT_HANDLING

### Check Query Complexity
```python
# Include cost extension in queries
{
  "query": "...",
  "extensions": {
    "cost": {
      "requestedQueryCost": 50,
      "actualQueryCost": 45,
      "throttleStatus": {
        "maximumAvailable": 1000,
        "currentlyAvailable": 955,
        "restoreRate": 50
      }
    }
  }
}
```

### Handle Throttling
```python
import asyncio

async def with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except ThrottleError as e:
            wait = e.retry_after or (2 ** attempt)
            await asyncio.sleep(wait)
    raise Exception("Max retries exceeded")
```
