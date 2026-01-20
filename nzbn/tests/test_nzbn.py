import asyncio
from context import nzbn
from autohive_integrations_sdk import ExecutionContext

TEST_AUTH = {
    "credentials": {
        "subscription_key": "your_subscription_key_here",
        "use_sandbox": True
    }
}


async def test_search_entities():
    """Test searching for entities."""
    print("\nTesting search_entities...")
    
    inputs = {"search_term": "Xero", "page_size": 5}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("search_entities", inputs, context)
            
            assert "result" in result
            if result.get("result"):
                assert "items" in result
                assert "totalItems" in result
                print(f"   [OK] Found {result.get('totalItems', 0)} entities")
                if result.get("items"):
                    entity = result["items"][0]
                    print(f"   First result: {entity.get('entityName', 'N/A')}")
            else:
                print(f"   [INFO] Search returned error: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_search_entities_with_filters():
    """Test searching with entity type filter."""
    print("\nTesting search_entities with filters...")
    
    inputs = {
        "search_term": "Limited",
        "entity_type": "LTD",
        "entity_status": "Registered",
        "page_size": 3
    }
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("search_entities", inputs, context)
            assert "result" in result
            print(f"   [OK] Search with filters completed")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_search_entities_missing_term():
    """Test search without search term."""
    print("\nTesting search_entities without search term...")
    
    inputs = {}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("search_entities", inputs, context)
            assert result.get("result") is False
            assert "required" in result.get("error", "").lower()
            print(f"   [OK] Correctly returned error for missing search term")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity():
    """Test getting entity details."""
    print("\nTesting get_entity...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity", inputs, context)
            
            if result.get("result"):
                assert "entity" in result
                entity = result["entity"]
                print(f"   [OK] Got entity: {entity.get('entityName', 'N/A')}")
            else:
                print(f"   [INFO] Get entity returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_missing_nzbn():
    """Test get entity without NZBN."""
    print("\nTesting get_entity without NZBN...")
    
    inputs = {}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity", inputs, context)
            assert result.get("result") is False
            assert "required" in result.get("error", "").lower()
            print(f"   [OK] Correctly returned error for missing NZBN")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_addresses():
    """Test getting entity addresses."""
    print("\nTesting get_entity_addresses...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity_addresses", inputs, context)
            
            if result.get("result"):
                assert "addresses" in result
                print(f"   [OK] Got {len(result.get('addresses', []))} addresses")
            else:
                print(f"   [INFO] Get addresses returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_roles():
    """Test getting entity roles."""
    print("\nTesting get_entity_roles...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity_roles", inputs, context)
            
            if result.get("result"):
                assert "roles" in result
                print(f"   [OK] Got {len(result.get('roles', []))} roles")
            else:
                print(f"   [INFO] Get roles returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_trading_names():
    """Test getting entity trading names."""
    print("\nTesting get_entity_trading_names...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity_trading_names", inputs, context)
            
            if result.get("result"):
                assert "tradingNames" in result
                print(f"   [OK] Got {len(result.get('tradingNames', []))} trading names")
            else:
                print(f"   [INFO] Get trading names returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_company_details():
    """Test getting company details."""
    print("\nTesting get_company_details...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_company_details", inputs, context)
            
            if result.get("result"):
                assert "companyDetails" in result
                print(f"   [OK] Got company details")
            else:
                print(f"   [INFO] Get company details returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_gst_numbers():
    """Test getting entity GST numbers."""
    print("\nTesting get_entity_gst_numbers...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity_gst_numbers", inputs, context)
            
            if result.get("result"):
                assert "gstNumbers" in result
                print(f"   [OK] Got {len(result.get('gstNumbers', []))} GST numbers")
            else:
                print(f"   [INFO] Get GST numbers returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_entity_industry_classifications():
    """Test getting entity industry classifications."""
    print("\nTesting get_entity_industry_classifications...")
    
    inputs = {"nzbn": "9429041525746"}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_entity_industry_classifications", inputs, context)
            
            if result.get("result"):
                assert "industryClassifications" in result
                print(f"   [OK] Got {len(result.get('industryClassifications', []))} classifications")
            else:
                print(f"   [INFO] Get industry classifications returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_changes():
    """Test getting recent changes."""
    print("\nTesting get_changes...")
    
    inputs = {
        "change_event_type": "NewRegistration",
        "page_size": 5
    }
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_changes", inputs, context)
            
            if result.get("result"):
                assert "changes" in result
                print(f"   [OK] Got {len(result.get('changes', []))} change events")
            else:
                print(f"   [INFO] Get changes returned: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def test_get_changes_missing_event_type():
    """Test get changes without event type."""
    print("\nTesting get_changes without event type...")
    
    inputs = {}
    
    async with ExecutionContext(auth=TEST_AUTH) as context:
        try:
            result = await nzbn.execute_action("get_changes", inputs, context)
            assert result.get("result") is False
            assert "required" in result.get("error", "").lower()
            print(f"   [OK] Correctly returned error for missing event type")
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            raise


async def main():
    print("=" * 60)
    print("Testing NZBN Integration")
    print("=" * 60)
    print("\nNote: Replace 'your_subscription_key_here' with a real key")
    print("      to test against the actual NZBN API.\n")
    
    await test_search_entities_missing_term()
    await test_get_entity_missing_nzbn()
    await test_get_changes_missing_event_type()
    
    print("\n" + "-" * 60)
    print("The following tests require a valid subscription key:")
    print("-" * 60)
    
    await test_search_entities()
    await test_search_entities_with_filters()
    await test_get_entity()
    await test_get_entity_addresses()
    await test_get_entity_roles()
    await test_get_entity_trading_names()
    await test_get_company_details()
    await test_get_entity_gst_numbers()
    await test_get_entity_industry_classifications()
    await test_get_changes()
    
    print("\n" + "=" * 60)
    print("[OK] All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
