# Testbed for a simple integration.
# The IUT (integration under test) is the my_integration.py file
import asyncio
from context import my_integration
from autohive_integrations_sdk import ExecutionContext

async def test_something():
   
    # Setup a mock auth object with OAuth2 access token (since this integration uses OAuth2)
    auth = {
        "access_token": "test_access_token_12345",
        "token_type": "Bearer"
    }

    inputs = {
        "field_name": "field_value"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await my_integration.test_connection(context, inputs)
            print(f"Test result: {result}")
        except Exception as e:
            print(f"Error testing test_connection: {str(e)}")


async def main():
    print("Testing My Integration")
    print("====================+=")

    await test_something()

if __name__ == "__main__":
    asyncio.run(main())
