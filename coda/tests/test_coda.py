# Test suite for Coda integration
import asyncio
from context import coda
from autohive_integrations_sdk import ExecutionContext

async def test_list_docs():
    """Test listing all accessible Coda docs"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 1: List All Docs")
            print("=" * 60)
            result = await coda.execute_action("list_docs", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                docs_count = len(result.get("docs", []))
                print(f"SUCCESS: Found {docs_count} docs")
                for idx, doc in enumerate(result.get("docs", [])[:3], 1):
                    print(f"\n{idx}. {doc.get('name', 'Untitled')}")
                    print(f"   ID: {doc.get('id')}")
                    print(f"   Owner: {doc.get('owner')}")

            return result
        except Exception as e:
            print(f"Error testing list_docs: {e}")
            return None

async def test_list_docs_with_filters():
    """Test listing docs with filters"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {
        "is_owner": True,
        "limit": 5
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 2: List Docs (Owner Only, Limit 5)")
            print("=" * 60)
            result = await coda.execute_action("list_docs", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                docs_count = len(result.get("docs", []))
                print(f"SUCCESS: Found {docs_count} owned docs (max 5)")
                assert docs_count <= 5, f"Expected max 5 docs, got {docs_count}"

            return result
        except Exception as e:
            print(f"Error testing list_docs_with_filters: {e}")
            return None

async def test_list_docs_with_query():
    """Test searching docs by query"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {
        "query": "test",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 3: Search Docs with Query 'test'")
            print("=" * 60)
            result = await coda.execute_action("list_docs", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                docs_count = len(result.get("docs", []))
                print(f"SUCCESS: Found {docs_count} docs matching 'test'")

            return result
        except Exception as e:
            print(f"Error testing list_docs_with_query: {e}")
            return None

async def test_get_doc():
    """Test getting a specific doc by ID"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID from list_docs
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 4: Get Doc (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            print("\nTest 4: Get Doc by ID")
            print("=" * 60)

            inputs = {"doc_id": doc_id}
            result = await coda.execute_action("get_doc", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                doc = result.get("data", {})
                print(f"SUCCESS: Retrieved doc")
                print(f"Name: {doc.get('name')}")
                print(f"ID: {doc.get('id')}")
                print(f"Owner: {doc.get('owner')}")
                print(f"Created: {doc.get('createdAt')}")
                print(f"Updated: {doc.get('updatedAt')}")

            return result
        except Exception as e:
            print(f"Error testing get_doc: {e}")
            return None

async def test_create_doc():
    """Test creating a new Coda doc"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {
        "title": "Test Doc - Created by Integration"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 5: Create New Doc")
            print("=" * 60)
            result = await coda.execute_action("create_doc", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                doc = result.get("data", {})
                print(f"SUCCESS: Doc created (HTTP 202 - Processing)")
                print(f"Name: {doc.get('name')}")
                print(f"ID: {doc.get('id')}")
                print(f"Request ID: {doc.get('requestId', 'N/A')}")

            return result
        except Exception as e:
            print(f"Error testing create_doc: {e}")
            return None

async def test_create_doc_from_source():
    """Test creating a doc from a source doc (template)"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID to use as source
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 6: Create Doc from Source (SKIPPED - No docs available)")
                return None

            source_doc_id = list_result["docs"][0]["id"]

            print("\nTest 6: Create Doc from Source Template")
            print("=" * 60)

            inputs = {
                "title": "Test Doc - From Template",
                "source_doc": source_doc_id
            }
            result = await coda.execute_action("create_doc", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                doc = result.get("data", {})
                print(f"SUCCESS: Doc created from source (HTTP 202 - Processing)")
                print(f"Name: {doc.get('name')}")
                print(f"ID: {doc.get('id')}")
                print(f"Source Doc: {source_doc_id}")

            return result
        except Exception as e:
            print(f"Error testing create_doc_from_source: {e}")
            return None

async def test_list_published_docs():
    """Test listing only published docs"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {
        "is_published": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 7: List Published Docs Only")
            print("=" * 60)
            result = await coda.execute_action("list_docs", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                docs_count = len(result.get("docs", []))
                print(f"SUCCESS: Found {docs_count} published docs")

            return result
        except Exception as e:
            print(f"Error testing list_published_docs: {e}")
            return None

async def test_list_starred_docs():
    """Test listing only starred docs"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    inputs = {
        "is_starred": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            print("\nTest 8: List Starred Docs Only")
            print("=" * 60)
            result = await coda.execute_action("list_docs", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                docs_count = len(result.get("docs", []))
                print(f"SUCCESS: Found {docs_count} starred docs")

            return result
        except Exception as e:
            print(f"Error testing list_starred_docs: {e}")
            return None

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CODA INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\nNOTE: Replace 'your_api_token_here' with actual API token")
    print("Get token from: https://coda.io/account")
    print("=" * 60)

    # Run all tests
    await test_list_docs()
    await test_list_docs_with_filters()
    await test_list_docs_with_query()
    await test_get_doc()
    await test_create_doc()
    await test_create_doc_from_source()
    await test_list_published_docs()
    await test_list_starred_docs()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
