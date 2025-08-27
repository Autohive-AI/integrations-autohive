# Xero Integration

A comprehensive integration for accessing Xero accounting data including financial reports, contact information, and aged payables/receivables through the Xero API.

## Features

### Actions
- **Get Tenant by Company Name** - Find tenant information by company name from Xero connections
- **Find Contact by Name** - Search for contacts by name within a specific tenant
- **Get Aged Payables** - Retrieve aged payables report for specific contacts
- **Get Aged Receivables** - Retrieve aged receivables report for specific contacts
- **Get Balance Sheet** - Access balance sheet reports with optional period comparisons
- **Get Profit and Loss** - Retrieve P&L statements with flexible date ranges and timeframes
- **Get Trial Balance** - Access trial balance reports with optional payment filtering
- **Get Available Connections** - Retrieve all available Xero tenant connections with company names and IDs
- **Find Contact by Name** - Search for contacts by name within a specific tenant using tenant ID
- **Get Aged Payables** - Retrieve aged payables report for specific contacts using tenant ID and contact ID
- **Get Aged Receivables** - Retrieve aged receivables report for specific contacts using tenant ID and contact ID
- **Get Balance Sheet** - Access balance sheet reports with optional period comparisons using tenant ID
- **Get Profit and Loss** - Retrieve P&L statements with flexible date ranges and timeframes using tenant ID
- **Get Trial Balance** - Access trial balance reports with optional payment filtering using tenant ID

## Setup

### 1. Authentication
The integration uses Xero's OAuth 2.0 authentication:

1. **Create a Xero App**:
   - Go to [Xero Developer Portal](https://developer.xero.com/)
   - Create a new app and configure OAuth 2.0 settings
   - Note your Client ID and Client Secret

2. **Configure Integration**:
   - Set authentication provider to "xero" 
   - Complete OAuth flow through the platform's auth system
   - Grant necessary permissions to access accounting data

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Required Scopes
The integration requires these OAuth scopes:
- `accounting.reports.read` - Access financial reports
- `accounting.contacts.read` - Access contact information
- `offline_access` - Maintain token refresh capability

## Usage Examples

### Get Tenant Information
### Get Available Connections
```python
# Find tenant by company name
result = await integration.execute_action("get_tenant_by_company_name", {
    "company_name": "My Company Pty Ltd"
})
# Get all available tenant connections
result = await integration.execute_action("get_available_connections", {})

print(f"Tenant ID: {result['tenant_id']}")
print(f"Tenant Name: {result['tenant_name']}")
if result['success']:
    for company in result['companies']:
        print(f"Tenant ID: {company['tenant_id']}")
        print(f"Company Name: {company['company_name']}")
```

### Find Contact
```python
# Search for contacts by name
# Search for contacts by name using tenant ID
result = await integration.execute_action("find_contact_by_name", {
    "company_name": "My Company Pty Ltd",
    "tenant_id": "tenant-guid-123",
    "contact_name": "ABC Suppliers"
})

for contact in result["contacts"]:
    print(f"Contact: {contact['name']} (ID: {contact['contact_id']})")
```

### Get Aged Payables Report
```python
# Get aged payables for a specific contact
# Get aged payables for a specific contact using tenant ID
result = await integration.execute_action("get_aged_payables", {
    "company_name": "My Company Pty Ltd",
    "contact_id": "contact-guid-123",
    "tenant_id": "tenant-guid-123",
    "contact_id": "contact-guid-456",
    "date": "2025-01-31"
})

for report in result["reports"]:
    print(f"Report: {report['report_name']} - {report['report_date']}")
```

### Get Balance Sheet
```python
# Get current balance sheet with 3-month comparison
# Get current balance sheet with 3-month comparison using tenant ID
result = await integration.execute_action("get_balance_sheet", {
    "company_name": "My Company Pty Ltd",
    "tenant_id": "tenant-guid-123",
    "date": "2025-01-31",
    "periods": 3
})

for report in result["reports"]:
    print(f"Balance Sheet as of {report['report_date']}")
```

### Get Profit & Loss Statement
```python
# Get P&L for specific date range
# Get P&L for specific date range using tenant ID
result = await integration.execute_action("get_profit_and_loss", {
    "company_name": "My Company Pty Ltd",
    "tenant_id": "tenant-guid-123",
    "from_date": "2025-01-01",
    "to_date": "2025-01-31",
    "timeframe": "MONTH",
    "periods": 3
})

for report in result["reports"]:
    print(f"P&L Report: {report['report_name']}")
```

## Testing

### API Testing with Postman

Before implementing the integration, you can test Xero API access using Postman:

1. **Setup OAuth 2.0 Authentication**:
   - In Postman, go to Authorization tab
   - Select "OAuth 2.0" as type
   - Configure with your Xero app credentials
   - Use authorization URL: `https://login.xero.com/identity/connect/authorize`
   - Use token URL: `https://identity.xero.com/connect/token`
   - Add required scopes: `accounting.reports.read`, `accounting.contacts.read`, `offline_access`

2. **Test Key Endpoints**:
   - **Get Connections**: `GET https://api.xero.com/connections`
   - **Find Contacts**: `GET https://api.xero.com/api.xro/2.0/Contacts?where=Name.Contains("contact_name")`
   - **Aged Payables**: `GET https://api.xero.com/api.xro/2.0/Reports/AgedPayablesByContact?contactId={contact_id}`
   - **Aged Receivables**: `GET https://api.xero.com/api.xro/2.0/Reports/AgedReceivablesByContact?contactId={contact_id}`

3. **Required Headers**:
   - `Accept: application/json`
   - `xero-tenant-id: {tenant_id}` (from connections response)

This helps validate API access and understand response structures before coding the integration.

### Quick Test
```bash
# Run basic tests
cd tests
python test_xero.py
```

### Test Structure
```python
# Example test for tenant lookup
async def test_get_tenant_by_company_name():
# Example test for getting available connections
async def test_get_available_connections():
    auth = {}  # OAuth tokens handled automatically
    inputs = {"company_name": "Test Company"}
    inputs = {}
    
    async with ExecutionContext(auth=auth) as context:
        result = await xero.execute_action("get_tenant_by_company_name", inputs, context)
        assert "tenant_id" in result
        assert "tenant_name" in result
        result = await xero.execute_action("get_available_connections", inputs, context)
        assert result["success"] == True
        assert "companies" in result
```

## API Reference

### Actions

#### `get_tenant_by_company_name`
Find tenant information by company name.
#### `get_available_connections`
Get all available Xero tenant connections with company names and IDs.

**Input:**
- `company_name` (required): Company name to search for
- No input parameters required

**Output:**
- `tenant_id`: Xero tenant ID (GUID)
- `tenant_name`: Company name as registered in Xero
- `success`: Boolean indicating if request was successful
- `companies`: Array of company objects with tenant_id and company_name
- `message`: Error message if success is false

#### `find_contact_by_name`
Search for contacts by name within a tenant.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `contact_name` (required): Contact name to search for

**Output:**
- `contacts`: Array of matching contact objects with ID, name, and status

#### `get_aged_payables`
Retrieve aged payables report for a specific contact.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `contact_id` (required): Contact ID (GUID)
- `date` (optional): Report date (YYYY-MM-DD format)

**Output:**
- `reports`: Array containing Xero aged payables report data

#### `get_aged_receivables`
Retrieve aged receivables report for a specific contact.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `contact_id` (required): Contact ID (GUID)
- `date` (optional): Report date (YYYY-MM-DD format)

**Output:**
- `reports`: Array containing Xero aged receivables report data

#### `get_balance_sheet`
Access balance sheet report with optional period comparisons.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `date` (optional): Report date (YYYY-MM-DD format)
- `periods` (optional): Number of periods to compare (1-12)

**Output:**
- `reports`: Array containing balance sheet report data

#### `get_profit_and_loss`
Retrieve profit and loss statement with flexible parameters.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `date` (optional): Report date (YYYY-MM-DD format)
- `from_date` (optional): Period start date
- `to_date` (optional): Period end date
- `timeframe` (optional): Period type ("MONTH", "QUARTER", "YEAR")
- `periods` (optional): Number of periods to compare (1-12)

**Output:**
- `reports`: Array containing P&L report data

#### `get_trial_balance`
Access trial balance report with payment filtering options.

**Input:**
- `company_name` (required): Company name to identify tenant
- `tenant_id` (required): Xero tenant ID
- `date` (optional): Report date (defaults to last month end)
- `payments_only` (optional): Include only payments (boolean)

**Output:**
- `reports`: Array containing trial balance report data

## Error Handling

The integration includes comprehensive error handling:
- Invalid company names return descriptive error messages
- Missing contacts result in empty arrays rather than errors
- Network issues are handled gracefully with informative errors
- Authentication problems provide clear guidance for resolution
- All API responses are validated before returning data

## Development

### Project Structure
```
xero/
├── config.json          # Integration configuration
├── requirements.txt     # Python dependencies  
├── xero.py             # Main integration code
├── icon.png            # Integration icon
├── README.md           # This file
└── tests/
    ├── __init__.py
    ├── context.py      # Test context setup
    └── test_xero.py    # Test suite
```

### Adding New Features
1. Update `config.json` with new action definitions
2. Add implementation in `xero.py` with matching decorators
3. Add corresponding tests in `tests/test_xero.py`
4. Update this documentation

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify OAuth app is properly configured in Xero
   - Ensure required scopes are granted
   - Check token refresh is working properly

2. **Tenant Not Found**
   - Verify company name exactly matches Xero tenant name
   - Check user has access to the specified organization
   - Ensure company is properly connected to Xero

3. **Contact Not Found**  
   - Verify contact exists in the specified tenant
   - Check contact name spelling and formatting
   - Ensure contact is active (not archived)

4. **Empty Reports**
   - Check date ranges are valid
   - Verify contact has transactions in the specified period
   - Ensure user has appropriate permissions to view reports

### Debug Tips
- Use exact company names as they appear in Xero
- Contact names are case-insensitive but must be exact matches
- Date parameters should be in YYYY-MM-DD format
- All reports return raw Xero API response data for maximum flexibility

## Support

For issues related to:
- **Integration bugs**: Check the test suite and error logs
- **Xero API**: Consult [Xero API documentation](https://developer.xero.com/documentation/)
- **Authentication**: Verify OAuth app configuration and permissions
- **Data access**: Ensure proper user permissions and organization access