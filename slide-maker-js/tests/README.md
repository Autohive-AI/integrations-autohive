# Test Suite

Comprehensive tests for all 4 actions in the Slide Maker JS integration.

## Running Tests

### Install Dependencies First
```bash
cd slide-maker-js
npm install
```

### Run All Tests
```bash
npm test
```

This will:
1. Run all 14 tests across 4 test suites
2. Generate PPTX files in `tests/output/`
3. Display summary with file sizes

### Run Individual Test Suites
```bash
# Test create_presentation action (3 tests)
npm run test:create

# Test generate_slides action (3 tests) - POWER FEATURE
npm run test:generate

# Test add_content action (4 tests)
npm run test:content

# Test add_chart_and_images action (4 tests)
npm run test:charts
```

## Test Coverage

### Test Suite 1: create_presentation (3 tests)
- ✓ Simple presentation
- ✓ Presentation with master slide template
- ✓ Multiple slides with various content types

**Files Generated:**
- `test_simple_presentation.pptx`
- `test_branded_presentation.pptx`
- `test_multiple_slides.pptx`

---

### Test Suite 2: generate_slides (3 tests) 🚀
The **POWER FEATURE** - generates many slides from data.

- ✓ Quarterly sales reports (4 slides from template + data)
- ✓ Product data sheets (3 slides from template + data)
- ✓ Employee profiles (20 slides from template + data)

**Files Generated:**
- `test_generated_quarterly_reports.pptx` (4 slides)
- `test_generated_product_sheets.pptx` (3 slides)
- `test_generated_20_slides.pptx` (20 slides)

**Why This Matters:**
- Traditional approach: 100+ API calls for 20 slides
- Our approach: **2 API calls** for 20 slides
- Efficiency gain: **50-100x fewer calls!**

---

### Test Suite 3: add_content (4 tests)
Tests all 3 modes of content addition.

- ✓ Auto-layout mode (vertical flow from markdown)
- ✓ Granular mode (precise positioning)
- ✓ HTML table mode (direct conversion)
- ✓ Mixed content types (auto-detection)

**Files Generated:**
- `test_autolayout_mode.pptx`
- `test_granular_mode.pptx`
- `test_html_table_mode.pptx`
- `test_mixed_content_types.pptx`

---

### Test Suite 4: add_chart_and_images (4 tests)
Tests charts and images.

- ✓ Bar chart
- ✓ Multiple chart types (bar, line, pie, area)
- ✓ Image placement
- ✓ Dashboard layout (4 charts + logo)

**Files Generated:**
- `test_bar_chart.pptx`
- `test_multiple_charts.pptx`
- `test_images.pptx`
- `test_dashboard.pptx`

---

## Verification Process

After running tests:

1. **Open the PPTX files** in Microsoft PowerPoint or compatible software
2. **Check each slide** for:
   - Content accuracy
   - Formatting (bold, italic, underline)
   - Table structure
   - Chart data
   - Image placement
   - Master slide branding (where applicable)

3. **Verify specific features:**
   - Master slides: Check footer/logo on branded presentations
   - Data generation: Verify 20+ slides have unique data
   - Auto-layout: Check vertical flow and spacing
   - Granular: Check precise positioning
   - Charts: Verify data points and labels

## Expected Output

```
╔═══════════════════════════════════════════════════════════╗
║  Slide Maker JS - Comprehensive Test Suite               ║
║  Tests all 4 actions with PPTX file generation           ║
╚═══════════════════════════════════════════════════════════╝

[... test output ...]

╔═══════════════════════════════════════════════════════════╗
║  TEST SUMMARY                                             ║
╚═══════════════════════════════════════════════════════════╝

Total tests:      14
Passed:           14 ✓
Failed:           0 ✗
Duration:         X.XXs

📄 Generated PPTX files:
   1. test_simple_presentation.pptx (X.XX MB)
   2. test_branded_presentation.pptx (X.XX MB)
   [... more files ...]

✓ All files saved to: /path/to/tests/output

💡 Open the PPTX files in PowerPoint to verify functionality!

🎉 ALL TESTS PASSED! Integration is ready to use.
```

## Test Structure

```
tests/
├── test_create_presentation.js    # Suite 1: Create presentations
├── test_generate_slides.js        # Suite 2: Data-driven generation
├── test_add_content.js            # Suite 3: Content modes
├── test_add_chart_and_images.js   # Suite 4: Charts & images
├── run_all_tests.js               # Main test runner
├── output/                        # Generated PPTX files (created on first run)
└── README.md                      # This file
```

## Troubleshooting

### Tests fail with "Cannot find module"
```bash
# Install dependencies
npm install
```

### Output directory not created
The test runner creates it automatically. If issues persist:
```bash
mkdir -p tests/output
```

### PPTX files won't open
- Ensure you have Microsoft PowerPoint or compatible software
- Check file sizes - they should be > 0 bytes
- Try opening with LibreOffice Impress or Google Slides

### Chart/Image rendering issues
This is expected - PPTXgenJS has some limitations compared to native PowerPoint. The tests verify the API works correctly, not pixel-perfect rendering.

## What Gets Tested

### ✅ Core Functionality
- Presentation creation
- Slide addition
- Content parsing (markdown → PPTX)
- Master slide templates
- Data-driven batch generation

### ✅ Markdown Features
- Headings (H1-H6)
- Bold, italic, underline, code
- Bullets (nested)
- Numbered lists
- Tables
- Blockquotes
- Code blocks

### ✅ Chart Types
- Bar charts
- Line charts
- Pie charts
- Area charts

### ✅ Layout Modes
- Auto-layout (vertical flow)
- Granular (positioned elements)
- HTML table (direct conversion)

### ✅ Advanced Features
- Master slide templates
- Template variables (Mustache)
- Multi-slide batch generation
- Mixed content types
- Auto-type detection

## Performance Metrics

Running all tests typically:
- Takes 5-15 seconds
- Generates ~15 PPTX files
- Total output size: ~5-10 MB
- Memory usage: < 200 MB

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
npm install

# Run tests (exits with code 0 on success, 1 on failure)
npm test

# Check exit code
echo $?
```

## Contributing

When adding new tests:

1. Create test file: `test_your_feature.js`
2. Export `runAllTests` function
3. Add to `run_all_tests.js`
4. Update this README
5. Verify PPTX files are generated correctly
