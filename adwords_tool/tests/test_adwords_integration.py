import asyncio
from pprint import pprint
from context import adwords
from autohive_integrations_sdk import ExecutionContext

async def test_get_campaigns():
    auth = {
        "auth_type": "PlatformOAuth2",
        "credentials": {
            "access_token": "ACCESS_TOKEN",
            "refresh_token": "REFRESH_TOKEN",
        }
    }

    context = ExecutionContext(
        auth=auth
    )

    inputs = {
        "login_customer_id": "LOGIN_CUSTOMER_ID",
        "customer_id": "CUSTOMER_ID",
        "date_ranges": ["2025-05-14_2025-05-20"] # Explicit date range for last 7 days
    }

    try:
        result = await adwords.execute_action("get_campaign_data", inputs, context)
        
        print("\nGoogle Ads API Test Results:")
        print("============================")
        pprint(result)
        
    except Exception as e:
        print(f"Error testing Google Ads API: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    print("Testing Google Ads Integration")
    print("=============================")
    
    await test_get_campaigns()

if __name__ == "__main__":
    asyncio.run(main()) 