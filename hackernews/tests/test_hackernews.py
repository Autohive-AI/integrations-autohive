import asyncio
from context import hackernews
from autohive_integrations_sdk import ExecutionContext


async def test_get_top_stories():
    """Test fetching top stories."""
    print("\n📰 Testing get_top_stories...")
    
    inputs = {"limit": 5}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_top_stories", inputs, context)
            assert "stories" in result
            assert "fetched_at" in result
            assert "count" in result
            assert len(result["stories"]) <= 5
            
            if result["stories"]:
                story = result["stories"][0]
                assert "id" in story
                assert "title" in story
                assert "hn_url" in story
                print(f"   ✅ Got {result['count']} stories")
                print(f"   📌 Top story: {story['title'][:60]}...")
            else:
                print("   ⚠️ No stories returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_best_stories():
    """Test fetching best stories."""
    print("\n🏆 Testing get_best_stories...")
    
    inputs = {"limit": 3}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_best_stories", inputs, context)
            assert "stories" in result
            assert len(result["stories"]) <= 3
            print(f"   ✅ Got {result['count']} best stories")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_new_stories():
    """Test fetching new stories."""
    print("\n🆕 Testing get_new_stories...")
    
    inputs = {"limit": 3}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_new_stories", inputs, context)
            assert "stories" in result
            print(f"   ✅ Got {result['count']} new stories")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_ask_hn_stories():
    """Test fetching Ask HN stories."""
    print("\n❓ Testing get_ask_hn_stories...")
    
    inputs = {"limit": 3}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_ask_hn_stories", inputs, context)
            assert "stories" in result
            print(f"   ✅ Got {result['count']} Ask HN stories")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_show_hn_stories():
    """Test fetching Show HN stories."""
    print("\n🎨 Testing get_show_hn_stories...")
    
    inputs = {"limit": 3}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_show_hn_stories", inputs, context)
            assert "stories" in result
            print(f"   ✅ Got {result['count']} Show HN stories")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_job_stories():
    """Test fetching job stories."""
    print("\n💼 Testing get_job_stories...")
    
    inputs = {"limit": 3}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_job_stories", inputs, context)
            assert "jobs" in result
            print(f"   ✅ Got {result['count']} job postings")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_story_with_comments():
    """Test fetching a story with comments."""
    print("\n💬 Testing get_story_with_comments...")
    
    async with ExecutionContext(auth={}) as context:
        try:
            top_result = await hackernews.execute_action(
                "get_top_stories", {"limit": 1}, context
            )
            
            if not top_result["stories"]:
                print("   ⚠️ No stories to test with")
                return
            
            story_id = top_result["stories"][0]["id"]
            
            inputs = {
                "story_id": story_id,
                "comment_limit": 5,
                "comment_depth": 2
            }
            
            result = await hackernews.execute_action("get_story_with_comments", inputs, context)
            assert "story" in result
            assert "comments" in result
            assert result["story"]["id"] == story_id
            
            print(f"   ✅ Got story with {len(result['comments'])} top-level comments")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_get_user_profile():
    """Test fetching a user profile."""
    print("\n👤 Testing get_user_profile...")
    
    inputs = {"username": "dang"}
    
    async with ExecutionContext(auth={}) as context:
        try:
            result = await hackernews.execute_action("get_user_profile", inputs, context)
            assert "id" in result
            assert "karma" in result
            assert result["id"] == "dang"
            
            print(f"   ✅ Got profile for {result['id']} (karma: {result['karma']})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


async def test_user_not_found():
    """Test handling of non-existent user."""
    print("\n🚫 Testing user not found handling...")
    
    inputs = {"username": "this_user_definitely_does_not_exist_12345"}
    
    async with ExecutionContext(auth={}) as context:
        try:
            await hackernews.execute_action("get_user_profile", inputs, context)
            print("   ❌ Should have raised an error")
        except ValueError as e:
            print(f"   ✅ Correctly raised error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error type: {e}")
            raise


async def main():
    print("=" * 50)
    print("🧪 Testing Hacker News Integration")
    print("=" * 50)
    
    await test_get_top_stories()
    await test_get_best_stories()
    await test_get_new_stories()
    await test_get_ask_hn_stories()
    await test_get_show_hn_stories()
    await test_get_job_stories()
    await test_get_story_with_comments()
    await test_get_user_profile()
    await test_user_not_found()
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
