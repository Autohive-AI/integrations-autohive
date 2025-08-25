# Test for Xero Accounting integration
import asyncio
from context import xeroaccounting
from autohive_integrations_sdk import ExecutionContext

async def test_get_tenant_by_company_name():
    """
    Test the get_tenant_by_company_name action
    """
    # Setup mock auth object (platform auth for Xero)
    auth = {}  # Platform auth tokens are handled automatically by ExecutionContext

    inputs = {
        "company_name": "Test Company"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xeroaccounting.execute_action("get_tenant_by_company_name", inputs, context)
            print(f"Success: Found tenant - ID: {result.get('tenant_id')}, Name: {result.get('tenant_name')}")
            return result
        except Exception as e:
            print(f"Error testing get_tenant_by_company_name: {str(e)}")
            return None

async def test_get_aged_payables_with_specific_tenant():
    """
    Test fetching aged payables with a specific company's tenant
    """
    # First get tenant info
    tenant_result = await test_get_tenant_by_company_name()
    if not tenant_result:
        print("Cannot test aged payables without tenant information")
        return

    auth = {}
    inputs = {
        "contact_id": "test-contact-id-123"  # Replace with actual contact ID
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xeroaccounting.execute_action("get_aged_payables_by_contact", inputs, context)
            print(f"Success: Retrieved aged payables report")
            return result
        except Exception as e:
            print(f"Error testing aged payables: {str(e)}")
            return None

async def main():
    print("Testing Xero Accounting Integration")
    print("==================================")
    
    print("\n1. Testing get_tenant_by_company_name...")
    await test_get_tenant_by_company_name()
    
    print("\n2. Testing aged payables with tenant...")
    await test_get_aged_payables_with_specific_tenant()

if __name__ == "__main__":
    asyncio.run(main())
