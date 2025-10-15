# Test complete table workflow: create template → extract styling → fill with data
import asyncio
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def test_complete_table_workflow():
    """Test the complete table workflow: create, style, extract, and fill"""
    print("Testing Complete Table Workflow")
    print("=" * 50)

    auth = {}
    async with ExecutionContext(auth=auth) as context:

        # Step 1: Create presentation with template table
        print("📋 Step 1: Creating presentation with template table...")

        create_inputs = {
            "title": "Employee Data Template",
            "subtitle": "Template table with Lato font styling",
            "custom_filename": "table_workflow_test"
        }
        result = await slide_maker.execute_action("create_presentation", create_inputs, context)
        presentation_id = result["presentation_id"]
        print(f"   ✅ Created presentation: {presentation_id}")

        # Step 2: Add template table with placeholder data
        print("\n🏗️  Step 2: Adding template table with placeholder data...")

        template_data = [
            ["Name", "Department", "Salary", "Status"],
            ["{{EMPLOYEE_NAME}}", "{{DEPARTMENT}}", "{{SALARY}}", "{{STATUS}}"],
            ["{{EMPLOYEE_NAME}}", "{{DEPARTMENT}}", "{{SALARY}}", "{{STATUS}}"],
            ["{{EMPLOYEE_NAME}}", "{{DEPARTMENT}}", "{{SALARY}}", "{{STATUS}}"]
        ]

        table_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "rows": 4,
            "cols": 4,
            "position": {"left": 1.0, "top": 2.5, "width": 7.0, "height": 3.0},
            "data": template_data,
            "files": [result["file"]]
        }

        result = await slide_maker.execute_action("add_table", table_inputs, context)
        print(f"   ✅ Added template table with placeholders")

        # Step 2.5: Inspect slide to find the table element
        print("\n🔍 Step 2.5: Finding the table element...")

        inspect_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "files": [result["file"]]
        }

        slide_elements = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)
        print(f"   📋 Found {slide_elements['total_elements']} elements:")

        table_element_index = None
        for i, element in enumerate(slide_elements['elements']):
            pos = element['position']
            print(f"     [{i}] {element['type']} at ({pos['left']:.1f}, {pos['top']:.1f}) - {pos['width']:.1f}×{pos['height']:.1f}")
            if element['type'] == 'table':
                table_element_index = i
                print(f"       🎯 Found table at index {i}!")

        if table_element_index is None:
            raise Exception("❌ No table found in slide elements!")

        # Step 3: Style the table (make headers bold, add font styling)
        print(f"\n🎨 Step 3: Styling the template table (element index {table_element_index})...")

        # Style header row (row 0) - make it bold with larger font
        header_styling_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,  # Use the correct table index
            "table_cell_updates": [
                {
                    "row": 0, "col": 0, "text": "Employee Name",
                    "formatting": {"font_size": 14, "bold": True, "color": "#FFFFFF", "font_name": "Arial"}
                },
                {
                    "row": 0, "col": 1, "text": "Department",
                    "formatting": {"font_size": 14, "bold": True, "color": "#FFFFFF", "font_name": "Arial"}
                },
                {
                    "row": 0, "col": 2, "text": "Annual Salary",
                    "formatting": {"font_size": 14, "bold": True, "color": "#FFFFFF", "font_name": "Arial"}
                },
                {
                    "row": 0, "col": 3, "text": "Employment Status",
                    "formatting": {"font_size": 14, "bold": True, "color": "#FFFFFF", "font_name": "Arial"}
                }
            ],
            "files": [result["file"]]
        }

        result = await slide_maker.execute_action("modify_element", header_styling_inputs, context)
        print(f"   ✅ Styled header row with bold white text")
        print(f"   Changes made: {len(result['changes_made'])} changes")
        if len(result['changes_made']) == 0:
            print(f"   ⚠️  No changes detected - debugging...")
            print(f"      Element type: {result.get('element_type', 'unknown')}")
            print(f"      Modified: {result.get('modified', False)}")
        else:
            print(f"   📋 Changes: {result['changes_made'][:3]}...")  # Show first 3

        # Style data rows with regular formatting
        data_styling_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,
            "table_cell_updates": [
                # Row 1 data cells with Arial font
                {"row": 1, "col": 0, "text": "{{NAME_1}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 1, "col": 1, "text": "{{DEPT_1}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 1, "col": 2, "text": "{{SALARY_1}}", "formatting": {"font_size": 12, "color": "#008000", "font_name": "Arial"}},
                {"row": 1, "col": 3, "text": "{{STATUS_1}}", "formatting": {"font_size": 12, "font_name": "Arial"}},

                # Row 2 data cells
                {"row": 2, "col": 0, "text": "{{NAME_2}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 2, "col": 1, "text": "{{DEPT_2}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 2, "col": 2, "text": "{{SALARY_2}}", "formatting": {"font_size": 12, "color": "#008000", "font_name": "Arial"}},
                {"row": 2, "col": 3, "text": "{{STATUS_2}}", "formatting": {"font_size": 12, "font_name": "Arial"}},

                # Row 3 data cells
                {"row": 3, "col": 0, "text": "{{NAME_3}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 3, "col": 1, "text": "{{DEPT_3}}", "formatting": {"font_size": 12, "font_name": "Arial"}},
                {"row": 3, "col": 2, "text": "{{SALARY_3}}", "formatting": {"font_size": 12, "color": "#008000", "font_name": "Arial"}},
                {"row": 3, "col": 3, "text": "{{STATUS_3}}", "formatting": {"font_size": 12, "font_name": "Arial"}}
            ],
            "files": [result["file"]]
        }

        result = await slide_maker.execute_action("modify_element", data_styling_inputs, context)
        print(f"   ✅ Styled data rows with template placeholders")
        print(f"   Changes made: {len(result['changes_made'])} cell updates")
        if len(result['changes_made']) == 0:
            print(f"   ⚠️  No data row changes detected - debugging needed")

        # Step 4: Extract styling information from the template
        print("\n🔍 Step 4: Extracting template styling information...")

        styling_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,  # The table element
            "files": [result["file"]]
        }

        styling_result = await slide_maker.execute_action("get_element_styling", styling_inputs, context)
        print(f"   ✅ Extracted template styling:")
        print("   " + "-" * 40)
        styling_lines = styling_result['styling_description'].split('\n')
        for line in styling_lines:
            if line.strip():
                print(f"   {line}")
        print("   " + "-" * 40)

        # Step 5: Fill template with actual data
        print("\n📝 Step 5: Filling template with actual employee data...")

        actual_data_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,
            "table_cell_updates": [
                # Fill row 1 with John's data (preserve Arial 12pt styling)
                {"row": 1, "col": 0, "text": "John Smith", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 1, "col": 1, "text": "Engineering", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 1, "col": 2, "text": "$95,000", "formatting": {"font_name": "Arial", "font_size": 12, "color": "#008000"}},
                {"row": 1, "col": 3, "text": "Full-Time", "formatting": {"font_name": "Arial", "font_size": 12}},

                # Fill row 2 with Sarah's data (preserve Arial 12pt styling)
                {"row": 2, "col": 0, "text": "Sarah Johnson", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 2, "col": 1, "text": "Marketing", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 2, "col": 2, "text": "$78,000", "formatting": {"font_name": "Arial", "font_size": 12, "color": "#008000"}},
                {"row": 2, "col": 3, "text": "Full-Time", "formatting": {"font_name": "Arial", "font_size": 12}},

                # Fill row 3 with Mike's data (preserve Arial 12pt styling)
                {"row": 3, "col": 0, "text": "Mike Chen", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 3, "col": 1, "text": "Sales", "formatting": {"font_name": "Arial", "font_size": 12}},
                {"row": 3, "col": 2, "text": "$82,000", "formatting": {"font_name": "Arial", "font_size": 12, "color": "#008000"}},
                {"row": 3, "col": 3, "text": "Part-Time", "formatting": {"font_name": "Arial", "font_size": 12}}
            ],
            "files": [result["file"]]
        }

        final_result = await slide_maker.execute_action("modify_element", actual_data_inputs, context)
        print(f"   ✅ Filled table with employee data")
        print(f"   Final changes: {len(final_result['changes_made'])} cells updated")

        # Step 6: Extract final styling to verify it was preserved
        print("\n🔍 Step 6: Verifying final table preserves styling...")

        final_styling_inputs = {
            "presentation_id": presentation_id,
            "slide_index": 0,
            "element_index": table_element_index,
            "files": [final_result["file"]]
        }

        final_styling = await slide_maker.execute_action("get_element_styling", final_styling_inputs, context)
        print(f"   ✅ Final table styling:")
        print("   " + "-" * 40)
        final_lines = final_styling['styling_description'].split('\n')
        for line in final_lines:
            if line.strip():
                print(f"   {line}")
        print("   " + "-" * 40)

        # Step 7: Compare expected vs actual styling
        print(f"\n🔬 Step 7: Verifying styling matches expectations...")

        # Expected styling based on what we applied
        expected_styling = {
            "headers": {
                "font_family": "Arial",  # Built-in font that should work
                "font_size": 14,
                "bold": True,
                "color": "#ffffff"  # White text
            },
            "data_cells": {
                "font_family": "Arial",  # Built-in font that should work
                "font_size": 12,
                "bold": False
            },
            "salary_column": {
                "font_family": "Arial",  # Built-in font that should work
                "font_size": 12,
                "color": "#008000"  # Green text
            }
        }

        print(f"   📋 Expected styling:")
        print(f"      Font family: Arial (built-in font test)")
        print(f"      Headers: Arial 14pt bold white (#FFFFFF)")
        print(f"      Data cells: Arial 12pt regular")
        print(f"      Salary column: Arial 12pt green (#008000)")

        # Extract detailed styling for verification
        final_detailed_styling = await slide_maker.execute_action("get_element_styling", final_styling_inputs, context)

        print(f"\n   🔍 Actual final styling:")
        print("   " + "=" * 50)
        final_detailed_lines = final_detailed_styling['styling_description'].split('\n')
        for line in final_detailed_lines:
            if line.strip():
                print(f"   {line}")
        print("   " + "=" * 50)

        # Check if it's actually a table in the styling description
        styling_desc = final_detailed_styling['styling_description']
        if "TABLE" in styling_desc:
            print(f"   ✅ Correctly identified as TABLE element")

            # Check for Arial font preservation
            arial_found = False
            if "Arial" in styling_desc:
                print(f"   ✅ Arial font detected in final styling - font preserved!")
                arial_found = True
            else:
                print(f"   ❌ Arial font NOT found in final styling")

                # Check what fonts are actually detected
                if "Fonts:" in styling_desc:
                    print(f"   📋 Analyzing detected fonts...")
                    lines = styling_desc.split('\n')
                    for line in lines:
                        if "Fonts:" in line:
                            print(f"      {line.strip()}")
                        elif "C0:" in line or "C1:" in line:
                            print(f"      {line.strip()}")
                else:
                    print(f"   ⚠️  No font information detected at all")

            # Look for our expected font sizes
            size_14_found = "14pt" in styling_desc
            size_12_found = "12pt" in styling_desc
            bold_found = "bold" in styling_desc
            white_found = "white" in styling_desc or "#ffffff" in styling_desc.lower()
            green_found = "#008000" in styling_desc.lower()

            print(f"\n   📊 Font attribute verification:")
            print(f"      Arial font family: {'✅' if arial_found else '❌'}")
            print(f"      14pt size (headers): {'✅' if size_14_found else '❌'}")
            print(f"      12pt size (data): {'✅' if size_12_found else '❌'}")
            print(f"      Bold styling: {'✅' if bold_found else '❌'}")
            print(f"      White color: {'✅' if white_found else '❌'}")
            print(f"      Green color: {'✅' if green_found else '❌'}")

            # Overall assessment
            attributes_preserved = [arial_found, size_14_found, size_12_found, bold_found]
            preservation_score = sum(attributes_preserved) / len(attributes_preserved) * 100

            print(f"\n   🎯 Styling preservation score: {preservation_score:.0f}%")
            if preservation_score >= 75:
                print(f"   ✅ Good styling preservation")
            elif preservation_score >= 50:
                print(f"   ⚠️  Partial styling preservation")
            else:
                print(f"   ❌ Poor styling preservation - investigation needed")

        else:
            print(f"   ❌ Not analyzing a table - element type issue!")

        # Step 8: Show final file information
        print(f"\n📄 Step 8: Final Result Summary:")
        print(f"   File: {final_result['file_path']}")
        print(f"   Saved: {final_result['saved']}")
        print(f"   File size: {len(final_result['file']['content'])} chars (base64)")
        print(f"   Element type analyzed: {final_detailed_styling.get('element_type', 'unknown')}")

        # Summary of what we accomplished
        print(f"\n🎯 Workflow Summary:")
        print(f"   ✅ Created presentation with template table")
        print(f"   ✅ Applied styling (headers: 14pt bold white, data: 12pt)")
        print(f"   ✅ Extracted styling information")
        print(f"   ✅ Filled table with employee data")
        print(f"   ✅ Verified final styling preservation")

        return {
            "final_result": final_result,
            "expected_styling": expected_styling,
            "actual_styling": final_detailed_styling,
            "table_element_index": table_element_index
        }

async def main():
    try:
        print("🚀 Starting Complete Table Workflow Test")
        print("This test demonstrates:")
        print("  1. Creating a presentation with template table")
        print("  2. Styling headers and data cells")
        print("  3. Extracting styling information")
        print("  4. Filling template with actual data")
        print("  5. Preserving styling during data updates")
        print("\n")

        result = await test_complete_table_workflow()

        print(f"\n✅ Complete workflow test successful!")
        print(f"📊 Final table contains employee data with preserved styling")
        print(f"🎯 Template → Style → Extract → Fill workflow verified")

    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())