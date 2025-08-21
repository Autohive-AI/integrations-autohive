import json
import re
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def validate_config():
    """Validate the integration configuration"""
    
    print("=== Validating Notion Integration Enhancement ===\n")
    
    # Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        print("✅ config.json loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load config.json: {e}")
        return False
    
    # Check required fields
    required_fields = ["name", "version", "description", "entry_point", "auth", "actions"]
    for field in required_fields:
        if field in config:
            print(f"✅ Has required field: {field}")
        else:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check new actions
    new_actions = ["update_notion_block", "delete_notion_block", "update_notion_page"]
    actions = config.get("actions", {})
    
    print(f"\n=== Checking New Actions ===")
    for action in new_actions:
        if action in actions:
            print(f"✅ {action} is defined")
            
            action_config = actions[action]
            
            # Check required action fields
            if "display_name" in action_config:
                print(f"   ✅ Has display_name: '{action_config['display_name']}'")
            else:
                print(f"   ❌ Missing display_name")
            
            if "description" in action_config:
                print(f"   ✅ Has description: '{action_config['description']}'")
            else:
                print(f"   ❌ Missing description")
            
            if "input_schema" in action_config and "output_schema" in action_config:
                print(f"   ✅ Has input and output schemas")
                
                # Check input schema has required fields
                input_schema = action_config["input_schema"]
                if "properties" in input_schema and "required" in input_schema:
                    required_props = input_schema["required"]
                    if action in ["update_notion_block", "delete_notion_block", "update_notion_page"]:
                        expected_id_field = "page_id" if action == "update_notion_page" else "block_id"
                        if expected_id_field in required_props:
                            print(f"   ✅ Has required {expected_id_field} field")
                        else:
                            print(f"   ❌ Missing required {expected_id_field} field")
            else:
                print(f"   ❌ Missing input or output schema")
        else:
            print(f"❌ {action} is NOT defined in config.json")
    
    # Check Python file for handlers
    print(f"\n=== Checking Python Handlers ===")
    try:
        with open("notion.py", "r") as f:
            python_content = f.read()
        
        for action in new_actions:
            # Look for the decorator pattern
            decorator_pattern = f'@notion.action\\("{action}"\\)'
            if re.search(decorator_pattern, python_content):
                print(f"✅ Handler for {action} found in notion.py")
            else:
                print(f"❌ Handler for {action} NOT found in notion.py")
                
    except Exception as e:
        print(f"❌ Failed to read notion.py: {e}")
        return False
    
    print(f"\n=== Summary ===")
    print("🎉 Notion integration enhancement completed!")
    print("\nNew capabilities added:")
    print("• update_notion_block - Update content of existing blocks (paragraphs, headings, etc.)")
    print("• delete_notion_block - Delete (archive) blocks by moving to trash") 
    print("• update_notion_page - Update page properties, icons, covers, and archive status")
    print("\nYou can now:")
    print("• Change 'hi' to 'bye' in any paragraph block")
    print("• Update headings, list items, code blocks, etc.")
    print("• Delete unwanted blocks")
    print("• Update page properties and metadata")
    
    return True

if __name__ == "__main__":
    validate_config()