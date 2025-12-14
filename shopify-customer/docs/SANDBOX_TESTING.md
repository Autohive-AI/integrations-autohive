---
integration: shopify-customer
type: testing-guide
format: llm-optimized
---

# Shopify Customer Account API Testing Guide

## QUICK_START

### 1. Prerequisites
```yaml
required:
  - Shopify development store with customer accounts enabled
  - OAuth client configured in Headless channel
  - Test customer account created

testing_approach:
  - Manual OAuth flow first (browser)
  - Store tokens for automated tests
  - Run integration tests
```

### 2. Configure Test File
```python
AUTH = {
    "auth_type": "CustomerAccountOAuth",
    "credentials": {
        "access_token": "your-access-token",  # From OAuth flow
        "shop_url": "your-store.myshopify.com"
    }
}
```

### 3. Run Tests
```bash
cd shopify-customer/tests
python test_shopify_customer.py safe     # Profile, addresses
python test_shopify_customer.py orders   # Order history
python test_shopify_customer.py all      # All tests
```

---

## STORE_SETUP

### Enable Customer Accounts

```yaml
location: Shopify Admin > Settings > Customer accounts
steps:
  1: Select account type
     - "New customer accounts" (recommended for API)
     - Classic accounts (limited API support)
  2: Configure login options
  3: Save changes

verification:
  - Visit your-store.myshopify.com/account
  - Should see login page
```

### Configure OAuth Client

```yaml
location: Shopify Admin > Settings > Apps and sales channels
steps:
  1: Install Headless channel (if not present)
  2: Go to Headless channel settings
  3: Navigate to Customer Account API
  4: Add redirect URIs:
     - https://localhost:3000/callback (development)
     - https://yourapp.com/callback (production)
  5: Copy Client ID
```

---

## OBTAINING_TEST_TOKENS

### Manual OAuth Flow

Since the Customer Account API requires OAuth + PKCE, you need to complete the flow once to get tokens for testing.

#### Option 1: Browser-Based Test

```python
# save as get_tokens.py
import secrets
import hashlib
import base64
import webbrowser
from urllib.parse import urlencode

# Configuration
SHOP = "your-store.myshopify.com"
CLIENT_ID = "your-client-id"
REDIRECT_URI = "https://localhost:3000/callback"
SCOPES = [
    "customer_read_customers",
    "customer_write_customers",
    "customer_read_orders"
]

# Generate PKCE
code_verifier = secrets.token_urlsafe(32)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip('=')
state = secrets.token_urlsafe(16)

# Build URL
params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': ' '.join(SCOPES),
    'state': state,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
}
auth_url = f"https://{SHOP}/account/authorize?{urlencode(params)}"

print(f"Code Verifier (save this!): {code_verifier}")
print(f"State: {state}")
print(f"\nOpening browser to: {auth_url}")

webbrowser.open(auth_url)
```

#### Option 2: Exchange Code Script

```python
# save as exchange_code.py
import asyncio
import aiohttp

async def exchange_code():
    SHOP = "your-store.myshopify.com"
    CLIENT_ID = "your-client-id"
    REDIRECT_URI = "https://localhost:3000/callback"

    # From the previous step
    code = input("Enter authorization code: ")
    code_verifier = input("Enter code verifier: ")

    url = f"https://{SHOP}/account/oauth/token"
    data = {
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            print("\nTokens received:")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"Refresh Token: {result.get('refresh_token', 'N/A')[:30]}...")
            print(f"Expires In: {result.get('expires_in')} seconds")
            return result

asyncio.run(exchange_code())
```

---

## TEST_CONFIGURATION

### Environment Variables
```bash
# .env
SHOPIFY_CUSTOMER_ACCESS_TOKEN=your-access-token
SHOPIFY_CUSTOMER_REFRESH_TOKEN=your-refresh-token
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_CLIENT_ID=your-client-id
```

### Using Environment Variables
```python
import os

AUTH = {
    "auth_type": "CustomerAccountOAuth",
    "credentials": {
        "access_token": os.getenv("SHOPIFY_CUSTOMER_ACCESS_TOKEN", ""),
        "refresh_token": os.getenv("SHOPIFY_CUSTOMER_REFRESH_TOKEN", ""),
        "shop_url": os.getenv("SHOPIFY_STORE_URL", ""),
        "client_id": os.getenv("SHOPIFY_CLIENT_ID", "")
    }
}
```

---

## TEST_CATEGORIES

### Safe Tests (Read-Only)
```yaml
tests:
  - customer_get_profile
  - customer_list_addresses
  - customer_list_orders
  - customer_get_order

risk: None
data_modification: No
```

### Profile Tests
```yaml
tests:
  - customer_update_profile
  - customer_create_address
  - customer_update_address
  - customer_delete_address

risk: Low
data_modification: Yes (reversible)
cleanup: Manual or automated
```

### Order Tests
```yaml
tests:
  - customer_list_orders
  - customer_get_order

risk: None
data_modification: No
note: Requires existing orders in account
```

---

## RUNNING_TESTS

### Commands
```bash
# Read-only profile and order tests
python test_shopify_customer.py safe

# Profile modification tests
python test_shopify_customer.py profile

# Order viewing tests
python test_shopify_customer.py orders

# All tests
python test_shopify_customer.py all
```

### Expected Output
```
============================================================
RUNNING SAFE (READ-ONLY) TESTS
============================================================

--- Testing: Get Customer Profile ---
  test_get_profile passed - customer@example.com

--- Testing: List Addresses ---
  test_list_addresses passed - Found 2 addresses

============================================================
SAFE TESTS: 4 passed, 0 failed
============================================================
```

---

## CREATING_TEST_DATA

### Create Test Customer
```yaml
via_storefront:
  1: Use Storefront API to create customer
  2: Set known password
  3: Use credentials for OAuth flow

via_admin:
  1: Shopify Admin > Customers > Add customer
  2: Set password
  3: Note email for OAuth

via_checkout:
  1: Complete test purchase with account creation
  2: Customer auto-created with order history
```

### Create Test Orders
```yaml
method_1_bogus_gateway:
  1: Enable Bogus gateway in dev store
  2: Place order as test customer
  3: Card number "1" = success
  4: Orders appear in customer history

method_2_admin_api:
  1: Use Admin API create_order
  2: Associate with customer_id
  3: Order appears in customer account
```

---

## TOKEN_REFRESH_TESTING

### Test Token Refresh
```python
async def test_token_refresh():
    """Test refreshing an expired access token."""
    # Get new tokens using refresh token
    new_tokens = await refresh_access_token(
        shop=SHOP,
        client_id=CLIENT_ID,
        refresh_token=REFRESH_TOKEN
    )

    print(f"New Access Token: {new_tokens['access_token'][:50]}...")
    print(f"New Refresh Token: {new_tokens['refresh_token'][:30]}...")

    # Verify new token works
    result = await customer_get_profile(new_tokens['access_token'])
    assert result['success'], "New token should work"
```

---

## TROUBLESHOOTING

### Authentication Errors
```yaml
error: "401 Unauthorized"
causes:
  - Access token expired
  - Invalid token format

solutions:
  - Refresh token and retry
  - Complete OAuth flow again
  - Check token is customer token (not admin)
```

### Scope Errors
```yaml
error: "403 Forbidden" or "Insufficient scope"
causes:
  - Token doesn't have required scope
  - Scope not requested during OAuth

solutions:
  - Re-authorize with all needed scopes
  - Check scope list in OAuth URL
```

### PKCE Errors
```yaml
error: "invalid_grant" during token exchange
causes:
  - Code verifier doesn't match challenge
  - Authorization code expired (10 min)
  - Code already used

solutions:
  - Generate fresh PKCE values
  - Complete flow quickly
  - Use code only once
```

### Customer Account Issues
```yaml
error: "Customer accounts not enabled"
causes:
  - Store doesn't have customer accounts

solutions:
  - Enable in Settings > Customer accounts
  - Select "New customer accounts"
```

---

## TEST_PATTERNS

### Profile Operations
```python
async def test_profile_workflow():
    # Get current profile
    profile = await get_profile(context)
    original_name = profile['firstName']

    # Update profile
    await update_profile(context, firstName="TestName")

    # Verify update
    updated = await get_profile(context)
    assert updated['firstName'] == "TestName"

    # Restore original
    await update_profile(context, firstName=original_name)
```

### Address Operations
```python
async def test_address_workflow():
    # Create address
    address = await create_address(context, {
        'address1': '123 Test St',
        'city': 'TestCity',
        'country': 'US',
        'zip': '12345'
    })
    address_id = address['id']

    # Update address
    await update_address(context, address_id, city='NewCity')

    # Delete address (cleanup)
    await delete_address(context, address_id)
```

---

## CONTINUOUS_INTEGRATION

### GitHub Actions Example
```yaml
# .github/workflows/test-shopify-customer.yml
name: Shopify Customer API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        env:
          SHOPIFY_CUSTOMER_ACCESS_TOKEN: ${{ secrets.SHOPIFY_CUSTOMER_ACCESS_TOKEN }}
          SHOPIFY_STORE_URL: ${{ secrets.SHOPIFY_STORE_URL }}
        run: |
          cd shopify-customer/tests
          python test_shopify_customer.py safe
```

---

## RATE_LIMIT_HANDLING

### Check Rate Limits
```python
# Response headers include rate limit info
# X-Shopify-API-Call-Limit: current/max

async def with_rate_limit_handling(func):
    """Execute with rate limit handling."""
    for attempt in range(3):
        try:
            return await func()
        except RateLimitError as e:
            wait = e.retry_after or (2 ** attempt)
            await asyncio.sleep(wait)
    raise Exception("Rate limit exceeded after retries")
```

### Batch Operations
```python
# Add delays between operations
for item in items:
    await process_item(item)
    await asyncio.sleep(0.5)  # 500ms delay
```
