# Run all action tests
import asyncio
import sys
import importlib.util

async def run_test_file(test_file_path, test_name):
    """Run a specific test file"""
    print(f"\n{'='*60}")
    print(f"RUNNING {test_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # Import and run the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Run the test
        await test_module.main()
        print(f"✅ {test_name} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ {test_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("SLIDE MAKER INTEGRATION - COMPREHENSIVE TEST SUITE")
    print("==================================================")
    print("Testing all actions with self-generated presentations...")
    
    # List of all test files to run
    test_files = [
        ("test_create_presentation.py", "Create Presentation Tests"),
        ("test_add_slide.py", "Add Slide Tests"),
        ("test_add_text.py", "Add Text Tests"),
        ("test_add_image.py", "Add Image Tests"),
        ("test_add_bullet_list.py", "Add Bullet List Tests"),
        ("test_get_slide_elements.py", "Get Slide Elements Tests"),
        ("test_modify_element.py", "Modify Element Tests"),
        ("test_modify_slide.py", "Modify Slide Tests"),
        ("test_delete_element.py", "Delete Element Tests"),
        ("test_backgrounds.py", "Background Tests"),
        ("test_text_controls.py", "Text Controls Tests"),
        ("test_tables_charts.py", "Tables and Charts Tests"),
        ("test_save_extract.py", "Save and Extract Tests"),
        ("test_error_messages.py", "Error Message Tests")
    ]
    
    passed_tests = 0
    total_tests = len(test_files)
    
    for test_file, test_name in test_files:
        success = await run_test_file(test_file, test_name)
        if success:
            passed_tests += 1
    
    print(f"\n{'='*60}")
    print(f"TEST SUITE SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Integration is working correctly.")
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} test(s) failed. Check output above for details.")
    
    print(f"\nSlide Maker Integration Test Suite Complete")

if __name__ == "__main__":
    asyncio.run(main())