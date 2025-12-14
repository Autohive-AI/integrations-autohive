---
integration: shopify-storefront
display_name: Shopify Storefront API
api_type: storefront
auth_method: access_tokens
base_url: https://{shop}.myshopify.com/api/{version}/graphql.json
api_version: 2024-10
protocol: GraphQL only
status: production
---

# Shopify Storefront API Integration

## QUICK_REFERENCE

| Property | Value |
|----------|-------|
| **API Type** | GraphQL only |
| **Auth Method** | Public or Private Access Token |
| **Public Header** | `X-Shopify-Storefront-Access-Token` |
| **Private Header** | `Shopify-Storefront-Private-Token` |
| **Rate Limit** | Complexity-based |
| **API Version** | 2024-10 |
| **Endpoint** | `https://{shop}.myshopify.com/api/2024-10/graphql.json` |

---

## AUTHENTICATION

### Token Types
```yaml
public_token:
  header: X-Shopify-Storefront-Access-Token
  use: Client-side (browser, mobile apps)
  safe_to_expose: true

private_token:
  header: Shopify-Storefront-Private-Token
  use: Server-side only
  safe_to_expose: false
  additional: Shopify-Storefront-Buyer-IP (recommended)
```

### Credential Structure
```python
# Using public token
AUTH = {
    "auth_type": "StorefrontPublic",
    "credentials": {
        "public_token": "your-public-storefront-token",
        "shop_url": "your-store.myshopify.com"
    }
}

# Using private token
AUTH = {
    "auth_type": "StorefrontPrivate",
    "credentials": {
        "private_token": "shpat_xxxxx",
        "shop_url": "your-store.myshopify.com"
    }
}
```

### Header Pattern
```python
def build_headers(context) -> dict:
    credentials = context.auth.get('credentials', {})
    auth_type = context.auth.get('auth_type', '')

    if auth_type == "StorefrontPrivate":
        return {
            "Shopify-Storefront-Private-Token": credentials['private_token'],
            "Content-Type": "application/json"
        }
    else:
        return {
            "X-Shopify-Storefront-Access-Token": credentials['public_token'],
            "Content-Type": "application/json"
        }
```

---

## ACTIONS_INDEX

### Product Actions

| Action | Type | Scopes | Description |
|--------|------|--------|-------------|
| `storefront_get_product` | Query | unauthenticated_read_product_listings | Get product by handle or ID |
| `storefront_list_products` | Query | unauthenticated_read_product_listings | List products with filters |
| `storefront_search_products` | Query | unauthenticated_read_product_listings | Search products by keyword |
| `storefront_get_collection` | Query | unauthenticated_read_product_listings | Get collection details |
| `storefront_list_collections` | Query | unauthenticated_read_product_listings | List all collections |

### Cart Actions

| Action | Type | Scopes | Description |
|--------|------|--------|-------------|
| `storefront_create_cart` | Mutation | unauthenticated_write_checkouts | Create new shopping cart |
| `storefront_get_cart` | Query | unauthenticated_read_checkouts | Get cart contents |
| `storefront_add_to_cart` | Mutation | unauthenticated_write_checkouts | Add items to cart |
| `storefront_update_cart_line` | Mutation | unauthenticated_write_checkouts | Update line item quantity |
| `storefront_remove_from_cart` | Mutation | unauthenticated_write_checkouts | Remove items from cart |
| `storefront_apply_discount` | Mutation | unauthenticated_write_checkouts | Apply discount code |

### Customer Actions

| Action | Type | Scopes | Description |
|--------|------|--------|-------------|
| `storefront_create_customer` | Mutation | unauthenticated_write_customers | Create customer account |
| `storefront_customer_login` | Mutation | unauthenticated_write_customers | Get customer access token |
| `storefront_get_customer` | Query | unauthenticated_read_customers | Get customer profile |
| `storefront_update_customer` | Mutation | unauthenticated_write_customers | Update customer info |
| `storefront_recover_customer` | Mutation | unauthenticated_write_customers | Send password reset email |

---

## ACTION_DETAILS

### storefront_get_product

```yaml
action: storefront_get_product
type: GraphQL Query
scopes: [unauthenticated_read_product_listings]

inputs:
  handle:
    type: string
    description: Product handle (URL slug)
    required: false
    example: "classic-leather-jacket"

  product_id:
    type: string
    description: Product GID
    required: false
    example: "gid://shopify/Product/123456"

outputs:
  success:
    type: boolean

  product:
    type: object
    fields:
      - id
      - title
      - description
      - handle
      - availableForSale
      - priceRange
      - images
      - variants

graphql_query: |
  query GetProduct($handle: String, $id: ID) {
    product(handle: $handle, id: $id) {
      id
      title
      description
      handle
      availableForSale
      priceRange {
        minVariantPrice { amount currencyCode }
        maxVariantPrice { amount currencyCode }
      }
      images(first: 10) {
        edges { node { url altText width height } }
      }
      variants(first: 50) {
        edges {
          node {
            id title price { amount currencyCode }
            availableForSale quantityAvailable
            selectedOptions { name value }
          }
        }
      }
    }
  }
```

### storefront_create_cart

```yaml
action: storefront_create_cart
type: GraphQL Mutation
scopes: [unauthenticated_write_checkouts]

inputs:
  lines:
    type: array
    description: Initial cart line items
    required: false
    items:
      merchandiseId:
        type: string
        description: Product variant GID
      quantity:
        type: integer
        description: Quantity to add

  buyer_identity:
    type: object
    description: Customer information
    required: false
    properties:
      email: string
      countryCode: string

outputs:
  success:
    type: boolean

  cart:
    type: object
    fields:
      - id
      - checkoutUrl
      - totalQuantity
      - lines
      - cost

graphql_mutation: |
  mutation CreateCart($input: CartInput!) {
    cartCreate(input: $input) {
      cart {
        id
        checkoutUrl
        totalQuantity
        lines(first: 50) {
          edges {
            node {
              id quantity
              merchandise { ... on ProductVariant { id title } }
              cost { totalAmount { amount currencyCode } }
            }
          }
        }
        cost {
          totalAmount { amount currencyCode }
          subtotalAmount { amount currencyCode }
          totalTaxAmount { amount currencyCode }
        }
      }
      userErrors { field message }
    }
  }
```

### storefront_customer_login

```yaml
action: storefront_customer_login
type: GraphQL Mutation
scopes: [unauthenticated_write_customers]

inputs:
  email:
    type: string
    format: email
    description: Customer email
    required: true

  password:
    type: string
    description: Customer password
    required: true

outputs:
  success:
    type: boolean

  customer_access_token:
    type: string
    description: Token for authenticated customer requests

  expires_at:
    type: string
    format: ISO 8601
    description: Token expiration time

graphql_mutation: |
  mutation CustomerLogin($input: CustomerAccessTokenCreateInput!) {
    customerAccessTokenCreate(input: $input) {
      customerAccessToken {
        accessToken
        expiresAt
      }
      customerUserErrors {
        field
        message
        code
      }
    }
  }
```

---

## REQUIRED_SCOPES

### Minimum (Product Browsing)
```yaml
scopes:
  - unauthenticated_read_product_listings
purpose: Display products to customers
```

### E-commerce (Cart + Checkout)
```yaml
scopes:
  - unauthenticated_read_product_listings
  - unauthenticated_read_product_inventory
  - unauthenticated_read_checkouts
  - unauthenticated_write_checkouts
purpose: Full shopping experience
```

### Full Storefront
```yaml
scopes:
  - unauthenticated_read_product_listings
  - unauthenticated_read_product_inventory
  - unauthenticated_read_checkouts
  - unauthenticated_write_checkouts
  - unauthenticated_read_customers
  - unauthenticated_write_customers
  - unauthenticated_read_content
purpose: Complete storefront with customer accounts
```

---

## GRAPHQL_PATTERNS

### Query Structure
```graphql
query QueryName($variable: Type!) {
  resource(argument: $variable) {
    field1
    field2
    nestedResource {
      nestedField
    }
    connection(first: 10) {
      edges {
        node {
          id
          ...fields
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
```

### Mutation Structure
```graphql
mutation MutationName($input: InputType!) {
  mutationName(input: $input) {
    resultObject {
      id
      ...fields
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Pagination Pattern
```python
async def paginated_query(context, query, variables, connection_path):
    """Fetch all pages of a connection."""
    all_items = []
    has_next = True
    cursor = None

    while has_next:
        vars = {**variables}
        if cursor:
            vars['after'] = cursor

        result = await execute_query(context, query, vars)

        # Extract connection from result using path
        connection = get_nested(result, connection_path)
        edges = connection.get('edges', [])
        page_info = connection.get('pageInfo', {})

        all_items.extend([edge['node'] for edge in edges])
        has_next = page_info.get('hasNextPage', False)
        cursor = page_info.get('endCursor')

    return all_items
```

---

## ERROR_HANDLING

### GraphQL Errors
```yaml
location: response.errors
structure:
  - message: Error description
  - locations: Where in query
  - path: Field path

example:
  errors:
    - message: "Product not found"
      locations: [{ line: 2, column: 3 }]
      path: ["product"]
```

### User Errors (Mutations)
```yaml
location: response.data.mutationName.userErrors
structure:
  - field: Input field causing error
  - message: Human-readable message
  - code: Error code

example:
  userErrors:
    - field: ["input", "email"]
      message: "Email has already been taken"
      code: "TAKEN"
```

### Error Handling Pattern
```python
async def execute_mutation(context, mutation, variables):
    result = await execute_query(context, mutation, variables)

    # Check for GraphQL errors
    if 'errors' in result:
        return error_response(result['errors'][0]['message'])

    # Check for user errors in mutation
    data = result.get('data', {})
    mutation_result = list(data.values())[0] if data else {}

    user_errors = mutation_result.get('userErrors', [])
    if user_errors:
        return error_response(user_errors[0]['message'])

    return success_response(**mutation_result)
```

---

## TESTING

### Run Tests
```bash
cd shopify-storefront/tests
python test_shopify_storefront.py safe    # Product queries
python test_shopify_storefront.py cart    # Cart operations
python test_shopify_storefront.py all     # All tests
```

### Test Categories
```yaml
safe:
  - storefront_list_products
  - storefront_get_product
  - storefront_list_collections
  risk: None (read-only)

cart:
  - storefront_create_cart
  - storefront_add_to_cart
  - storefront_update_cart_line
  risk: Creates cart (no purchase)

customer:
  - storefront_create_customer
  - storefront_customer_login
  risk: Creates test accounts
```

---

## RELATED_DOCUMENTATION

```yaml
scopes: ./SCOPES.md
graphql_queries: ./GRAPHQL_QUERIES.md
testing: ./SANDBOX_TESTING.md
master_guide: ../../docs/SHOPIFY_MASTER_GUIDE.md
official_docs: https://shopify.dev/docs/api/storefront
```
