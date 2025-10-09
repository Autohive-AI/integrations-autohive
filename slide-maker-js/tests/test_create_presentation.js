const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

// Ensure output directory exists
const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function testCreateSimple() {
  console.log('Test 1: Create simple presentation...');

  const inputs = {
    title: 'Test Presentation',
    author: 'Test Suite',
    slides: [
      {
        markdown: '# Welcome\n\nThis is a test presentation created by the JavaScript integration.'
      }
    ],
    custom_filename: 'test_simple_presentation'
  };

  try {
    const result = await executeAction('create_presentation', inputs, {});

    console.log('✓ Presentation created:', result.presentation_id);
    console.log('  - Slides:', result.slide_count);
    console.log('  - Master defined:', result.master_defined);

    // Save file
    const outputPath = path.join(outputDir, result.file.name);
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testCreateWithMaster() {
  console.log('\nTest 2: Create presentation with master slide...');

  const inputs = {
    title: 'Branded Presentation',
    author: 'Test Suite',
    master: {
      title: 'TEST_BRAND',
      background: { color: 'F0F0F0' },
      objects: [
        {
          rect: {
            x: 0,
            y: 7,
            w: '100%',
            h: 0.5,
            fill: { color: '003366' }
          }
        },
        {
          text: {
            text: 'Company Confidential',
            options: {
              x: 0.5,
              y: 7.1,
              w: 3,
              h: 0.3,
              fontSize: 10,
              color: 'FFFFFF'
            }
          }
        }
      ],
      slideNumber: { x: '95%', y: '95%' }
    },
    slides: [
      {
        markdown: '# Executive Summary\n\n## Q4 2024 Results\n\n- Revenue: $10M\n- Growth: 25% YoY\n- Customer Satisfaction: 92%'
      },
      {
        markdown: '# Financial Overview\n\n| Metric | Q3 | Q4 | Change |\n|--------|----|----|--------|\n| Revenue | $8M | $10M | +25% |\n| Profit | $2M | $2.5M | +25% |\n| EBITDA | $3M | $3.8M | +27% |'
      },
      {
        markdown: '# Next Steps\n\n1. **Expand to new markets**\n2. *Hire 20 new employees*\n3. Launch product v2.0\n4. Increase marketing budget'
      }
    ],
    custom_filename: 'test_branded_presentation'
  };

  try {
    const result = await executeAction('create_presentation', inputs, {});

    console.log('✓ Branded presentation created:', result.presentation_id);
    console.log('  - Slides:', result.slide_count);
    console.log('  - Master defined:', result.master_defined);
    console.log('  - Master name:', result.master_name);

    // Save file
    const outputPath = path.join(outputDir, result.file.name);
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testCreateMultipleSlides() {
  console.log('\nTest 3: Create presentation with multiple content types...');

  const inputs = {
    title: 'Content Showcase',
    slides: [
      {
        markdown: '# Slide 1: Title\n\n## Subtitle with **bold** and *italic*'
      },
      {
        markdown: '# Slide 2: Bullets\n\n- First bullet point\n  - Nested bullet\n  - Another nested\n- Second bullet point\n- Third bullet point'
      },
      {
        markdown: '# Slide 3: Table\n\n| Product | Q1 | Q2 | Q3 | Q4 |\n|---------|----|----|----|----|  \n| Widget A | 100 | 150 | 200 | 250 |\n| Widget B | 50 | 75 | 100 | 125 |\n| Widget C | 200 | 225 | 250 | 300 |'
      },
      {
        markdown: '# Slide 4: Mixed Content\n\n## Overview\n\nThis slide has **multiple elements**:\n\n- Headings\n- Paragraphs\n- Lists\n\n> Important note: All data is confidential\n\n## Code Example\n\n```\nfunction hello() {\n  return "world";\n}\n```'
      }
    ],
    custom_filename: 'test_multiple_slides'
  };

  try {
    const result = await executeAction('create_presentation', inputs, {});

    console.log('✓ Multi-slide presentation created:', result.presentation_id);
    console.log('  - Slides:', result.slide_count);

    // Save file
    const outputPath = path.join(outputDir, result.file.name);
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function runAllTests() {
  console.log('=== Testing create_presentation Action ===\n');

  try {
    await testCreateSimple();
    await testCreateWithMaster();
    await testCreateMultipleSlides();

    console.log('\n=== All create_presentation tests passed! ===');
  } catch (error) {
    console.error('\n=== Tests failed ===');
    process.exit(1);
  }
}

// Run tests if called directly
if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
