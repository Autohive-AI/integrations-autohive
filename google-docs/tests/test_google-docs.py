# Testbed for Google Docs integration.
import asyncio
from context import google_docs
from autohive_integrations_sdk import ExecutionContext

async def test_create_document():
    """Test creating a new document."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "title": "Test Document"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_create", inputs, context)
            print(f"Create Document Result: {result}")
        except Exception as e:
            print(f"Error testing docs_create: {e}")


async def test_get_document():
    """Test retrieving a document."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "document_id": "test_document_id",
        "include_tabs_content": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_get", inputs, context)
            print(f"Get Document Result: {result}")
        except Exception as e:
            print(f"Error testing docs_get: {e}")


async def test_insert_paragraphs():
    """Test inserting plain paragraphs."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "document_id": "test_document_id",
        "paragraphs": [
            "This is the first paragraph.",
            "This is the second paragraph.",
            "This is the third paragraph."
        ],
        "append": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_insert_paragraphs", inputs, context)
            print(f"Insert Paragraphs Result: {result}")
        except Exception as e:
            print(f"Error testing docs_insert_paragraphs: {e}")


async def test_insert_markdown_content():
    """Test inserting markdown content with automatic heading styling."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "document_id": "test_document_id",
        "content": "# Overview\n\nThis is the overview section.\n\n# Details\n\nThis section has more details.",
        "heading_level": 1,
        "append": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_insert_markdown_content", inputs, context)
            print(f"Insert Markdown Content Result: {result}")
        except Exception as e:
            print(f"Error testing docs_insert_markdown_content: {e}")


async def test_batch_update():
    """Test batch update for text formatting."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "document_id": "test_document_id",
        "requests": [
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": 10
                    },
                    "textStyle": {
                        "bold": True
                    },
                    "fields": "bold"
                }
            },
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": 10,
                        "endIndex": 20
                    },
                    "textStyle": {
                        "italic": True
                    },
                    "fields": "italic"
                }
            }
        ]
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_batch_update", inputs, context)
            print(f"Batch Update Result: {result}")
        except Exception as e:
            print(f"Error testing docs_batch_update: {e}")


async def test_parse_structure():
    """Test parsing document structure."""
    auth = {
        "credentials": {
            "access_token": "test_access_token"
        }
    }

    inputs = {
        "document_id": "test_document_id"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await google_docs.execute_action("docs_parse_structure", inputs, context)
            print(f"Parse Structure Result: {result}")
        except Exception as e:
            print(f"Error testing docs_parse_structure: {e}")


async def main():
    print("Testing Google Docs Integration")
    print("================================")
    print()

    print("1. Testing document creation...")
    await test_create_document()
    print()

    print("2. Testing document retrieval...")
    await test_get_document()
    print()

    print("3. Testing plain paragraph insertion...")
    await test_insert_paragraphs()
    print()

    print("4. Testing markdown content insertion...")
    await test_insert_markdown_content()
    print()

    print("5. Testing batch update (text formatting)...")
    await test_batch_update()
    print()

    print("6. Testing document structure parsing...")
    await test_parse_structure()
    print()

    print("================================")
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
