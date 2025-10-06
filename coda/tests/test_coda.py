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

async def test_list_pages():
    """Test listing pages in a doc"""
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
                print("\nTest 9: List Pages (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            print("\nTest 9: List Pages")
            print("=" * 60)

            inputs = {"doc_id": doc_id, "limit": 10}
            result = await coda.execute_action("list_pages", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                pages_count = len(result.get("pages", []))
                print(f"SUCCESS: Found {pages_count} pages")
                for idx, page in enumerate(result.get("pages", [])[:3], 1):
                    print(f"\n{idx}. {page.get('name', 'Untitled')}")
                    print(f"   ID: {page.get('id')}")

            return result
        except Exception as e:
            print(f"Error testing list_pages: {e}")
            return None

async def test_get_page():
    """Test getting a specific page"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID and page ID
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 10: Get Page (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            # Get pages
            pages_result = await coda.execute_action("list_pages", {"doc_id": doc_id, "limit": 1}, context)

            if not pages_result.get("result") or not pages_result.get("pages"):
                print("\nTest 10: Get Page (SKIPPED - No pages available)")
                return None

            page_id = pages_result["pages"][0]["id"]

            print("\nTest 10: Get Page")
            print("=" * 60)

            inputs = {"doc_id": doc_id, "page_id_or_name": page_id}
            result = await coda.execute_action("get_page", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                page = result.get("data", {})
                print(f"SUCCESS: Retrieved page")
                print(f"Name: {page.get('name')}")
                print(f"ID: {page.get('id')}")
                print(f"Subtitle: {page.get('subtitle', 'None')}")
                print(f"Created: {page.get('createdAt')}")

            return result
        except Exception as e:
            print(f"Error testing get_page: {e}")
            return None

async def test_create_page():
    """Test creating a new page in a doc"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 11: Create Page (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            print("\nTest 11: Create Page")
            print("=" * 60)

            inputs = {
                "doc_id": doc_id,
                "name": "Test Page - Created by Integration",
                "subtitle": "This is a test page",
                "icon_name": "rocket"
            }
            result = await coda.execute_action("create_page", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                page = result.get("data", {})
                print(f"SUCCESS: Page created (HTTP 202 - Processing)")
                print(f"ID: {page.get('id')}")
                print(f"Request ID: {page.get('requestId', 'N/A')}")

            return result
        except Exception as e:
            print(f"Error testing create_page: {e}")
            return None

async def test_create_page_with_content():
    """Test creating a page with HTML content"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 12: Create Page with Content (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            print("\nTest 12: Create Page with Content")
            print("=" * 60)

            inputs = {
                "doc_id": doc_id,
                "name": "Test Page with Content",
                "content_format": "html",
                "content": "<h1>Test Content</h1><p>This is a test page with HTML content.</p>"
            }
            result = await coda.execute_action("create_page", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                page = result.get("data", {})
                print(f"SUCCESS: Page with content created (HTTP 202 - Processing)")
                print(f"ID: {page.get('id')}")

            return result
        except Exception as e:
            print(f"Error testing create_page_with_content: {e}")
            return None

async def test_update_page():
    """Test updating a page's metadata"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, get a doc ID and page ID
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 13: Update Page (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            # Get pages
            pages_result = await coda.execute_action("list_pages", {"doc_id": doc_id, "limit": 1}, context)

            if not pages_result.get("result") or not pages_result.get("pages"):
                print("\nTest 13: Update Page (SKIPPED - No pages available)")
                return None

            page_id = pages_result["pages"][0]["id"]

            print("\nTest 13: Update Page")
            print("=" * 60)

            inputs = {
                "doc_id": doc_id,
                "page_id_or_name": page_id,
                "name": "Updated Page Name",
                "subtitle": "Updated subtitle"
            }
            result = await coda.execute_action("update_page", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                page = result.get("data", {})
                print(f"SUCCESS: Page updated (HTTP 202 - Processing)")
                print(f"ID: {page.get('id')}")
                print(f"Request ID: {page.get('requestId', 'N/A')}")

            return result
        except Exception as e:
            print(f"Error testing update_page: {e}")
            return None

async def test_delete_page():
    """Test deleting a page"""
    auth = {
        "credentials": {
            "api_token": "your_api_token_here"
        }
    }

    # First, create a test page to delete
    list_inputs = {"limit": 1}
    async with ExecutionContext(auth=auth) as context:
        try:
            list_result = await coda.execute_action("list_docs", list_inputs, context)

            if not list_result.get("result") or not list_result.get("docs"):
                print("\nTest 14: Delete Page (SKIPPED - No docs available)")
                return None

            doc_id = list_result["docs"][0]["id"]

            # Create a page to delete
            create_result = await coda.execute_action("create_page", {
                "doc_id": doc_id,
                "name": "Page to Delete"
            }, context)

            if not create_result.get("result"):
                print("\nTest 14: Delete Page (SKIPPED - Could not create test page)")
                return None

            # Wait a moment for page creation to process
            import asyncio
            await asyncio.sleep(2)

            # Get the created page ID from list
            pages_result = await coda.execute_action("list_pages", {"doc_id": doc_id}, context)

            # Find the page we just created
            page_id = None
            for page in pages_result.get("pages", []):
                if page.get("name") == "Page to Delete":
                    page_id = page.get("id")
                    break

            if not page_id:
                print("\nTest 14: Delete Page (SKIPPED - Could not find created page)")
                return None

            print("\nTest 14: Delete Page")
            print("=" * 60)

            inputs = {
                "doc_id": doc_id,
                "page_id_or_name": page_id
            }
            result = await coda.execute_action("delete_page", inputs, context)

            if not result.get("result"):
                print(f"ERROR: {result.get('error')}")
            else:
                page = result.get("data", {})
                print(f"SUCCESS: Page deleted (HTTP 202 - Processing)")
                print(f"ID: {page.get('id')}")
                print(f"Request ID: {page.get('requestId', 'N/A')}")

            return result
        except Exception as e:
            print(f"Error testing delete_page: {e}")
            return None

async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CODA INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\nNOTE: Replace 'your_api_token_here' with actual API token")
    print("Get token from: https://coda.io/account")
    print("=" * 60)

    # Run all doc tests
    await test_list_docs()
    await test_list_docs_with_filters()
    await test_list_docs_with_query()
    await test_get_doc()
    await test_create_doc()
    await test_create_doc_from_source()
    await test_list_published_docs()
    await test_list_starred_docs()

    # Run all page tests
    await test_list_pages()
    await test_get_page()
    await test_create_page()
    await test_create_page_with_content()
    await test_update_page()
    await test_delete_page()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
