import sys
import os
import asyncio
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../dependencies"))

from autohive_integrations_sdk import ExecutionContext
from adwords import adwords

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
        # TODO: See todo in adwords.py on passing in the login client id
        "customer_id": "CUSTOMER_ID", # ID of the Google Ads account we want to query from (cannot be a Manager Account)
        "date_ranges": ["last_7_days"]
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