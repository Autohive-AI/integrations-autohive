---
integration: shopify-customer
api_type: customer-account
auth_method: oauth2-pkce
base_url: https://{shop}.myshopify.com/account/customer/api/{version}/graphql
format: llm-optimized
---

# Shopify Customer Account API Integration

## QUICK_REFERENCE

| Property | Value |
|----------|-------|
| API Type | GraphQL only |
| Auth | OAuth 2.0 + PKCE |
| Header | Authorization: Bearer {token} |
| Rate Limit | 1000 pts (50/sec restore) |
| Purpose | Customer self-service |

---

## ACTIONS_INDEX

| Action | Scope Required | Description |
|--------|----------------|-------------|
| customer_get_profile | customer_read_customers | Get customer's profile |
| customer_update_profile | customer_write_customers | Update profile info |
| customer_list_addresses | customer_read_customers | List saved addresses |
| customer_create_address | customer_write_customers | Add new address |
| customer_update_address | customer_write_customers | Modify address |
| customer_delete_address | customer_write_customers | Remove address |
| customer_set_default_address | customer_write_customers | Set default address |
| customer_list_orders | customer_read_orders | View order history |
| customer_get_order | customer_read_orders | Get order details |
| customer_list_subscriptions | customer_read_own_subscription_contracts | List subscriptions |
| customer_update_subscription | customer_write_own_subscription_contracts | Modify subscription |

---

## AUTHENTICATION_SETUP

### OAuth 2.0 + PKCE Flow

```yaml
flow_overview:
  1: Generate PKCE code_verifier and code_challenge
  2: Redirect user to Shopify authorization URL
  3: User logs in and approves requested scopes
  4: Receive authorization code via callback
  5: Exchange code + code_verifier for tokens
  6: Use access_token for API calls
  7: Use refresh_token to get new access_token
```

### Configuration

```python
AUTH_CONFIG = {
    "auth_type": "CustomerAccountOAuth",
    "credentials": {
        "access_token": "<customer-access-token>",  # From OAuth flow
        "refresh_token": "<refresh-token>",          # For token refresh
        "shop_url": "<store>.myshopify.com",
        "client_id": "<oauth-client-id>"
    }
}
```

---

## CREDENTIAL_ACQUISITION

### 1. Enable Customer Accounts
```yaml
location: Shopify Admin > Settings > Customer accounts
steps:
  1: Select "New customer accounts"
  2: Configure login methods
  3: Save changes
```

### 2. Configure OAuth Client
```yaml
location: Shopify Admin > Settings > Apps and sales channels
steps:
  1: Create or use existing Headless/Hydrogen channel
  2: Go to Customer Account API settings
  3: Add redirect URIs for your application
  4: Copy Client ID
```

### 3. Implement OAuth Flow
```yaml
your_application:
  1: Generate PKCE values
  2: Build authorization URL
  3: Redirect user to Shopify
  4: Handle callback with code
  5: Exchange for tokens
  6: Store tokens securely
```

---

## API_ENDPOINT_STRUCTURE

```yaml
authorization:
  url: https://{shop}.myshopify.com/account/authorize
  method: GET (redirect)

token_exchange:
  url: https://{shop}.myshopify.com/account/oauth/token
  method: POST

graphql_api:
  url: https://{shop}.myshopify.com/account/customer/api/{version}/graphql
  method: POST
  version: "2024-10"
```

---

## KEY_DIFFERENCES

### vs Admin API
```yaml
admin_api:
  - Store-wide access
  - All customers' data
  - Server-side only
  - Admin credentials

customer_account_api:
  - Single customer access
  - Own data only
  - Client-safe (with PKCE)
  - Customer OAuth
```

### vs Storefront API
```yaml
storefront_api:
  - Anonymous + authenticated
  - Shopping operations
  - Simple token auth
  - Products, cart, checkout

customer_account_api:
  - Authenticated only
  - Account management
  - Full OAuth flow
  - Profile, orders, addresses
```

---

## COMMON_USE_CASES

### Customer Portal
```yaml
features:
  - View/edit profile
  - Manage addresses
  - View order history
  - Track shipments
  - Manage subscriptions
```

### Mobile App
```yaml
features:
  - Native login flow
  - Stored refresh tokens
  - Profile management
  - Order tracking
```

### Headless Commerce
```yaml
features:
  - Custom account pages
  - Self-service features
  - Subscription management
  - B2B company access
```

---

## IMPLEMENTATION_NOTES

### Token Storage
```yaml
access_token:
  storage: Memory/session
  lifetime: ~1 hour
  refresh: Before expiry

refresh_token:
  storage: Encrypted database
  lifetime: ~30 days
  rotate: On each use
```

### Error Handling
```yaml
common_errors:
  - 401: Token expired (refresh needed)
  - 403: Insufficient scope
  - 429: Rate limited

retry_strategy:
  token_expired: Refresh and retry once
  rate_limited: Exponential backoff
```

### Security Best Practices
```yaml
pkce:
  - Generate new code_verifier per auth
  - Never expose code_verifier to client

state:
  - Random value per request
  - Verify on callback

tokens:
  - Store refresh_token encrypted
  - Clear on logout
  - Validate id_token claims
```

---

## TESTING_APPROACH

```yaml
development:
  1: Create test customer in dev store
  2: Complete OAuth flow manually
  3: Store tokens for testing
  4: Run integration tests

test_commands:
  safe: "python test_shopify_customer.py safe"     # Profile, addresses
  orders: "python test_shopify_customer.py orders" # Order history
  all: "python test_shopify_customer.py all"       # All tests
```

---

## RELATED_DOCUMENTATION

- [SCOPES.md](./SCOPES.md) - Detailed scope reference
- [OAUTH_PKCE.md](./OAUTH_PKCE.md) - OAuth implementation guide
- [SANDBOX_TESTING.md](./SANDBOX_TESTING.md) - Testing guide
