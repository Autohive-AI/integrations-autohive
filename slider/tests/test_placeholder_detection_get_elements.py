"""
Test that get_slide_elements returns placeholder detection fields.
"""

import asyncio
import sys
import os
import base64
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import slide_maker
from autohive_integrations_sdk import ExecutionContext

async def test():
    auth = {}

    # Load template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'HK Template Real.pptx')
    with open(template_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    files = [{
        'name': 'HK Template Real.pptx',
        'contentType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'content': content
    }]

    async with ExecutionContext(auth=auth) as context:
        result = await slide_maker.execute_action(
            'create_presentation',
            {'files': files},
            context
        )

        presentation_id = result['presentation_id']
        files = [result['file']]

        print('Testing get_slide_elements with placeholder detection...')
        print()

        # Get ALL slides (omit slide_index)
        result = await slide_maker.execute_action(
            'get_slide_elements',
            {
                'presentation_id': presentation_id,
                'files': files,
                'include_content': True
            },
            context
        )

        print(f'Total slides: {result["total_slides"]}')
        print(f'Total elements: {result["total_elements"]}')
        print()

        # Find elements with placeholders
        fillable_count = 0
        for slide in result['slides']:
            for elem in slide['elements']:
                if elem.get('is_fillable'):
                    fillable_count += 1
                    print(f'Slide {slide["slide_index"]}, Element {elem["index"]}:')
                    print(f'  Content: {elem.get("content", "")[:60]}...')
                    print(f'  is_fillable: {elem.get("is_fillable")}')
                    print(f'  placeholders: {elem.get("placeholders")}')
                    if elem.get('placeholder_metadata'):
                        print(f'  metadata: {elem.get("placeholder_metadata")}')
                    print()

        print(f'Total fillable elements found: {fillable_count}')

        if fillable_count == 0:
            print()
            print('[ERROR] No fillable elements detected!')
            print('Checking first few elements to debug:')
            print()
            for i, elem in enumerate(result['slides'][0]['elements'][:3]):
                print(f'Element {i}:')
                print(f'  Keys: {list(elem.keys())}')
                print(f'  Content: {elem.get("content", "")[:60]}')
                print()

asyncio.run(test())
