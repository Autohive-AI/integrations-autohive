"""
Test Google Fonts auto-download functionality.
Requests fonts that aren't in local directory to verify auto-download works.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_maker import get_font_path

print("=" * 70)
print("GOOGLE FONTS AUTO-DOWNLOAD TEST")
print("=" * 70)

# Test cases: Commercial fonts that should map to Google Fonts
test_fonts = [
    ("Sofia Pro Light", "Should download Poppins Light"),
    ("Helvetica Neue", "Should download Roboto"),
    ("Proxima Nova Bold", "Should download Montserrat Bold"),
    ("Avenir", "Should download Nunito Sans"),
    ("Gotham", "Should download Montserrat"),
]

print("\nTesting auto-download for commercial fonts...")
print("(First run will download from Google Fonts, subsequent runs use cache)\n")

for font_name, expected in test_fonts:
    print(f"Testing: {font_name}")
    print(f"  Expected: {expected}")

    font_path = get_font_path(font_name)

    if font_path:
        if os.path.exists(font_path):
            file_size = os.path.getsize(font_path)
            print(f"  [OK] Downloaded to: {os.path.basename(font_path)}")
            print(f"  [OK] File size: {file_size / 1024:.1f} KB")
        else:
            print(f"  [FAIL] Path returned but file doesn't exist: {font_path}")
    else:
        print(f"  [FAIL] Could not download or find alternative")

    print()

print("=" * 70)
print("RESULTS:")
print("=" * 70)

# Check fonts directory
fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
downloaded_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') and ('Poppins' in f or 'Roboto' in f or 'Montserrat' in f or 'Nunito' in f)]

if downloaded_fonts:
    print(f"\n[OK] Downloaded {len(downloaded_fonts)} font file(s) from Google Fonts:")
    for font in downloaded_fonts:
        print(f"  - {font}")
else:
    print("\n[WARN] No fonts were downloaded - check network connection")

print("\n" + "=" * 70)
print("Next step: Use these fonts in presentations!")
print("Example: font_face='Sofia Pro Light' will now use Poppins Light")
print("=" * 70)
