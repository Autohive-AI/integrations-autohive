import asyncio
import json
from typing import Dict, Any
from notion import notion

async def test_integration_config():
    """Test that the integration configuration is valid"""
    
    # Test that all actions defined in config.json have corresponding handlers
    with open("config.json", "r") as f:
        config = json.load(f)
    
    defined_actions = set(config.get("actions", {}).keys())
    
    # Get all registered action handlers from the integration
    registered_actions = set(notion._actions.keys()) if hasattr(notion, '_actions') else set()
    
    print(f"Actions defined in config.json: {defined_actions}")
    print(f"Actions registered in handlers: {registered_actions}")
    
    missing_handlers = defined_actions - registered_actions
    extra_handlers = registered_actions - defined_actions
    
    if missing_handlers:
        print(f"Missing handlers for actions: {missing_handlers}")
    
    if extra_handlers:
        print(f"Extra handlers without config: {extra_handlers}")
    
    if not missing_handlers and not extra_handlers:
        print("ll actions have matching handlers!")
        return True
    
    return False

async def test_new_actions():
    """Test that the new update/delete actions are properly configured"""
    
    new_actions = ["update_notion_block", "delete_notion_block", "update_notion_page"]
    
    with open("config.json", "r") as f:
        config = json.load(f)
    
    actions = config.get("actions", {})
    
    for action in new_actions:
        if action in actions:
            print(f"✅ {action} is defined in config.json")
            
            # Check required fields
            action_config = actions[action]
            if "display_name" in action_config and "description" in action_config:
                print(f"   - Has display_name: {action_config['display_name']}")
                print(f"   - Has description: {action_config['description']}")
            else:
                print(f"Missing display_name or description")
                
            if "input_schema" in action_config and "output_schema" in action_config:
                print(f"   - Has input and output schemas")
            else:
                print(f"Missing input or output schema")
        else:
            print(f"{action} is NOT defined in config.json")

async def main():
    """Run all tests"""
    print("=== Testing Notion Integration Enhancement ===\n")
    
    print("1. Testing integration configuration...")
    config_valid = await test_integration_config()
    print()
    
    print("2. Testing new action configurations...")
    await test_new_actions()
    print()
    
    if config_valid:
        print("Integration enhancement completed successfully!")
        print("\nNew capabilities added:")
        print("- update_notion_block: Update content of existing blocks")
        print("- delete_notion_block: Delete (archive) blocks")
        print("- update_notion_page: Update page properties, icon, cover, etc.")
    else:
        print("Integration has configuration issues that need to be fixed.")

if __name__ == "__main__":
    asyncio.run(main())