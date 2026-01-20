# NZBN Integration

Integration with the New Zealand Business Number (NZBN) API for searching and retrieving business entity information from the NZBN Register.

## Overview

The NZBN (New Zealand Business Number) is a unique 13-digit identifier for NZ businesses. This integration provides access to the NZBN Register API, allowing you to:

- Search for businesses by name, trading name, or NZBN
- Retrieve detailed entity information
- Get addresses, roles, trading names, and GST numbers
- Track changes to business registrations

## Authentication

This integration uses Autohive's pre-configured NZBN API credentials with 2-legged OAuth (Client Credentials flow). **No user configuration required** - credentials are managed by Autohive.

### Deployment Configuration

The following environment variables must be set at deployment time:

| Variable | Description |
|----------|-------------|
| `NZBN_CLIENT_ID` | OAuth Client ID (Autohive's registered NZBN app) |
| `NZBN_CLIENT_SECRET` | OAuth Client Secret |
| `NZBN_SUBSCRIPTION_KEY` | NZBN API Subscription Key |

### Security Model

- OAuth credentials are injected server-side at deployment, not distributed to users
- Tokens are cached with automatic refresh before expiry
- Zero-config experience for end users

## Actions

### search_entities

Search the NZBN directory by name, trading name, NZBN, or company number.

**Inputs:**
- `search_term` (required): Text to search for
- `entity_status`: Filter by status (Registered, InLiquidation, etc.)
- `entity_type`: Filter by type (NZCompany, SoleTrader, Partnership, etc.)
- `page`: Page number (zero-indexed, default: 0)
- `page_size`: Results per page (default: 25, max: 100)

**Example:**
```json
{
  "search_term": "Xero",
  "entity_type": "NZCompany",
  "page_size": 10
}
```

### get_entity

Retrieve detailed information about a specific business entity.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

**Example:**
```json
{
  "nzbn": "9429041525746"
}
```

### get_entity_addresses

Retrieve addresses for a business entity.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier
- `address_type`: Filter by type (RegisteredOffice, Physical, Postal)

### get_entity_roles

Retrieve roles/officers (directors, shareholders) for an entity.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

### get_entity_trading_names

Retrieve trading names for a business entity.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

### get_company_details

Retrieve company-specific details for NZ companies.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

### get_entity_gst_numbers

Retrieve GST numbers registered to a business.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

### get_entity_industry_classifications

Retrieve industry classification codes (ANZSIC) for an entity.

**Inputs:**
- `nzbn` (required): The 13-digit NZBN identifier

### get_changes

Search for entities that have changed within a time period.

**Inputs:**
- `change_event_type` (required): Type of change (NewRegistration, NameChange, StatusChange, etc.)
- `start_date`: Start date (ISO format: YYYY-MM-DD)
- `end_date`: End date (ISO format: YYYY-MM-DD)
- `page`: Page number (zero-indexed)
- `page_size`: Results per page (max: 100)

## Entity Types

| Code | Description |
|------|-------------|
| LTD | NZ Limited Company |
| ULTD | NZ Unlimited Company |
| COOP | NZ Co-operative Company |
| ASIC | Overseas ASIC Company |
| NON_ASIC | Overseas Non-ASIC Company |
| Sole_Trader | Sole Trader |
| Partnership | Partnership |
| Trading_Trust | Trust |
| B | Building Society |
| I | Incorporated Society |
| D | Credit Union |
| F | Friendly Society |
| N | Industrial & Provident Society |
| S | Special Body |
| T | Charitable Trust |
| Y | Limited Partnership (NZ) |
| Z | Limited Partnership (Overseas) |

## Entity Status Codes

| Code | Description |
|------|-------------|
| Registered | Active and registered |
| VoluntaryAdministration | In voluntary administration |
| InReceivership | In receivership |
| InLiquidation | In liquidation |
| InStatutoryAdministration | In statutory administration |
| Inactive | Inactive |
| RemovedClosed | Removed or closed |

## Testing

```bash
cd nzbn
python -m pytest tests/ -v
```

## API Documentation

- [NZBN API Portal](https://portal.api.business.govt.nz/api/nzbn)
- [NZBN Website](https://www.nzbn.govt.nz/)
- [API Support](https://support.api.business.govt.nz/)

## Rate Limits

The NZBN API is free to use but may have rate limits. Check the API portal for current limits.

## Notes

- Sandbox data is test data and not a mirror of production
- Some PBD (Primary Business Data) may be private if set by the business
- ETags can be used for efficient data retrieval (If-None-Match header)
