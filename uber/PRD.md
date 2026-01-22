# Uber Integration - Product Requirements Document (PRD)

## 1. Executive Summary

### 1.1 Overview
This document defines the requirements for building an Uber integration for the Autohive platform. The integration will enable businesses to automate transportation logistics, delivery management, expense tracking, and employee travel coordination through Uber's comprehensive API suite.

### 1.2 Business Value
- **Enterprise Travel Management**: Automate employee ride booking and expense tracking
- **Delivery Automation**: Enable on-demand delivery for e-commerce and logistics workflows
- **Cost Control**: Centralize business travel expenses with real-time receipt capture
- **Workflow Integration**: Connect Uber services to existing business processes in Autohive

### 1.3 Target Users
- Corporate travel managers
- E-commerce businesses requiring last-mile delivery
- Operations teams managing logistics
- Finance teams tracking transportation expenses

---

## 2. Uber API Landscape

### 2.1 Available API Products

| API Suite | Description | Use Case | Access Level |
|-----------|-------------|----------|--------------|
| **Uber for Business** | Employee/guest transportation management | Corporate travel, expense automation | Enterprise clients |
| **Uber Direct** | On-demand delivery dispatching | E-commerce, food delivery, logistics | Business accounts |
| **Ride Requests API** | Consumer ride booking | App integrations | OAuth-based |
| **Receipts API** | Trip receipt retrieval | Expense management | Business accounts |

### 2.2 Authentication Methods

| Method | API Suite | Description |
|--------|-----------|-------------|
| **OAuth 2.0 Client Credentials** | Uber Direct, Business APIs | Server-to-server authentication |
| **OAuth 2.0 Authorization Code** | Ride Requests | User-authorized access |
| **API Key + Secret** | Business APIs | Organization-level access |

**Recommended for Autohive**: OAuth 2.0 Client Credentials for Uber Direct and Business APIs.

---

## 3. Proposed Integration Scope

### 3.1 Phase 1: Uber Direct (Delivery) - MVP

The Uber Direct API enables on-demand delivery dispatching. This is the most immediately valuable for workflow automation.

#### Actions

| Action | API Endpoint | Description |
|--------|--------------|-------------|
| `create_delivery_quote` | `POST /v1/customers/{customer_id}/delivery_quotes` | Get delivery pricing and ETA before committing |
| `create_delivery` | `POST /v1/customers/{customer_id}/deliveries` | Dispatch a courier for pickup and delivery |
| `get_delivery` | `GET /v1/customers/{customer_id}/deliveries/{delivery_id}` | Check delivery status and courier details |
| `list_deliveries` | `GET /v1/customers/{customer_id}/deliveries` | Retrieve all deliveries with filtering |
| `update_delivery` | `POST /v1/customers/{customer_id}/deliveries/{delivery_id}` | Modify delivery details |
| `cancel_delivery` | `POST /v1/customers/{customer_id}/deliveries/{delivery_id}/cancel` | Cancel an ongoing or scheduled delivery |
| `get_proof_of_delivery` | `POST /v1/customers/{customer_id}/deliveries/{delivery_id}/proof-of-delivery` | Retrieve signature, photo, or PIN verification |

#### Key Input Parameters

**Create Delivery Quote**:
```json
{
  "pickup_address": { "street_address": ["..."], "city": "...", "state": "...", "zip_code": "...", "country": "US" },
  "dropoff_address": { "street_address": ["..."], "city": "...", "state": "...", "zip_code": "...", "country": "US" },
  "pickup_ready_dt": "2024-12-12T14:00:00.000Z",
  "pickup_deadline_dt": "2024-12-12T14:30:00.000Z",
  "dropoff_ready_dt": "2024-12-12T14:30:00.000Z",
  "dropoff_deadline_dt": "2024-12-12T16:00:00.000Z",
  "manifest_total_value": 5000
}
```

**Create Delivery**:
```json
{
  "quote_id": "dqt_xxx",
  "pickup_name": "Store Name",
  "pickup_phone_number": "+15551234567",
  "dropoff_name": "Customer Name",
  "dropoff_phone_number": "+15559876543",
  "manifest_items": [
    { "name": "Package", "quantity": 1, "size": "small" }
  ],
  "tip": 500
}
```

#### Delivery Statuses
| Status | Description |
|--------|-------------|
| `pending` | Delivery created, awaiting courier assignment |
| `pickup` | Courier en route to pickup location |
| `pickup_complete` | Courier has picked up the order |
| `dropoff` | Courier en route to dropoff location |
| `delivered` | Delivery completed successfully |
| `canceled` | Delivery was canceled |
| `returned` | Delivery was returned to sender |

#### Webhooks (Optional Enhancement)
| Webhook Event | Description |
|---------------|-------------|
| `event.delivery_status` | Real-time delivery status updates |
| `event.courier_update` | Courier location and ETA updates |
| `event.refund_request` | Refund request notifications |

---

### 3.2 Phase 2: Uber for Business (Corporate Travel)

#### Actions

| Action | API Endpoint | Description |
|--------|--------------|-------------|
| `get_trip_receipt` | `GET /v1/business/trips/{trip_id}/receipt` | Retrieve detailed trip receipt |
| `get_trip_receipt_pdf` | `GET /v1/business/trips/{trip_id}/receipt/pdf_url` | Get PDF receipt URL |
| `get_trip_invoice` | `GET /v1/business/trips/{trip_id}/invoice_urls` | Get invoice PDF URLs |
| `get_order_receipt` | `GET /v1/business/orders/{order_id}/receipt` | Retrieve Uber Eats order receipt |
| `list_employees` | SFTP/SCIM | Manage employee roster |
| `manage_expense_codes` | SFTP | Sync expense codes for trips |

#### Webhooks
| Webhook Event | Description |
|---------------|-------------|
| `business_trips.receipt_ready` | New trip receipt available |
| `business_trips.invoice_ready` | Invoice ready for download |
| `business_order.receipt` | Uber Eats order receipt ready |

---

### 3.3 Phase 3: Ride Requests (Consumer-facing)

#### Actions

| Action | API Endpoint | Description |
|--------|--------------|-------------|
| `get_ride_estimate` | `GET /v1/estimates/price` | Get fare estimates |
| `get_ride_products` | `GET /v1/products` | List available ride types |
| `request_ride` | `POST /v1/requests` | Book a ride for user |
| `get_ride_status` | `GET /v1/requests/{request_id}` | Check ride status |
| `cancel_ride` | `DELETE /v1/requests/{request_id}` | Cancel ride request |
| `get_ride_receipt` | `GET /v1/requests/{request_id}/receipt` | Get ride receipt |

---

## 4. Technical Specifications

### 4.1 Authentication Configuration

```json
{
  "auth": {
    "type": "oauth2",
    "provider": "uber",
    "grant_type": "client_credentials",
    "token_url": "https://login.uber.com/oauth/v2/token",
    "scopes": [
      "direct.organizations",
      "eats.deliveries"
    ]
  }
}
```

### 4.2 API Base URLs

| Environment | Base URL |
|-------------|----------|
| **Production** | `https://api.uber.com/v1` |
| **Sandbox** | `https://sandbox-api.uber.com/v1` |

### 4.3 Rate Limits

| Endpoint Type | Rate Limit |
|---------------|------------|
| Quote endpoints | 100 requests/minute |
| Delivery endpoints | 100 requests/minute |
| Status endpoints | 500 requests/minute |

### 4.4 Error Handling

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `invalid_params` | Invalid request parameters |
| 401 | `unauthorized` | Invalid or expired credentials |
| 402 | `customer_suspended` | Account suspended |
| 403 | `customer_blocked` | Account blocked |
| 404 | `not_found` | Resource not found |
| 409 | `duplicate_delivery` | Idempotency key conflict |
| 429 | `customer_limited` | Rate limit exceeded |
| 500 | `internal_server_error` | Uber server error |

---

## 5. config.json Structure

```json
{
  "name": "Uber",
  "display_name": "Uber",
  "version": "1.0.0",
  "description": "Uber integration for on-demand delivery and business transportation management",
  "entry_point": "uber.py",
  "supports_billing": false,
  "supports_connected_account": true,
  "auth": {
    "type": "oauth2",
    "provider": "uber",
    "grant_type": "client_credentials",
    "token_url": "https://login.uber.com/oauth/v2/token",
    "scopes": [
      "direct.organizations",
      "eats.deliveries"
    ]
  },
  "actions": {
    "create_delivery_quote": {
      "display_name": "Create Delivery Quote",
      "description": "Get pricing and ETA for a delivery before dispatching a courier",
      "input_schema": {
        "type": "object",
        "properties": {
          "pickup_address": { "type": "object", "description": "Pickup location address" },
          "dropoff_address": { "type": "object", "description": "Dropoff location address" },
          "pickup_ready_dt": { "type": "string", "format": "date-time", "description": "Earliest pickup time (ISO 8601)" },
          "pickup_deadline_dt": { "type": "string", "format": "date-time", "description": "Latest pickup time (ISO 8601)" },
          "dropoff_ready_dt": { "type": "string", "format": "date-time", "description": "Earliest dropoff time (ISO 8601)" },
          "dropoff_deadline_dt": { "type": "string", "format": "date-time", "description": "Latest dropoff time (ISO 8601)" },
          "manifest_total_value": { "type": "integer", "description": "Total value in cents for insurance" },
          "external_store_id": { "type": "string", "description": "Your internal store identifier" }
        },
        "required": ["pickup_address", "dropoff_address"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "quote_id": { "type": "string" },
          "fee": { "type": "integer", "description": "Delivery fee in cents" },
          "currency": { "type": "string" },
          "dropoff_eta": { "type": "string", "format": "date-time" },
          "duration": { "type": "integer", "description": "Estimated delivery time in minutes" },
          "expires": { "type": "string", "format": "date-time" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    },
    "create_delivery": {
      "display_name": "Create Delivery",
      "description": "Dispatch an Uber courier to pick up and deliver an order",
      "input_schema": {
        "type": "object",
        "properties": {
          "quote_id": { "type": "string", "description": "Quote ID from create_delivery_quote" },
          "pickup_name": { "type": "string", "description": "Pickup contact name" },
          "pickup_phone_number": { "type": "string", "description": "Pickup contact phone (E.164 format)" },
          "pickup_address": { "type": "object", "description": "Pickup address (if not using quote)" },
          "dropoff_name": { "type": "string", "description": "Dropoff contact name" },
          "dropoff_phone_number": { "type": "string", "description": "Dropoff contact phone (E.164 format)" },
          "dropoff_address": { "type": "object", "description": "Dropoff address (if not using quote)" },
          "manifest_items": { "type": "array", "description": "Items being delivered" },
          "tip": { "type": "integer", "description": "Tip amount in cents" },
          "idempotency_key": { "type": "string", "description": "Unique key to prevent duplicate deliveries" },
          "dropoff_notes": { "type": "string", "description": "Instructions for courier at dropoff" },
          "pickup_notes": { "type": "string", "description": "Instructions for courier at pickup" }
        },
        "required": ["pickup_name", "pickup_phone_number", "dropoff_name", "dropoff_phone_number"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "delivery_id": { "type": "string" },
          "status": { "type": "string" },
          "quote_id": { "type": "string" },
          "fee": { "type": "integer" },
          "currency": { "type": "string" },
          "dropoff_eta": { "type": "string", "format": "date-time" },
          "tracking_url": { "type": "string" },
          "courier": { "type": "object" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    },
    "get_delivery": {
      "display_name": "Get Delivery",
      "description": "Retrieve current status and details of a delivery",
      "input_schema": {
        "type": "object",
        "properties": {
          "delivery_id": { "type": "string", "description": "The delivery ID" }
        },
        "required": ["delivery_id"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "delivery": { "type": "object" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    },
    "list_deliveries": {
      "display_name": "List Deliveries",
      "description": "Retrieve a list of deliveries with optional filtering",
      "input_schema": {
        "type": "object",
        "properties": {
          "limit": { "type": "integer", "default": 50, "maximum": 100 },
          "offset": { "type": "integer", "default": 0 },
          "status": { "type": "string", "enum": ["pending", "pickup", "pickup_complete", "dropoff", "delivered", "canceled", "returned"] },
          "start_date": { "type": "string", "format": "date-time" },
          "end_date": { "type": "string", "format": "date-time" }
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "deliveries": { "type": "array" },
          "total": { "type": "integer" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    },
    "cancel_delivery": {
      "display_name": "Cancel Delivery",
      "description": "Cancel an ongoing or scheduled delivery",
      "input_schema": {
        "type": "object",
        "properties": {
          "delivery_id": { "type": "string", "description": "The delivery ID to cancel" },
          "cancellation_reason": {
            "type": "string",
            "enum": ["out_of_items", "store_closed", "customer_called_to_cancel", "store_too_busy", "courier_delayed_en_route_to_pickup", "too_expensive", "customer_changed_order_requirements", "delivery_vehicle_too_small", "no_courier_assigned", "other"]
          },
          "additional_description": { "type": "string", "description": "Required if reason is 'other'" }
        },
        "required": ["delivery_id", "cancellation_reason"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "delivery": { "type": "object" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    },
    "get_proof_of_delivery": {
      "display_name": "Get Proof of Delivery",
      "description": "Retrieve signature, photo, or PIN verification proof for a completed delivery",
      "input_schema": {
        "type": "object",
        "properties": {
          "delivery_id": { "type": "string", "description": "The delivery ID" }
        },
        "required": ["delivery_id"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "proof_image_base64": { "type": "string" },
          "signature": { "type": "object" },
          "picture": { "type": "object" },
          "pin_code": { "type": "object" },
          "result": { "type": "boolean" },
          "error": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 6. Use Case Examples

### 6.1 E-commerce Order Fulfillment
```
Trigger: New order placed in Shopify
Action 1: create_delivery_quote (get pricing)
Condition: If fee < $15
Action 2: create_delivery (dispatch courier)
Action 3: Update order with tracking URL
Action 4: get_delivery (poll for status updates)
Action 5: Notify customer on delivery
```

### 6.2 Restaurant Delivery
```
Trigger: Order ready in POS system
Action 1: create_delivery with 15-min pickup window
Action 2: Send tracking link to customer
Action 3: Monitor status via webhook
```

### 6.3 Corporate Document Delivery
```
Trigger: Document signed in DocuSign
Action 1: create_delivery_quote for same-day delivery
Action 2: create_delivery with signature verification required
Action 3: get_proof_of_delivery on completion
Action 4: Store proof in document archive
```

---

## 7. Implementation Roadmap

### Phase 1: MVP (Week 1-2)
- [ ] Set up Uber Direct sandbox account
- [ ] Implement OAuth 2.0 client credentials flow
- [ ] Implement `create_delivery_quote` action
- [ ] Implement `create_delivery` action
- [ ] Implement `get_delivery` action
- [ ] Implement `cancel_delivery` action
- [ ] Write unit tests

### Phase 2: Extended Delivery Features (Week 3)
- [ ] Implement `list_deliveries` action
- [ ] Implement `get_proof_of_delivery` action
- [ ] Add webhook handler for real-time updates
- [ ] Add support for scheduled deliveries

### Phase 3: Business APIs (Week 4+)
- [ ] Implement Receipts API actions
- [ ] Implement expense code management
- [ ] Evaluate SFTP/SCIM provisioning needs

---

## 8. Testing Strategy

### 8.1 Sandbox Testing
Uber provides a sandbox environment with simulated deliveries:
- Use `POST /sandbox/terminal-state-trip-run` to simulate trip states
- Use `POST /sandbox/terminal-state-eats-run` for Eats order simulation
- Deliveries auto-progress through states in sandbox

### 8.2 Test Cases
| Test | Description |
|------|-------------|
| Quote creation | Verify quote returns fee, ETA, and expires |
| Delivery creation | Verify delivery ID and initial status |
| Invalid address | Confirm proper error handling |
| Cancellation | Test cancel with various reasons |
| Rate limiting | Handle 429 responses gracefully |
| Duplicate prevention | Verify idempotency key works |

---

## 9. Security Considerations

- Store OAuth credentials securely (never in code)
- Use HTTPS for all API calls
- Implement idempotency keys to prevent duplicate deliveries
- Validate phone numbers before sending to API
- Mask customer PII in logs
- Implement proper error handling to avoid leaking API details

---

## 10. Dependencies & Requirements

### 10.1 Uber Account Requirements
- Uber for Business Enterprise account (for Business APIs)
- Uber Direct merchant account (for delivery APIs)
- Completed Uber partner onboarding

### 10.2 Technical Requirements
- Python 3.9+
- `autohive_integrations_sdk`
- `aiohttp` or similar for async HTTP
- Environment variables for credentials

---

## 11. References

| Resource | URL |
|----------|-----|
| Uber Direct API Docs | https://developer.uber.com/docs/deliveries/overview |
| Uber for Business API | https://developer.uber.com/docs/businesses/introduction |
| Ride Requests API | https://developer.uber.com/docs/riders/introduction |
| Authentication Guide | https://developer.uber.com/docs/deliveries/guides/authentication |
| Sandbox Testing | https://developer.uber.com/docs/deliveries/guides/robocourier |
| Webhooks Guide | https://developer.uber.com/docs/deliveries/guides/webhooks |

---

## 12. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-23 | Autohive Team | Initial PRD |
