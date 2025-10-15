# Test get_element_styling action
import asyncio
import os
import base64
from context import slide_maker
from autohive_integrations_sdk import ExecutionContext

def load_presentation_file(file_path):
    """Load a PowerPoint file and convert to base64 for testing"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Presentation file not found: {file_path}")

    with open(file_path, 'rb') as f:
        file_content = f.read()

    content_base64 = base64.b64encode(file_content).decode('utf-8')
    filename = os.path.basename(file_path)

    return {
        "name": filename,
        "contentType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "content": content_base64
    }

async def test_table_styling_extraction(file_path, slide_index=10, element_index=1):
    """Test styling extraction on a specific table element"""
    print(f"Testing table styling extraction...")
    print(f"File: {file_path}")
    print(f"Slide: {slide_index} (0-based)")
    print(f"Element: {element_index}")
    print("=" * 50)

    try:
        # Load the presentation file
        file_data = load_presentation_file(file_path)
        presentation_id = "test-styling-extraction"

        auth = {}
        async with ExecutionContext(auth=auth) as context:

            # First, inspect the slide to see what elements are available
            print("🔍 Inspecting slide elements...")
            inspect_inputs = {
                "presentation_id": presentation_id,
                "slide_index": slide_index,
                "files": [file_data]
            }

            slide_result = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)

            print(f"✅ Slide {slide_index} inspection:")
            print(f"   Total elements: {slide_result['total_elements']}")
            print(f"   Layout status: {slide_result['layout_status']}")

            if slide_result['total_elements'] == 0:
                print("❌ No elements found on this slide!")
                return

            print("\n📋 Available elements:")
            for i, element in enumerate(slide_result['elements']):
                pos = element['position']
                print(f"   [{i}] {element['type']} at ({pos['left']:.1f}, {pos['top']:.1f}) - {pos['width']:.1f}×{pos['height']:.1f}")
                if 'content' in element and element['content']:
                    content_preview = element['content'][:50] + "..." if len(element['content']) > 50 else element['content']
                    print(f"       Content: \"{content_preview}\"")

            # Check if requested element exists
            if element_index >= len(slide_result['elements']):
                print(f"\n❌ Element index {element_index} out of range!")
                print(f"   Available elements: 0-{len(slide_result['elements'])-1}")
                return

            target_element = slide_result['elements'][element_index]
            print(f"\n🎯 Target element: {target_element['type']} at index {element_index}")

            # Now extract styling information
            print(f"\n🎨 Extracting styling information...")
            styling_inputs = {
                "presentation_id": presentation_id,
                "slide_index": slide_index,
                "element_index": element_index,
                "files": [file_data]
            }

            styling_result = await slide_maker.execute_action("get_element_styling", styling_inputs, context)

            print(f"✅ Styling extraction result:")
            print(f"   Element type: {styling_result['element_type']}")
            print(f"   Position: {styling_result['position']}")
            print(f"\n📝 Styling description:")
            print("-" * 30)
            print(styling_result['styling_description'])
            print("-" * 30)

            return styling_result

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_multiple_elements(file_path, slide_index=10):
    """Test styling extraction on multiple elements from the same slide"""
    print(f"\n🔄 Testing multiple elements on slide {slide_index}...")

    try:
        file_data = load_presentation_file(file_path)
        presentation_id = "test-multi-styling"

        auth = {}
        async with ExecutionContext(auth=auth) as context:

            # Get all elements on the slide
            inspect_inputs = {
                "presentation_id": presentation_id,
                "slide_index": slide_index,
                "files": [file_data]
            }

            slide_result = await slide_maker.execute_action("get_slide_elements", inspect_inputs, context)

            print(f"Found {slide_result['total_elements']} elements")

            # Extract styling for each element
            for i in range(min(slide_result['total_elements'], 5)):  # Limit to first 5 elements
                element = slide_result['elements'][i]
                print(f"\n--- Element {i} ({element['type']}) ---")

                styling_inputs = {
                    "presentation_id": presentation_id,
                    "slide_index": slide_index,
                    "element_index": i,
                    "files": [file_data]
                }

                styling_result = await slide_maker.execute_action("get_element_styling", styling_inputs, context)

                # Print compact styling info
                styling_lines = styling_result['styling_description'].split('\n')
                for line in styling_lines[:8]:  # Show first 8 lines
                    if line.strip():
                        print(f"   {line}")

                if len(styling_lines) > 8:
                    print("   ...")

    except Exception as e:
        print(f"❌ Multiple elements test failed: {e}")

async def main():
    print("Testing Element Styling Extraction")
    print("==================================")

    # You need to provide the path to your PowerPoint file
    # Update this path to point to your actual file
    file_path = input("Enter path to PowerPoint file (or press Enter for demo): ").strip()

    if not file_path:
        print("No file path provided. Please run with a PowerPoint file:")
        print("  python test_element_styling.py")
        print("Then enter the full path to your .pptx file when prompted.")
        return

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Get slide index (default to 10 for slide 11)
    slide_input = input("Enter slide index (0-based, default 10 for slide 11): ").strip()
    slide_index = int(slide_input) if slide_input.isdigit() else 10

    # Get element index (default to 1)
    element_input = input("Enter element index to analyze (default 1): ").strip()
    element_index = int(element_input) if element_input.isdigit() else 1

    try:
        # Test specific element
        result = await test_table_styling_extraction(file_path, slide_index, element_index)

        if result:
            # Test multiple elements
            await test_multiple_elements(file_path, slide_index)

        print("\n✅ Element styling tests completed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())