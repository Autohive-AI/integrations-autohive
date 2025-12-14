---
api: shopify-storefront
api_type: Storefront API
version: 2024-10
last_updated: 2025-01
type: scope-reference
format: llm-optimized
---

# Shopify Storefront API Scopes

## SCOPE_FORMAT

```yaml
pattern: "unauthenticated_{action}_{resource}"
actions:
  - read: Retrieve data
  - write: Create or modify data
example: unauthenticated_read_product_listings
note: All Storefront API scopes are prefixed with "unauthenticated_"
```

---

## SCOPE_REGISTRY

### PRODUCTS

```yaml
- scope: unauthenticated_read_product_listings
  access: read
  resource: products
  description: Browse products, variants, collections, and catalog data
  graphql_queries:
    - product(id, handle)
    - products(first, query, sortKey)
    - productByHandle(handle)
    - collection(id, handle)
    - collections(first)
  required_for_actions:
    - storefront_get_product
    - storefront_list_products
    - storefront_search_products
    - storefront_get_collection
    - storefront_list_collections
  data_accessible:
    - Product title, description, images
    - Variant pricing and availability
    - Collection information
    - Product tags and types

- scope: unauthenticated_read_product_inventory
  access: read
  resource: inventory
  description: Check product availability and inventory quantities
  graphql_queries:
    - product.availableForSale
    - productVariant.availableForSale
    - productVariant.quantityAvailable
  required_for_actions:
    - storefront_check_availability
  use_case: Display stock status to customers

- scope: unauthenticated_read_product_tags
  access: read
  resource: product_tags
  description: Access product tag data for filtering
  graphql_queries:
    - product.tags
    - productTags(first)
  use_case: Build tag-based navigation and filters

- scope: unauthenticated_read_product_pickup_locations
  access: read
  resource: pickup_locations
  description: Find products available at physical store locations
  graphql_queries:
    - product.storeAvailability
  use_case: Buy online, pick up in store (BOPIS)
```

### CART & CHECKOUT

```yaml
- scope: unauthenticated_read_checkouts
  access: read
  resource: checkouts
  description: Read shopping cart and checkout data
  graphql_queries:
    - cart(id)
    - checkout(id) # Legacy
  required_for_actions:
    - storefront_get_cart
    - storefront_get_checkout

- scope: unauthenticated_write_checkouts
  access: write
  resource: checkouts
  description: Create and modify shopping carts and checkouts
  graphql_mutations:
    - cartCreate
    - cartLinesAdd
    - cartLinesUpdate
    - cartLinesRemove
    - cartBuyerIdentityUpdate
    - cartDiscountCodesUpdate
    - checkoutCreate # Legacy
    - checkoutLineItemsAdd # Legacy
  required_for_actions:
    - storefront_create_cart
    - storefront_add_to_cart
    - storefront_update_cart
    - storefront_remove_from_cart
    - storefront_apply_discount
  depends_on:
    - unauthenticated_read_checkouts
```

### CUSTOMERS

```yaml
- scope: unauthenticated_read_customers
  access: read
  resource: customers
  description: Read customer data (requires customer access token)
  graphql_queries:
    - customer(customerAccessToken)
    - customer.orders
    - customer.addresses
  required_for_actions:
    - storefront_get_customer
  note: Requires customerAccessToken from login

- scope: unauthenticated_write_customers
  access: write
  resource: customers
  description: Create customer accounts and update profiles
  graphql_mutations:
    - customerCreate
    - customerAccessTokenCreate
    - customerAccessTokenRenew
    - customerUpdate
    - customerAddressCreate
    - customerAddressUpdate
    - customerAddressDelete
    - customerRecover
    - customerReset
  required_for_actions:
    - storefront_create_customer
    - storefront_customer_login
    - storefront_update_customer
    - storefront_create_address
  depends_on:
    - unauthenticated_read_customers

- scope: unauthenticated_read_customer_tags
  access: read
  resource: customer_tags
  description: Access customer tag data
  graphql_queries:
    - customer.tags
  use_case: Personalization based on customer segments
```

### CONTENT

```yaml
- scope: unauthenticated_read_content
  access: read
  resource: content
  description: Read blog articles, pages, and store content
  graphql_queries:
    - article(id, handle)
    - articles(first)
    - blog(id, handle)
    - blogs(first)
    - page(id, handle)
    - pages(first)
  required_for_actions:
    - storefront_get_article
    - storefront_list_articles
    - storefront_get_page
  use_case: Display blog and CMS content
```

### SELLING PLANS & SUBSCRIPTIONS

```yaml
- scope: unauthenticated_read_selling_plans
  access: read
  resource: selling_plans
  description: Access subscription and selling plan information
  graphql_queries:
    - product.sellingPlanGroups
    - sellingPlanGroup(id)
  required_for_actions:
    - storefront_get_selling_plans
  use_case: Display subscription options to customers
```

### METAOBJECTS

```yaml
- scope: unauthenticated_read_metaobjects
  access: read
  resource: metaobjects
  description: Access custom metaobject data
  graphql_queries:
    - metaobject(id, handle)
    - metaobjects(type, first)
  use_case: Custom content and data structures
```

---

## TOKEN_TYPES

### Public Access Token
```yaml
header: X-Shopify-Storefront-Access-Token
use_case: Client-side applications (browser, mobile)
security: Safe to expose in client code
rate_limit: Per customer IP address
example_header: "X-Shopify-Storefront-Access-Token: your-public-token"
```

### Private Access Token
```yaml
header: Shopify-Storefront-Private-Token
use_case: Server-side applications only
security: Must be kept secret
rate_limit: Per app
additional_header: "Shopify-Storefront-Buyer-IP: customer-ip" (recommended)
example_header: "Shopify-Storefront-Private-Token: shpat_xxxxx"
```

---

## RATE_LIMITS

```yaml
type: complexity-based

tokenless_requests:
  limit: 1000 complexity points per query
  use_case: Basic product browsing

public_token_requests:
  limit: Higher complexity allowed
  rate: Per customer IP

private_token_requests:
  limit: Highest complexity
  rate: Per app
  recommended_header: Include buyer IP for accurate rate limiting

complexity_calculation:
  - Each field adds to complexity
  - Nested connections multiply complexity
  - Use query complexity analyzer to optimize
```

---

## GRAPHQL_ENDPOINT

```yaml
endpoint: https://{shop}.myshopify.com/api/{version}/graphql.json
method: POST
content_type: application/json

versions:
  current: "2024-10"
  supported:
    - "2024-10"
    - "2024-07"
    - "2024-04"
    - "2024-01"

request_format:
  query: "GraphQL query string"
  variables: { optional variables object }
```

---

## IMPLEMENTATION_PATTERNS

### Header Patterns
```python
# Public token (client-side safe)
def storefront_public_headers(public_token: str) -> dict:
    return {
        "X-Shopify-Storefront-Access-Token": public_token,
        "Content-Type": "application/json"
    }

# Private token (server-side only)
def storefront_private_headers(private_token: str, buyer_ip: str = None) -> dict:
    headers = {
        "Shopify-Storefront-Private-Token": private_token,
        "Content-Type": "application/json"
    }
    if buyer_ip:
        headers["Shopify-Storefront-Buyer-IP"] = buyer_ip
    return headers
```

### URL Pattern
```python
API_VERSION = "2024-10"

def get_storefront_url(shop_url: str) -> str:
    return f"https://{shop_url}/api/{API_VERSION}/graphql.json"
```

### GraphQL Query Execution
```python
async def execute_storefront_query(context, query: str, variables: dict = None):
    url = get_storefront_url(context)
    headers = get_storefront_headers(context)

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = await context.fetch(url, method="POST", json=payload, headers=headers)

    if "errors" in response:
        raise Exception(f"GraphQL Error: {response['errors']}")

    return response.get("data", {})
```

---

## COMMON_QUERIES

### Product Query
```graphql
query GetProduct($handle: String!) {
  product(handle: $handle) {
    id
    title
    description
    handle
    availableForSale
    priceRange {
      minVariantPrice { amount currencyCode }
      maxVariantPrice { amount currencyCode }
    }
    images(first: 5) {
      edges {
        node { url altText }
      }
    }
    variants(first: 10) {
      edges {
        node {
          id
          title
          price { amount currencyCode }
          availableForSale
          quantityAvailable
        }
      }
    }
  }
}
```

### Cart Operations
```graphql
# Create Cart
mutation CreateCart($input: CartInput!) {
  cartCreate(input: $input) {
    cart {
      id
      checkoutUrl
      lines(first: 10) {
        edges {
          node {
            id
            quantity
            merchandise { ... on ProductVariant { id title } }
          }
        }
      }
    }
    userErrors { field message }
  }
}

# Add to Cart
mutation AddToCart($cartId: ID!, $lines: [CartLineInput!]!) {
  cartLinesAdd(cartId: $cartId, lines: $lines) {
    cart { id totalQuantity }
    userErrors { field message }
  }
}
```

### Customer Login
```graphql
mutation CustomerLogin($email: String!, $password: String!) {
  customerAccessTokenCreate(input: { email: $email, password: $password }) {
    customerAccessToken {
      accessToken
      expiresAt
    }
    customerUserErrors { field message }
  }
}
```

---

## BEST_PRACTICES

```yaml
performance:
  - Request only needed fields to reduce complexity
  - Use pagination (first/last, after/before)
  - Cache product data when possible
  - Combine related queries when practical

security:
  - Use private tokens for server-side operations
  - Never expose private tokens in client code
  - Include buyer IP header for accurate rate limiting
  - Validate cart operations server-side

error_handling:
  - Check for userErrors in mutation responses
  - GraphQL returns 200 even for errors
  - Handle network errors and retries
  - Log query complexity for optimization
```
