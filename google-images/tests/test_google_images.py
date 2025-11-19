import asyncio
from context import google_images
from autohive_integrations_sdk import ExecutionContext

async def test_google_images_search():
    """Test searching for Google Images"""
    
    # REPLACE WITH YOUR REAL API KEY IF YOU WANT REAL RESULTS
    # Otherwise, it will fail with an auth error from SerpApi, but the code will run
    auth = {
        "api_key": "0e601a38e1357b0cbbdaf897512a93cb98729b56a8577c6cf58ba172ab243f3e",
        "credentials": {
            "api_key": "0e601a38e1357b0cbbdaf897512a93cb98729b56a8577c6cf58ba172ab243f3e" 
        }
    }

    inputs = {
        "q": "Seddon Park 2025",
        "location": "New Zealand",
        "num": 5
    }

    print(f"\nRunning search for: {inputs['q']}...")

    async with ExecutionContext(auth=auth) as context:
        try:
            # Execute the action
            result = await google_images.execute_action("google_images_search", inputs, context)
            
            print(f"\n[Success] Found {result['total_results']} images")
            
            for i, img in enumerate(result['images']):
                print(f"\n--- Image {i+1} ---")
                print(f"Title: {img.get('title')}")
                print(f"Source: {img.get('source')}")
                print(f"URL: {img.get('image_url')}")
                print(f"Dimensions: {img.get('width')}x{img.get('height')}")

        except Exception as e:
            print(f"\n[Error] testing google_images_search: {e}")

async def main():
    print("=" * 60)
    print("TESTING GOOGLE IMAGES INTEGRATION")
    print("=" * 60)
    
    await test_google_images_search()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())