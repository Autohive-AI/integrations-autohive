# Stripe Integration for Autohive

Connects Autohive to the Stripe API to manage customers, invoices, and invoice items for billing and payment processing.

## Description

This integration provides comprehensive access to Stripe's billing functionality, enabling automated invoice creation, customer management, and payment processing. Key features include:

- **Customer Management**: Create, update, list, and delete customers
- **Invoice Management**: Create draft invoices, finalize, send, pay, and void invoices
- **Invoice Items**: Add, update, and remove line items from invoices
- **RUC Billing Support**: Designed to support NZ Road User Charges invoice generation

## Setup & Authentication

This integration uses Stripe's Secret API Key for authentication.

### Getting Your API Key

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers** > **API Keys**
3. Copy your **Secret key** (starts with `sk_live_` for production or `sk_test_` for testing)
4. **Important**: Use test keys (`sk_test_`) during development to avoid real charges

**Authentication Fields:**

| Field | Description |
|-------|-------------|
| `api_key` | Your Stripe Secret API Key (starts with `sk_live_` or `sk_test_`) |

## Actions

### Customer Actions

#### `list_customers`
Retrieve a paginated list of customers from Stripe.

**Inputs:**
- `limit` (integer, optional): Number of customers to return (max: 100, default: 10)
- `starting_after` (string, optional): Cursor for pagination
- `email` (string, optional): Filter by customer email address
- `created_gte` (integer, optional): Filter by creation timestamp (Unix)

**Outputs:**
- `customers` (array): List of customer objects
- `has_more` (boolean): Whether there are more customers to fetch
- `result` (boolean): Success status

---

#### `get_customer`
Retrieve details of a specific customer by their ID.

**Inputs:**
- `customer_id` (string, required): The Stripe customer ID (starts with `cus_`)

**Outputs:**
- `customer` (object): Customer details
- `result` (boolean): Success status

---

#### `create_customer`
Create a new customer in Stripe.

**Inputs:**
- `email` (string, optional): Customer's email address
- `name` (string, optional): Customer's full name
- `description` (string, optional): Arbitrary description
- `phone` (string, optional): Customer's phone number
- `address` (object, optional): Customer's address (line1, line2, city, state, postal_code, country)
- `metadata` (object, optional): Key-value pairs for additional data

**Outputs:**
- `customer` (object): Created customer details
- `result` (boolean): Success status

---

#### `update_customer`
Update an existing customer's information.

**Inputs:**
- `customer_id` (string, required): The Stripe customer ID
- `email`, `name`, `description`, `phone`, `address`, `metadata` (optional): Fields to update

**Outputs:**
- `customer` (object): Updated customer details
- `result` (boolean): Success status

---

#### `delete_customer`
Permanently delete a customer from Stripe.

**Inputs:**
- `customer_id` (string, required): The Stripe customer ID to delete

**Outputs:**
- `id` (string): The deleted customer ID
- `deleted` (boolean): Whether the customer was deleted
- `result` (boolean): Success status

---

### Invoice Actions

#### `list_invoices`
Retrieve a paginated list of invoices from Stripe.

**Inputs:**
- `limit` (integer, optional): Number to return (max: 100)
- `customer` (string, optional): Filter by customer ID
- `status` (string, optional): Filter by status: `draft`, `open`, `paid`, `uncollectible`, `void`

**Outputs:**
- `invoices` (array): List of invoice objects
- `has_more` (boolean): Pagination indicator
- `result` (boolean): Success status

---

#### `get_invoice`
Retrieve details of a specific invoice.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID (starts with `in_`)

**Outputs:**
- `invoice` (object): Invoice details
- `result` (boolean): Success status

---

#### `create_invoice`
Create a new draft invoice in Stripe.

**Inputs:**
- `customer` (string, required): The Stripe customer ID to invoice
- `currency` (string, optional): Three-letter ISO currency code (default: `nzd`)
- `description` (string, optional): Invoice memo/description (shown on invoice)
- `auto_advance` (boolean, optional): Whether to auto-finalize (default: `false`)
- `collection_method` (string, optional): `charge_automatically` or `send_invoice`
- `days_until_due` (integer, optional): Days until invoice is due
- `metadata` (object, optional): Key-value pairs

**Outputs:**
- `invoice` (object): Created invoice details
- `result` (boolean): Success status

---

#### `update_invoice`
Update a draft invoice's details.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID
- `description`, `auto_advance`, `collection_method`, `days_until_due`, `metadata` (optional)

**Outputs:**
- `invoice` (object): Updated invoice details
- `result` (boolean): Success status

---

#### `delete_invoice`
Permanently delete a draft invoice.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID (must be draft)

**Outputs:**
- `id` (string): The deleted invoice ID
- `deleted` (boolean): Success indicator
- `result` (boolean): Success status

---

#### `finalize_invoice`
Finalize a draft invoice, making it ready for payment.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID
- `auto_advance` (boolean, optional): Whether to auto-advance after finalizing

**Outputs:**
- `invoice` (object): Finalized invoice details
- `result` (boolean): Success status

---

#### `send_invoice`
Send a finalized invoice to the customer via email.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID

**Outputs:**
- `invoice` (object): Sent invoice details
- `result` (boolean): Success status

---

#### `pay_invoice`
Pay an open invoice using the customer's default payment method.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID
- `payment_method` (string, optional): Specific payment method ID

**Outputs:**
- `invoice` (object): Paid invoice details
- `result` (boolean): Success status

---

#### `void_invoice`
Void an open invoice, marking it as uncollectible.

**Inputs:**
- `invoice_id` (string, required): The Stripe invoice ID

**Outputs:**
- `invoice` (object): Voided invoice details
- `result` (boolean): Success status

---

### Invoice Item Actions

#### `list_invoice_items`
Retrieve a paginated list of invoice items.

**Inputs:**
- `limit` (integer, optional): Number to return (max: 100)
- `customer` (string, optional): Filter by customer ID
- `invoice` (string, optional): Filter by invoice ID
- `pending` (boolean, optional): Filter for pending items

**Outputs:**
- `invoice_items` (array): List of invoice item objects
- `has_more` (boolean): Pagination indicator
- `result` (boolean): Success status

---

#### `get_invoice_item`
Retrieve details of a specific invoice item.

**Inputs:**
- `invoice_item_id` (string, required): The Stripe invoice item ID (starts with `ii_`)

**Outputs:**
- `invoice_item` (object): Invoice item details
- `result` (boolean): Success status

---

#### `create_invoice_item`
Create a new invoice item and optionally attach to a draft invoice.

**Inputs:**
- `customer` (string, required): The Stripe customer ID
- `invoice` (string, optional): Invoice ID to attach to (must be draft)
- `amount` (integer, optional): Amount in cents
- `currency` (string, optional): Currency code (default: `nzd`)
- `description` (string, optional): Line item description
- `quantity` (integer, optional): Quantity of units
- `unit_amount` (integer, optional): Unit price in cents
- `metadata` (object, optional): Key-value pairs

**Outputs:**
- `invoice_item` (object): Created invoice item details
- `result` (boolean): Success status

---

#### `update_invoice_item`
Update an existing invoice item.

**Inputs:**
- `invoice_item_id` (string, required): The Stripe invoice item ID
- `amount`, `description`, `quantity`, `unit_amount`, `metadata` (optional)

**Outputs:**
- `invoice_item` (object): Updated invoice item details
- `result` (boolean): Success status

---

#### `delete_invoice_item`
Delete an invoice item.

**Inputs:**
- `invoice_item_id` (string, required): The Stripe invoice item ID

**Outputs:**
- `id` (string): The deleted invoice item ID
- `deleted` (boolean): Success indicator
- `result` (boolean): Success status

---

## Requirements

- `autohive-integrations-sdk` (Autohive Integration SDK)

## Usage Examples

### Example 1: Create a RUC Invoice

```python
# 1. Create the invoice
invoice = await stripe.execute_action("create_invoice", {
    "customer": "cus_xxxxx",
    "currency": "nzd",
    "description": "RUC Purchase - GTR680 (John's BMW)\n5 units (5,000km)",
    "auto_advance": False,
    "collection_method": "send_invoice",
    "days_until_due": 30
}, context)

invoice_id = invoice.data["invoice"]["id"]

# 2. Add RUC line item ($66.09 x 5 units)
await stripe.execute_action("create_invoice_item", {
    "customer": "cus_xxxxx",
    "invoice": invoice_id,
    "unit_amount": 6609,  # cents
    "currency": "nzd",
    "quantity": 5,
    "description": "RUC - 5 units (5,000km)"
}, context)

# 3. Add NZTA Fee
await stripe.execute_action("create_invoice_item", {
    "customer": "cus_xxxxx",
    "invoice": invoice_id,
    "unit_amount": 1082,  # $10.82 in cents
    "currency": "nzd",
    "quantity": 1,
    "description": "NZTA Administration Fee"
}, context)

# 4. Add BONNET Processing Fee
await stripe.execute_action("create_invoice_item", {
    "customer": "cus_xxxxx",
    "invoice": invoice_id,
    "unit_amount": 600,  # $6.00 in cents
    "currency": "nzd",
    "quantity": 1,
    "description": "BONNET Processing Fee"
}, context)

# Invoice is now ready as draft for review
```

### Example 2: List Draft Invoices for a Customer

```python
result = await stripe.execute_action("list_invoices", {
    "customer": "cus_xxxxx",
    "status": "draft",
    "limit": 10
}, context)

for invoice in result.data["invoices"]:
    print(f"Invoice {invoice['id']}: ${invoice['total']/100:.2f}")
```

## Testing

To run the tests:

1. Navigate to the integration's directory:
   ```bash
   cd stripe
   ```

2. Set your test API key:
   ```bash
   export STRIPE_TEST_API_KEY=sk_test_your_key_here
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the tests:
   ```bash
   python tests/test_stripe.py
   ```

**Note**: Always use test API keys (`sk_test_`) when running tests to avoid creating real charges.

## API Reference

- [Stripe API Documentation](https://docs.stripe.com/api)
- [Customers API](https://docs.stripe.com/api/customers)
- [Invoices API](https://docs.stripe.com/api/invoices)
- [Invoice Items API](https://docs.stripe.com/api/invoiceitems)
