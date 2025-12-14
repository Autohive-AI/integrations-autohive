---
api: shopify-customer-account
version: 2024-10
last_updated: 2025-01
type: scope-reference
format: llm-optimized
---

# Shopify Customer Account API Scopes

## OVERVIEW

The Customer Account API uses customer-specific scopes (prefixed with `customer_`) that define what a logged-in customer can access about their own data.

```yaml
api_type: GraphQL only
auth_method: OAuth 2.0 + PKCE
endpoint: https://{shop}.myshopify.com/account/customer/api/{version}/graphql
token_type: Customer access token (from OAuth flow)
```

---

## SCOPE_REGISTRY

### CUSTOMER_PROFILE

```yaml
- scope: customer_read_customers
  access: read
  resource: customer_profile
  description: Read customer's own profile information
  required_for:
    - customer_get_profile
  fields_accessible:
    - id
    - email
    - firstName
    - lastName
    - phone
    - acceptsMarketing
    - createdAt
    - defaultAddress

- scope: customer_write_customers
  access: write
  resource: customer_profile
  description: Update customer's own profile information
  required_for:
    - customer_update_profile
  depends_on: [customer_read_customers]
```

### ADDRESSES

```yaml
- scope: customer_read_customers
  access: read
  resource: addresses
  description: Read customer's saved addresses
  required_for:
    - customer_list_addresses
    - customer_get_address
  note: Addresses are part of customer profile scope

- scope: customer_write_customers
  access: write
  resource: addresses
  description: Manage customer's addresses
  required_for:
    - customer_create_address
    - customer_update_address
    - customer_delete_address
    - customer_set_default_address
  depends_on: [customer_read_customers]
```

### ORDERS

```yaml
- scope: customer_read_orders
  access: read
  resource: orders
  description: Read customer's own order history
  required_for:
    - customer_list_orders
    - customer_get_order
  fields_accessible:
    - id
    - orderNumber
    - processedAt
    - totalPrice
    - fulfillmentStatus
    - financialStatus
    - lineItems
    - shippingAddress
    - billingAddress

- scope: customer_write_orders
  access: write
  resource: orders
  description: Limited write access to customer's orders
  required_for:
    - customer_cancel_order (if store allows)
  note: Most order modifications require Admin API
```

### DRAFT_ORDERS

```yaml
- scope: customer_read_draft_orders
  access: read
  resource: draft_orders
  description: Read draft orders associated with customer
  required_for:
    - customer_list_draft_orders
  note: Typically used for B2B or quote workflows
```

### STORE_CREDIT

```yaml
- scope: customer_read_store_credit_accounts
  access: read
  resource: store_credit
  description: Read customer's store credit balance
  required_for:
    - customer_get_store_credit
  fields_accessible:
    - balance
    - currency
```

### MARKETS

```yaml
- scope: customer_read_markets
  access: read
  resource: markets
  description: Read market-specific information
  required_for:
    - customer_get_market_info
  note: Multi-market/international store support
```

### B2B_SCOPES

```yaml
- scope: customer_read_companies
  access: read
  resource: b2b_companies
  description: Read B2B company information
  required_for:
    - customer_get_company
    - customer_list_company_contacts
  note: Requires B2B features enabled

- scope: customer_write_companies
  access: write
  resource: b2b_companies
  description: Manage B2B company data
  required_for:
    - customer_update_company
  depends_on: [customer_read_companies]

- scope: customer_read_locations
  access: read
  resource: b2b_locations
  description: Read B2B company locations
  required_for:
    - customer_list_company_locations
  note: Requires B2B features enabled

- scope: customer_write_locations
  access: write
  resource: b2b_locations
  description: Manage B2B company locations
  depends_on: [customer_read_locations]
```

---

## SCOPE_CATEGORIES

### Standard Customer Scopes
```yaml
basic:
  - customer_read_customers
  - customer_write_customers

orders:
  - customer_read_orders
  - customer_write_orders
```

### Extended Scopes
```yaml
financial:
  - customer_read_store_credit_accounts
  - customer_read_draft_orders

international:
  - customer_read_markets

b2b:
  - customer_read_companies
  - customer_write_companies
  - customer_read_locations
  - customer_write_locations
```

---

## SCOPE_BY_ACTION

| Action | Required Scopes |
|--------|-----------------|
| customer_get_profile | customer_read_customers |
| customer_update_profile | customer_write_customers |
| customer_list_addresses | customer_read_customers |
| customer_create_address | customer_write_customers |
| customer_update_address | customer_write_customers |
| customer_delete_address | customer_write_customers |
| customer_list_orders | customer_read_orders |
| customer_get_order | customer_read_orders |
| customer_get_store_credit | customer_read_store_credit_accounts |

---

## AUTHENTICATION_FLOW

### OAuth 2.0 + PKCE

```yaml
flow_type: Authorization Code with PKCE
why_pkce: Public clients (mobile/SPA) cannot store secrets securely

steps:
  1_generate_pkce:
    code_verifier: Random 43-128 character string
    code_challenge: SHA256(code_verifier) base64url encoded

  2_authorization_request:
    endpoint: https://{shop}.myshopify.com/account/authorize
    params:
      - client_id
      - redirect_uri
      - response_type: code
      - scope: requested_scopes
      - state: random_csrf_token
      - code_challenge
      - code_challenge_method: S256

  3_user_authorization:
    action: User logs in and approves scopes

  4_callback:
    receives: authorization_code

  5_token_exchange:
    endpoint: https://{shop}.myshopify.com/account/oauth/token
    params:
      - client_id
      - code: authorization_code
      - redirect_uri
      - code_verifier
      - grant_type: authorization_code

  6_receive_tokens:
    - access_token (short-lived)
    - refresh_token (long-lived)
    - id_token (OpenID Connect)
```

### Token Management

```yaml
access_token:
  lifetime: ~1 hour
  storage: Memory/secure session
  refresh: Use refresh_token

refresh_token:
  lifetime: ~30 days
  storage: Secure persistent storage
  rotation: New refresh_token on use

id_token:
  format: JWT
  contains: customer_id, email, shop
  verify: Check signature and claims
```

---

## IMPLEMENTATION_PATTERNS

### PKCE Generation (Python)
```python
import secrets
import hashlib
import base64

def generate_pkce():
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge
```

### Authorization URL
```python
def build_auth_url(shop, client_id, redirect_uri, scopes, state, code_challenge):
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(scopes),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    return f"https://{shop}/account/authorize?" + urlencode(params)
```

### Token Exchange
```python
async def exchange_code(shop, client_id, code, redirect_uri, code_verifier):
    url = f"https://{shop}/account/oauth/token"
    data = {
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }
    response = await http_post(url, data=data)
    return response.json()
```

### GraphQL Request
```python
async def customer_api_request(shop, access_token, query, variables=None):
    url = f"https://{shop}/account/customer/api/2024-10/graphql"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    response = await http_post(url, json=payload, headers=headers)
    return response.json()
```

---

## COMMON_QUERIES

### Get Customer Profile
```graphql
query GetCustomerProfile {
  customer {
    id
    email
    firstName
    lastName
    phone
    acceptsMarketing
    createdAt
    defaultAddress {
      id
      address1
      city
      province
      country
      zip
    }
  }
}
```

### List Orders
```graphql
query ListOrders($first: Int!) {
  customer {
    orders(first: $first) {
      edges {
        node {
          id
          orderNumber
          processedAt
          totalPrice {
            amount
            currencyCode
          }
          fulfillmentStatus
          financialStatus
        }
      }
    }
  }
}
```

---

## RATE_LIMITS

```yaml
type: cost-based
bucket_size: 1000 points
restore_rate: 50 points/second
per_customer: Each customer has own bucket
headers:
  - X-Shopify-API-Call-Limit: current/max
```

---

## IMPORTANT_NOTES

```yaml
differences_from_storefront:
  - Requires OAuth authentication (not just access token)
  - Customer must actively consent to scopes
  - Scopes are customer-specific, not store-wide
  - Uses /account/ endpoint path

security_considerations:
  - Never store code_verifier server-side long-term
  - Validate state parameter to prevent CSRF
  - Store refresh_token securely (encrypted)
  - Validate id_token signature

store_requirements:
  - Customer accounts must be enabled
  - New customer accounts experience recommended
  - OAuth client must be configured in Shopify
```
