---
api: shopify-storefront
type: graphql-templates
format: llm-optimized
---

# Shopify Storefront API GraphQL Queries

## PRODUCT_QUERIES

### Get Product by Handle
```graphql
query GetProductByHandle($handle: String!) {
  product(handle: $handle) {
    id
    title
    description
    descriptionHtml
    handle
    availableForSale
    productType
    vendor
    tags
    priceRange {
      minVariantPrice {
        amount
        currencyCode
      }
      maxVariantPrice {
        amount
        currencyCode
      }
    }
    images(first: 10) {
      edges {
        node {
          id
          url
          altText
          width
          height
        }
      }
    }
    variants(first: 100) {
      edges {
        node {
          id
          title
          availableForSale
          quantityAvailable
          price {
            amount
            currencyCode
          }
          compareAtPrice {
            amount
            currencyCode
          }
          selectedOptions {
            name
            value
          }
          image {
            url
            altText
          }
        }
      }
    }
    options {
      id
      name
      values
    }
  }
}
```

### List Products
```graphql
query ListProducts($first: Int!, $after: String, $query: String, $sortKey: ProductSortKeys, $reverse: Boolean) {
  products(first: $first, after: $after, query: $query, sortKey: $sortKey, reverse: $reverse) {
    edges {
      cursor
      node {
        id
        title
        handle
        availableForSale
        productType
        vendor
        priceRange {
          minVariantPrice {
            amount
            currencyCode
          }
        }
        images(first: 1) {
          edges {
            node {
              url
              altText
            }
          }
        }
        variants(first: 1) {
          edges {
            node {
              id
              price {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

### Search Products
```graphql
query SearchProducts($query: String!, $first: Int!) {
  search(query: $query, first: $first, types: [PRODUCT]) {
    edges {
      node {
        ... on Product {
          id
          title
          handle
          description
          availableForSale
          priceRange {
            minVariantPrice {
              amount
              currencyCode
            }
          }
          images(first: 1) {
            edges {
              node {
                url
                altText
              }
            }
          }
        }
      }
    }
    totalCount
  }
}
```

---

## COLLECTION_QUERIES

### Get Collection
```graphql
query GetCollection($handle: String!, $first: Int!) {
  collection(handle: $handle) {
    id
    title
    description
    handle
    image {
      url
      altText
    }
    products(first: $first) {
      edges {
        node {
          id
          title
          handle
          availableForSale
          priceRange {
            minVariantPrice {
              amount
              currencyCode
            }
          }
          images(first: 1) {
            edges {
              node {
                url
                altText
              }
            }
          }
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

### List Collections
```graphql
query ListCollections($first: Int!, $after: String) {
  collections(first: $first, after: $after) {
    edges {
      node {
        id
        title
        handle
        description
        image {
          url
          altText
        }
        productsCount: products(first: 0) {
          edges {
            node {
              id
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

---

## CART_MUTATIONS

### Create Cart
```graphql
mutation CartCreate($input: CartInput!) {
  cartCreate(input: $input) {
    cart {
      id
      checkoutUrl
      totalQuantity
      createdAt
      updatedAt
      lines(first: 100) {
        edges {
          node {
            id
            quantity
            merchandise {
              ... on ProductVariant {
                id
                title
                product {
                  title
                  handle
                }
                price {
                  amount
                  currencyCode
                }
                image {
                  url
                  altText
                }
              }
            }
            cost {
              totalAmount {
                amount
                currencyCode
              }
            }
          }
        }
      }
      cost {
        totalAmount {
          amount
          currencyCode
        }
        subtotalAmount {
          amount
          currencyCode
        }
        totalTaxAmount {
          amount
          currencyCode
        }
      }
      buyerIdentity {
        email
        countryCode
      }
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Get Cart
```graphql
query GetCart($cartId: ID!) {
  cart(id: $cartId) {
    id
    checkoutUrl
    totalQuantity
    createdAt
    updatedAt
    lines(first: 100) {
      edges {
        node {
          id
          quantity
          merchandise {
            ... on ProductVariant {
              id
              title
              product {
                title
                handle
              }
              price {
                amount
                currencyCode
              }
            }
          }
          cost {
            totalAmount {
              amount
              currencyCode
            }
          }
        }
      }
    }
    cost {
      totalAmount {
        amount
        currencyCode
      }
      subtotalAmount {
        amount
        currencyCode
      }
      totalTaxAmount {
        amount
        currencyCode
      }
    }
    discountCodes {
      code
      applicable
    }
  }
}
```

### Add Lines to Cart
```graphql
mutation CartLinesAdd($cartId: ID!, $lines: [CartLineInput!]!) {
  cartLinesAdd(cartId: $cartId, lines: $lines) {
    cart {
      id
      totalQuantity
      lines(first: 100) {
        edges {
          node {
            id
            quantity
            merchandise {
              ... on ProductVariant {
                id
                title
              }
            }
          }
        }
      }
      cost {
        totalAmount {
          amount
          currencyCode
        }
      }
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Update Cart Lines
```graphql
mutation CartLinesUpdate($cartId: ID!, $lines: [CartLineUpdateInput!]!) {
  cartLinesUpdate(cartId: $cartId, lines: $lines) {
    cart {
      id
      totalQuantity
      lines(first: 100) {
        edges {
          node {
            id
            quantity
          }
        }
      }
      cost {
        totalAmount {
          amount
          currencyCode
        }
      }
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Remove Cart Lines
```graphql
mutation CartLinesRemove($cartId: ID!, $lineIds: [ID!]!) {
  cartLinesRemove(cartId: $cartId, lineIds: $lineIds) {
    cart {
      id
      totalQuantity
      lines(first: 100) {
        edges {
          node {
            id
            quantity
          }
        }
      }
      cost {
        totalAmount {
          amount
          currencyCode
        }
      }
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

### Apply Discount Code
```graphql
mutation CartDiscountCodesUpdate($cartId: ID!, $discountCodes: [String!]!) {
  cartDiscountCodesUpdate(cartId: $cartId, discountCodes: $discountCodes) {
    cart {
      id
      discountCodes {
        code
        applicable
      }
      cost {
        totalAmount {
          amount
          currencyCode
        }
      }
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

---

## CUSTOMER_MUTATIONS

### Create Customer
```graphql
mutation CustomerCreate($input: CustomerCreateInput!) {
  customerCreate(input: $input) {
    customer {
      id
      email
      firstName
      lastName
      phone
      acceptsMarketing
    }
    customerUserErrors {
      field
      message
      code
    }
  }
}
```

### Customer Login (Get Access Token)
```graphql
mutation CustomerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) {
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

### Get Customer (Authenticated)
```graphql
query GetCustomer($customerAccessToken: String!) {
  customer(customerAccessToken: $customerAccessToken) {
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
      address2
      city
      province
      country
      zip
      phone
    }
    addresses(first: 10) {
      edges {
        node {
          id
          address1
          address2
          city
          province
          country
          zip
        }
      }
    }
    orders(first: 10) {
      edges {
        node {
          id
          orderNumber
          totalPrice {
            amount
            currencyCode
          }
          processedAt
          fulfillmentStatus
          financialStatus
        }
      }
    }
  }
}
```

### Update Customer
```graphql
mutation CustomerUpdate($customerAccessToken: String!, $customer: CustomerUpdateInput!) {
  customerUpdate(customerAccessToken: $customerAccessToken, customer: $customer) {
    customer {
      id
      email
      firstName
      lastName
      phone
    }
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

### Customer Password Recover
```graphql
mutation CustomerRecover($email: String!) {
  customerRecover(email: $email) {
    customerUserErrors {
      field
      message
      code
    }
  }
}
```

### Create Customer Address
```graphql
mutation CustomerAddressCreate($customerAccessToken: String!, $address: MailingAddressInput!) {
  customerAddressCreate(customerAccessToken: $customerAccessToken, address: $address) {
    customerAddress {
      id
      address1
      address2
      city
      province
      country
      zip
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

## VARIABLE_EXAMPLES

### CartInput
```json
{
  "input": {
    "lines": [
      {
        "merchandiseId": "gid://shopify/ProductVariant/12345",
        "quantity": 2
      }
    ],
    "buyerIdentity": {
      "email": "customer@example.com",
      "countryCode": "US"
    }
  }
}
```

### CartLineInput
```json
{
  "cartId": "gid://shopify/Cart/abc123",
  "lines": [
    {
      "merchandiseId": "gid://shopify/ProductVariant/12345",
      "quantity": 1
    }
  ]
}
```

### CustomerCreateInput
```json
{
  "input": {
    "email": "customer@example.com",
    "password": "securepassword123",
    "firstName": "John",
    "lastName": "Doe",
    "acceptsMarketing": true
  }
}
```

### CustomerAccessTokenCreateInput
```json
{
  "input": {
    "email": "customer@example.com",
    "password": "securepassword123"
  }
}
```

---

## SORT_KEYS

### ProductSortKeys
```yaml
values:
  - TITLE
  - PRODUCT_TYPE
  - VENDOR
  - UPDATED_AT
  - CREATED_AT
  - BEST_SELLING
  - PRICE
  - ID
  - RELEVANCE
default: RELEVANCE
```

### CollectionSortKeys
```yaml
values:
  - TITLE
  - UPDATED_AT
  - ID
  - RELEVANCE
default: RELEVANCE
```

---

## PAGINATION_PATTERN

```python
# Variables for pagination
variables = {
    "first": 50,           # Items per page
    "after": None,         # Cursor for next page
    "query": "tag:featured" # Optional filter
}

# After first request, use endCursor for next page
variables["after"] = result["pageInfo"]["endCursor"]
```
