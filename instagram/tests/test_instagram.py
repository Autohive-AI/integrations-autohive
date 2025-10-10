# Testbed for Instagram integration
import asyncio
from context import instagram
from autohive_integrations_sdk import ExecutionContext

async def test_get_recent_posts_default():
    """Test get_recent_posts with default limit (10 posts)"""
    print("\n[Test 1] Testing get_recent_posts with default limit...")

    # Setup auth object (you'll need real tokens for actual testing)
    auth = {
        "access_token": "your_facebook_access_token_here"
    }

    inputs = {}  # Using default limit of 10

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await instagram.execute_action("get_recent_posts", inputs, context)
            print(f"✓ Success! Retrieved {len(result['posts'])} posts")

            # Validate output structure
            assert "posts" in result, "Result should contain 'posts' key"
            assert isinstance(result["posts"], list), "'posts' should be a list"

            # Print first post details if available
            if result['posts']:
                first_post = result['posts'][0]
                print(f"  First post ID: {first_post.get('id', 'N/A')}")
                print(f"  Media type: {first_post.get('media_type', 'N/A')}")
                print(f"  Caption: {first_post.get('caption', '')[:60]}...")

                # Validate post structure
                required_fields = ['id', 'media_type', 'media_url', 'caption', 'timestamp', 'permalink']
                for field in required_fields:
                    assert field in first_post, f"Post should contain '{field}' field"

                print(f"✓ All required fields present in post object")
            else:
                print("  No posts found (this may be normal if account has no posts)")

        except Exception as e:
            print(f"✗ Error testing get_recent_posts: {str(e)}")
            raise


async def test_get_recent_posts_custom_limit():
    """Test get_recent_posts with custom limit (5 posts)"""
    print("\n[Test 2] Testing get_recent_posts with custom limit (5)...")

    auth = {
        "access_token": "your_facebook_access_token_here"
    }

    inputs = {
        "limit": 5
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await instagram.execute_action("get_recent_posts", inputs, context)
            print(f"✓ Success! Retrieved {len(result['posts'])} posts (requested limit: 5)")

            # Validate that we don't exceed the requested limit
            assert len(result['posts']) <= 5, "Should not return more posts than requested"
            print(f"✓ Limit respected correctly")

        except Exception as e:
            print(f"✗ Error testing get_recent_posts: {str(e)}")
            raise


async def test_get_recent_posts_max_limit():
    """Test get_recent_posts with maximum limit (25 posts)"""
    print("\n[Test 3] Testing get_recent_posts with maximum limit (25)...")

    auth = {
        "access_token": "your_facebook_access_token_here"
    }

    inputs = {
        "limit": 25
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await instagram.execute_action("get_recent_posts", inputs, context)
            print(f"✓ Success! Retrieved {len(result['posts'])} posts (requested limit: 25)")

            # Validate that we don't exceed the maximum limit
            assert len(result['posts']) <= 25, "Should not return more than 25 posts"
            print(f"✓ Maximum limit respected correctly")

        except Exception as e:
            print(f"✗ Error testing get_recent_posts: {str(e)}")
            raise


async def test_post_data_structure():
    """Test that post data contains all expected fields with correct types"""
    print("\n[Test 4] Testing post data structure and field types...")

    auth = {
        "access_token": "your_facebook_access_token_here"
    }

    inputs = {
        "limit": 1  # Just get one post to test structure
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await instagram.execute_action("get_recent_posts", inputs, context)

            if result['posts']:
                post = result['posts'][0]

                # Check all required fields exist
                required_fields = {
                    'id': str,
                    'media_type': str,
                    'media_url': str,
                    'caption': str,
                    'timestamp': str,
                    'permalink': str
                }

                for field, expected_type in required_fields.items():
                    assert field in post, f"Post missing required field: {field}"
                    assert isinstance(post[field], expected_type), f"Field '{field}' should be type {expected_type.__name__}"

                # Check media_type is one of expected values
                valid_media_types = ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']
                assert post['media_type'] in valid_media_types, f"media_type should be one of {valid_media_types}"

                print(f"✓ Post structure validated successfully")
                print(f"  - All required fields present")
                print(f"  - All field types correct")
                print(f"  - Media type valid: {post['media_type']}")
            else:
                print("  ⚠ No posts available to validate structure")

        except Exception as e:
            print(f"✗ Error testing post data structure: {str(e)}")
            raise


async def test_empty_results_handling():
    """Test that the integration handles empty results gracefully"""
    print("\n[Test 5] Testing empty results handling...")

    # This test simulates what happens when there are no posts or connection fails
    # The integration should return {"posts": []} rather than throwing an error

    auth = {
        "access_token": "invalid_token_for_testing"  # Intentionally invalid
    }

    inputs = {
        "limit": 5
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await instagram.execute_action("get_recent_posts", inputs, context)

            # Should still return a valid structure even on failure
            assert "posts" in result, "Result should always contain 'posts' key"
            assert isinstance(result["posts"], list), "'posts' should always be a list"

            print(f"✓ Empty results handled gracefully")
            print(f"  Returned: {result}")

        except Exception as e:
            # The current implementation catches all exceptions and returns {"posts": []}
            # So this shouldn't happen, but log if it does
            print(f"⚠ Exception raised instead of returning empty result: {str(e)}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Instagram Integration Test Suite")
    print("=" * 60)
    print("\nNote: These tests require valid Facebook/Instagram credentials")
    print("Replace 'your_facebook_access_token_here' with a real token\n")

    tests = [
        ("Default Limit Test", test_get_recent_posts_default),
        ("Custom Limit Test", test_get_recent_posts_custom_limit),
        ("Maximum Limit Test", test_get_recent_posts_max_limit),
        ("Data Structure Test", test_post_data_structure),
        ("Empty Results Test", test_empty_results_handling),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name} FAILED: {str(e)}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
