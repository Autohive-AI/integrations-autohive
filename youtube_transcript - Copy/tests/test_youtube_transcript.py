# Testbed for youtube_transcript integration.
import asyncio
from context import youtube_transcript
from autohive_integrations_sdk import ExecutionContext

async def test_get_transcript():
    # Setup auth with test API key
    auth = {
        "api_key": "test_api_key"
    }

    inputs = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await youtube_transcript.execute_action("get_transcript", inputs, context)
            assert "transcript" in result
            assert "video_id" in result
            assert "language" in result
            assert "available_languages" in result
            print(f"✓ Test passed: {result}")
        except Exception as e:
            print(f"Error testing get_transcript: {str(e)}")

async def main():
    print("Testing YouTube Transcript Integration")
    print("====================================")

    await test_get_transcript()

if __name__ == "__main__":
    asyncio.run(main())
