import asyncio
from pprint import pprint
from context import adwords
from autohive_integrations_sdk import ExecutionContext

async def test_retrieve_campaign_metrics():
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
        result = await adwords.execute_action("retrieve_campaign_metrics", inputs, context)
        
        print("\nGoogle Ads API Test Results:")
        print("============================")
        pprint(result)
        
    except Exception as e:
        print(f"Error testing Google Ads API: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_retrieve_keyword_metrics():
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
        "ad_group_ids": ["123456789", "987654321"],
        "campaign_ids": ["111222333", "444555666"],
        "date_ranges": ["2025-05-14_2025-05-20"]
    }

    try:
        result = await adwords.execute_action("retrieve_keyword_metrics", inputs, context)
        
        print("\nGoogle Ads Keyword Metrics Test Results:")
        print("=======================================")
        pprint(result)
        
    except Exception as e:
        print(f"Error testing Google Ads Keyword Metrics: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    print("Testing Google Ads Integration")
    print("=============================")
    
    await test_retrieve_campaign_metrics()
    await test_retrieve_keyword_metrics()

if __name__ == "__main__":
    asyncio.run(main()) 