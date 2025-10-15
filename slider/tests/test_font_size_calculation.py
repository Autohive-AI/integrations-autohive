# Test font size calculation logic
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the calculation function
import re

def calculate_best_fit_font_size(text, width_inches, height_inches, max_font_size=18):
    """Copy of the function for testing"""
    if not text or width_inches <= 0 or height_inches <= 0:
        return max_font_size

    # Remove markdown markers
    clean_text = text.replace('**', '').replace('*', '').replace('__', '').replace('`', '').replace('~~', '')
    char_count = len(clean_text)

    # Estimate characters per line
    chars_per_inch_width = 8
    usable_width = width_inches - 0.2
    chars_per_line = usable_width * chars_per_inch_width * (max_font_size / 18)

    if chars_per_line <= 0:
        return max_font_size

    # Estimate lines needed
    lines_needed = char_count / chars_per_line

    # Estimate line height
    line_height_inches = 0.25 * (max_font_size / 18)
    usable_height = height_inches - 0.1
    max_lines_that_fit = usable_height / line_height_inches

    if lines_needed <= max_lines_that_fit:
        return max_font_size

    # Calculate scaling
    scale_factor = max_lines_that_fit / lines_needed
    calculated_size = max_font_size * scale_factor

    # Min/max bounds
    min_size = 8
    final_size = max(min_size, min(calculated_size, max_font_size))

    return int(final_size), {
        'char_count': char_count,
        'chars_per_line': chars_per_line,
        'lines_needed': lines_needed,
        'max_lines_fit': max_lines_that_fit,
        'scale_factor': scale_factor,
        'calculated_size': calculated_size
    }

print("="*70)
print("FONT SIZE CALCULATION TEST")
print("="*70)

# Test cases from our actual slides
test_cases = [
    {
        'name': 'Short text in large box',
        'text': 'Short',
        'width': 3, 'height': 2,
        'max_size': 18
    },
    {
        'name': 'Short text in small box',
        'text': 'Tiny',
        'width': 1, 'height': 0.5,
        'max_size': 18
    },
    {
        'name': 'Long text in 3x1 box (Slide 3, Box 1)',
        'text': "This is a very long piece of text that should automatically size to fit within the text box boundaries using our calculation logic.",
        'width': 3, 'height': 1,
        'max_size': 18
    },
    {
        'name': 'Very long text in 4x1.5 box (Slide 3, Box 3)',
        'text': "**Test**: " + ("Word " * 50),
        'width': 4, 'height': 1.5,
        'max_size': 18
    },
    {
        'name': 'Extreme: 500 chars in 3x2 box',
        'text': "Test " * 100,
        'width': 3, 'height': 2,
        'max_size': 18
    },
    {
        'name': 'Tiny box: 0.5x0.3',
        'text': 'Minimal Box Test',
        'width': 0.5, 'height': 0.3,
        'max_size': 18
    },
    {
        'name': 'Long word in 2x0.5 box',
        'text': 'Pneumonoultramicroscopicsilicovolcanoconiosis',
        'width': 2, 'height': 0.5,
        'max_size': 18
    }
]

for test in test_cases:
    result = calculate_best_fit_font_size(
        test['text'],
        test['width'],
        test['height'],
        test['max_size']
    )

    if isinstance(result, tuple):
        size, details = result
    else:
        size = result
        details = {'note': 'No details returned'}

    print(f"\n{test['name']}:")
    print(f"  Box: {test['width']}\" x {test['height']}\"")
    print(f"  Text: {len(test['text'])} chars")
    print(f"  Calculated font size: {size}pt")
    if 'note' not in details:
        print(f"  Details:")
        print(f"    - Chars per line: {details['chars_per_line']:.1f}")
        print(f"    - Lines needed: {details['lines_needed']:.1f}")
        print(f"    - Max lines that fit: {details['max_lines_fit']:.1f}")
        if details['lines_needed'] > details['max_lines_fit']:
            print(f"    - NEEDS SHRINKING: {details['lines_needed']:.1f} lines > {details['max_lines_fit']:.1f} max")
            print(f"    - Scale factor: {details['scale_factor']:.2f}")
        else:
            print(f"    - FITS: Uses max size {test['max_size']}pt")

print("\n" + "="*70)
print("ANALYSIS:")
print("  If calculated font sizes seem too large/small, adjust:")
print("  - chars_per_inch_width (currently 8)")
print("  - line_height_inches formula (currently 0.25 * size/18)")
print("="*70)
