# Testbed for a simple integration.
# The IUT (integration under test) is the my_integration.py file
import asyncio
from context import my_integration
from autohive_integrations_sdk import ExecutionContext

async def test_something():
   
    # Setup a mock auth object
    auth = {
        "user_name": "test_user",
        "password": "test_password"
    }

    inputs = {
        "field_name": "field_value"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await my_integration.execute_action("<your-action-name>", inputs, context)
            ...
        except Exception as e:
            print(f"Error testing <your-action-name>: {e.message}")


async def main():
    print("Testing My Integration")
    print("====================+=")

    await test_something()

if __name__ == "__main__":
    asyncio.run(main())
