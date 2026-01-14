# NZBN Integration

Integration with the New Zealand Business Number (NZBN) API for searching and retrieving business entity information from the NZBN Register.

## Overview

The NZBN API provides access to the New Zealand Business Number Register, which contains information about New Zealand businesses including:
- Companies (NZ and Overseas)
- Sole Traders
- Partnerships
- Trusts
- Incorporated Societies
- Charitable Trusts
- Public Sector Entities

## Authentication

This integration uses **2-legged OAuth** authentication. You need:

1. **Subscription Key** - From your NZBN API subscription
2. **Client ID** - From your registered application
3. **Client Secret** - From your registered application

### Getting Your Credentials

1. Register at [api.business.govt.nz](https://portal.api.business.govt.nz)
2. Subscribe to the **NZBN API** product (choose 2-legged OAuth method)
3. Create an **Application** under "My Applications"
4. Copy your Client ID and Client Secret
5. Get your Subscription Key from "My Subscriptions"

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `subscription_key` | Yes | Your NZBN API subscription key (Ocp-Apim-Subscription-Key) |
| `client_id` | Yes | OAuth Client ID from your registered application |
| `client_secret` | Yes | OAuth Client Secret from your registered application |
| `environment` | No | `sandbox` for testing, `production` for live data (default: production) |

## Available Actions

### search_entities
Search the NZBN directory by name, trading name, NZBN, or company number.

**Inputs:**
- `search_term` (required): Text to search for
- `entity_status`: Filter by status (Registered, InLiquidation, etc.)
- `entity_type`: Filter by type (NZCompany, SoleTrader, Partnership, etc.)
- `industry_code`: Filter by BIC code
- `page`: Page number (zero-indexed)
- `page_size`: Results per page

### get_entity
Get full details about a specific business entity by NZBN.

**Inputs:**
- `nzbn` (required): 13-digit New Zealand Business Number

**Returns:** Full entity details including addresses, contacts, roles, trading names, and industry classifications.

### get_entity_changes
Search for entities that have been updated within a time period.

**Inputs:**
- `change_event_type` (required): Type of change (EntityRegistered, DirectorChanged, etc.)
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `entity_type`: Filter by entity type

### get_entity_roles
Get roles (directors, shareholders, partners) for a business entity.

**Inputs:**
- `nzbn` (required): 13-digit NZBN

### get_entity_addresses
Get addresses for a business entity.

**Inputs:**
- `nzbn` (required): 13-digit NZBN
- `address_type`: Filter by type (RegisteredOffice, AddressForService, etc.)

### get_entity_trading_names
Get trading names for a business entity.

### get_entity_phone_numbers
Get phone numbers for a business entity.

### get_entity_email_addresses
Get email addresses for a business entity.

### get_entity_websites
Get websites for a business entity.

### get_entity_gst_numbers
Get GST registration numbers for a business entity.

### get_entity_industry_classifications
Get BIC industry classifications for a business entity.

### get_entity_company_details
Get company-specific details (annual returns, constitution) for NZ companies.

### get_entity_history
Get change history for a business entity.

### get_entity_trading_areas
Get geographic trading areas for a business entity.

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
| GovtCentral | Central Government |
| GovtLocal | Local Government |
| GovtEdu | Education |
| GovtOther | Other Public Entity |

## Entity Statuses

- `Registered`
- `VoluntaryAdministration`
- `InReceivership`
- `InLiquidation`
- `InStatutoryAdministration`
- `Inactive`
- `RemovedClosed`

## API Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.business.govt.nz/gateway/nzbn/v5` |
| Sandbox | `https://api.business.govt.nz/sandbox/nzbn/v5` |

> **Note:** Sandbox data is not a mirror of production. It contains test cases and old Companies Register data (prior to 2010).

## OAuth Token Endpoint

Token URL: `https://login.microsoftonline.com/b2cessmapprd.onmicrosoft.com/oauth2/v2.0/token`

| Environment | Scope |
|-------------|-------|
| Production | `https://api.business.govt.nz/gateway/.default` |
| Sandbox | `https://api.business.govt.nz/sandbox/.default` |

## Testing

```bash
# Run unit tests
cd integrations-autohive/nzbn
pip install pytest pytest-asyncio
python -m pytest tests/ -v

# Run live sandbox test
pip install aiohttp
python test_live.py
```

## Resources

- [NZBN API Portal](https://portal.api.business.govt.nz/api/nzbn)
- [NZBN Website](https://www.nzbn.govt.nz/)
- [API Getting Started Guide](https://portal.api.business.govt.nz/getting-started)
- [2-Legged OAuth Documentation](https://support.api.business.govt.nz/s/article/cloud-authentication-oauth-2-legged)
- [NZBN Support](https://support.api.business.govt.nz/)

## Version

1.0.0
