# Test suite for Ahrefs integration
import asyncio
from context import ahrefs
from autohive_integrations_sdk import ExecutionContext


# Test credentials - replace with your actual API key
TEST_AUTH = {
    "api_key": "your_api_key_here"
}


# ---- Domain Analysis Tests ----

async def test_get_domain_rating():
    """Test getting domain rating."""
    inputs = {"target": "ahrefs.com"}

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_domain_rating", inputs, context)
            print(f"Get Domain Rating Result: {result}")
            assert result.data.get('result') == True
            assert 'domain_rating' in result.data
            assert 'ahrefs_rank' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_domain_rating: {e}")
            return None


# ---- Backlinks Tests ----

async def test_get_backlinks_stats():
    """Test getting backlink statistics."""
    inputs = {
        "target": "ahrefs.com",
        "mode": "domain"
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_backlinks_stats", inputs, context)
            print(f"Get Backlinks Stats Result: {result}")
            assert result.data.get('result') == True
            assert 'live_backlinks' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_backlinks_stats: {e}")
            return None


async def test_get_backlinks():
    """Test getting backlinks."""
    inputs = {
        "target": "ahrefs.com",
        "mode": "domain",
        "limit": 10
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_backlinks", inputs, context)
            print(f"Get Backlinks Result: {result}")
            assert result.data.get('result') == True
            assert 'backlinks' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_backlinks: {e}")
            return None


async def test_get_referring_domains():
    """Test getting referring domains."""
    inputs = {
        "target": "ahrefs.com",
        "mode": "domain",
        "limit": 10
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_referring_domains", inputs, context)
            print(f"Get Referring Domains Result: {result}")
            assert result.data.get('result') == True
            assert 'referring_domains' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_referring_domains: {e}")
            return None


# ---- Organic Search Tests ----

async def test_get_organic_keywords():
    """Test getting organic keywords."""
    inputs = {
        "target": "ahrefs.com",
        "country": "us",
        "limit": 10
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_organic_keywords", inputs, context)
            print(f"Get Organic Keywords Result: {result}")
            assert result.data.get('result') == True
            assert 'keywords' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_organic_keywords: {e}")
            return None


async def test_get_top_pages():
    """Test getting top pages."""
    inputs = {
        "target": "ahrefs.com",
        "country": "us",
        "limit": 10
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_top_pages", inputs, context)
            print(f"Get Top Pages Result: {result}")
            assert result.data.get('result') == True
            assert 'pages' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_top_pages: {e}")
            return None


# ---- Outgoing Links Tests ----

async def test_get_outlinks_stats():
    """Test getting outgoing link statistics."""
    inputs = {
        "target": "ahrefs.com",
        "mode": "domain"
    }

    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await ahrefs.execute_action("get_outlinks_stats", inputs, context)
            print(f"Get Outlinks Stats Result: {result}")
            assert result.data.get('result') == True
            assert 'outgoing_links' in result.data
            return result
        except Exception as e:
            print(f"Error testing get_outlinks_stats: {e}")
            return None


# Main test runner
async def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Ahrefs Integration Test Suite")
    print("=" * 60)
    print()
    print("NOTE: Replace 'your_api_key_here' with your actual API key.")
    print("NOTE: Ahrefs API requires Enterprise plan for full access.")
    print()

    test_functions = [
        # Domain Analysis
        ("Get Domain Rating", test_get_domain_rating),
        # Backlinks
        ("Get Backlinks Stats", test_get_backlinks_stats),
        ("Get Backlinks", test_get_backlinks),
        ("Get Referring Domains", test_get_referring_domains),
        # Organic Search
        ("Get Organic Keywords", test_get_organic_keywords),
        ("Get Top Pages", test_get_top_pages),
        # Outgoing Links
        ("Get Outlinks Stats", test_get_outlinks_stats),
    ]

    results = []
    for test_name, test_func in test_functions:
        print(f"\n{'-' * 60}")
        print(f"Running: {test_name}")
        print(f"{'-' * 60}")
        result = await test_func()
        results.append((test_name, result is not None))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
