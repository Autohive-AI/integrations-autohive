# Shopify Admin Integration for Autohive

Connects Autohive to the Shopify Admin API for backend store management, currently focusing on Customer operations.

## Description

This integration provides access to the Shopify Admin API (GraphQL), allowing you to automate customer management tasks such as searching, creating, updating, and deleting customer records.

## Setup & Authentication

This integration uses **Platform Authentication** with Shopify (Admin API).

**Scopes Required:**
- `read_customers`
- `write_customers`

## Actions

### Customer Actions

#### `admin_list_customers`
List customers from the store with pagination and filtering.

**Inputs:**
- `first` (integer, optional): Number of customers to return (default: 20)
- `after` (string, optional): Pagination cursor
- `query` (string, optional): Search query (e.g., `email:bob@example.com` or `country:US`)

**Outputs:**
- `customers` (array): List of customers
- `count` (integer): Number of customers returned
- `has_next_page` (boolean): Whether there are more pages
- `end_cursor` (string): Cursor for the next page
- `success` (boolean)

---

#### `admin_get_customer`
Get a customer by their GraphQL ID.

**Inputs:**
- `id` (string, required): Customer GraphQL ID (e.g., `gid://shopify/Customer/123456789`)

**Outputs:**
- `customer` (object): Customer details
- `success` (boolean)

---

#### `admin_create_customer`
Create a new customer profile.

**Inputs:**
- `email` (string, required): Customer email
- `first_name` (string, optional)
- `last_name` (string, optional)
- `phone` (string, optional)
- `verified` (boolean, optional): Whether email is verified
- `addresses` (array, optional): List of address objects

**Outputs:**
- `customer` (object): Created customer details
- `success` (boolean)

---

#### `admin_update_customer`
Update an existing customer.

**Inputs:**
- `id` (string, required): Customer GraphQL ID
- `input` (object, required): Fields to update (e.g., `{ "firstName": "NewName", "note": "VIP" }`)

**Outputs:**
- `customer` (object): Updated customer details
- `success` (boolean)

---

#### `admin_delete_customer`
Permanently delete a customer.

**Inputs:**
- `id` (string, required): Customer GraphQL ID

**Outputs:**
- `deleted_id` (string): ID of the deleted customer
- `success` (boolean)

## Requirements

- `autohive-integrations-sdk`
- `aiohttp`

## Usage Examples

### Example 1: Find a Customer by Email
```python
result = await shopify_admin.execute_action("admin_list_customers", {
    "query": "email:alice@example.com",
    "first": 1
}, context)

if result.data["customers"]:
    customer = result.data["customers"][0]
    print(f"Found customer: {customer['firstName']} ({customer['id']})")
```

### Example 2: Update a Customer Note
```python
customer_id = "gid://shopify/Customer/123456789"

await shopify_admin.execute_action("admin_update_customer", {
    "id": customer_id,
    "input": {
        "note": "Updated via Autohive on " + str(date.today()),
        "tags": ["vip", "imported"]
    }
}, context)
```

## Testing

To run the tests:

1. Navigate to the integration's directory:
   ```bash
   cd shopify-admin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the tests:
   ```bash
   python -m pytest tests/
   ```
