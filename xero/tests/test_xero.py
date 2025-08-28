# Test for Xero Accounting integration
import asyncio
from context import xero
from autohive_integrations_sdk import ExecutionContext

async def test_get_available_connections():
    """
    Test the get_available_connections action
    """
    # Setup mock auth object (platform auth for Xero)
    auth = {}  # Platform auth tokens are handled automatically by ExecutionContext

    inputs = {}  # No inputs required for get_available_connections

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xero.execute_action("get_available_connections", inputs, context)
            print(f"Success: Retrieved {len(result.get('companies', []))} available connections")
            if result.get('companies'):
                for company in result['companies']:
                    print(f"  - ID: {company.get('tenant_id')}, Name: {company.get('company_name')}")
            return result
        except Exception as e:
            print(f"Error testing get_available_connections: {str(e)}")
            return None

async def test_get_aged_payables_with_specific_tenant():
    """
    Test fetching aged payables with a specific tenant ID
    """
    # First get available connections
    connections_result = await test_get_available_connections()
    if not connections_result or not connections_result.get('companies'):
        print("Cannot test aged payables without tenant information")
        return

    # Use the first available tenant
    tenant_id = connections_result['companies'][0]['tenant_id']
    print(f"Using tenant ID: {tenant_id}")

    auth = {}
    inputs = {
        "tenant_id": tenant_id,
        "contact_id": "test-contact-id-123"  # Replace with actual contact ID
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xero.execute_action("get_aged_payables", inputs, context)
            print(f"Success: Retrieved aged payables report")
            return result
        except Exception as e:
            print(f"Error testing aged payables: {str(e)}")
            return None

async def main():
    print("Testing Xero Integration")
    print("==================================")
    
    print("\n1. Testing get_available_connections...")
    await test_get_available_connections()
    
    print("\n2. Testing aged payables with tenant ID...")
    await test_get_aged_payables_with_specific_tenant()

if __name__ == "__main__":
    asyncio.run(main())
