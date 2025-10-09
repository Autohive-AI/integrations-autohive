const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function testAutoLayoutMode() {
  console.log('Test 1: Auto-layout mode (single markdown document)...');

  // Create base presentation
  const createInputs = {
    title: 'Auto-Layout Test',
    slides: [
      { markdown: '# Auto-Layout Mode Test\n\nDemonstrates vertical flow layout' }
    ]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Add content using auto-layout mode
    const addInputs = {
      slide_index: 0,
      auto_layout: true,
      markdown: `# Executive Summary

## Market Overview

The market has shown **strong growth** in Q4 2024 with *significant momentum* heading into 2025.

## Key Findings

- Revenue increased by 35% year-over-year
- Customer base grew to 10,000+ users
- Market share expanded to 18%
- Net Promoter Score improved to 72

## Financial Performance

| Quarter | Revenue | Profit | Margin |
|---------|---------|--------|--------|
| Q1 2024 | $2.5M   | $500K  | 20%    |
| Q2 2024 | $3.1M   | $650K  | 21%    |
| Q3 2024 | $3.8M   | $800K  | 21%    |
| Q4 2024 | $4.5M   | $1.0M  | 22%    |

> **Note:** All figures are preliminary and subject to audit

## Next Steps

1. Expand to new geographic markets
2. Launch next-generation product
3. Increase R&D investment by 25%
4. Hire 50 new team members

## Code Snippet

\`\`\`
function calculateGrowth(current, previous) {
  return ((current - previous) / previous) * 100;
}
\`\`\`

## Conclusion

With __strong fundamentals__ and \`excellent execution\`, we're well-positioned for 2025.`
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('✓ Auto-layout content added');
    console.log('  - Mode:', result.mode);
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_autolayout_mode.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testGranularMode() {
  console.log('\nTest 2: Granular mode (positioned elements)...');

  const createInputs = {
    title: 'Granular Mode Test',
    slides: [{ markdown: '# Granular Mode Test\n\nPrecise element positioning' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Add content with specific positions
    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '# Product Roadmap 2025',
          position: { x: 0.5, y: 0.5, w: 9, h: 1 }
        },
        {
          content: `**Q1 Goals:**
- Launch mobile app
- Reach 1,000 beta users
- Complete security audit

**Q2 Goals:**
- Add AI features
- Expand to EU market
- Achieve SOC2 compliance`,
          position: { x: 0.5, y: 2, w: 4, h: 3.5 }
        },
        {
          content: `| Quarter | Budget | Team Size | Status |
|---------|--------|-----------|--------|
| Q1 | $500K | 25 | ✓ On Track |
| Q2 | $750K | 30 | Planning |
| Q3 | $600K | 35 | Planning |
| Q4 | $800K | 40 | Planning |`,
          position: { x: 5, y: 2, w: 4.5, h: 3.5 }
        },
        {
          content: '> **Strategic Priority:** Focus on product-market fit before scaling',
          position: { x: 0.5, y: 6, w: 9, h: 0.8 }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('✓ Granular content added');
    console.log('  - Mode:', result.mode);
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_granular_mode.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testHTMLTableMode() {
  console.log('\nTest 3: HTML table mode (direct conversion)...');

  const createInputs = {
    title: 'HTML Table Test',
    slides: [{ markdown: '# HTML Table Mode\n\nDirect HTML to PowerPoint conversion' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Add HTML table directly (PPTXgenJS native feature)
    const htmlTable = `
      <table>
        <thead>
          <tr>
            <th>Employee</th>
            <th>Department</th>
            <th>Salary</th>
            <th>Performance</th>
            <th>Bonus</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Smith</td>
            <td>Engineering</td>
            <td>$120,000</td>
            <td>Exceeds</td>
            <td>$15,000</td>
          </tr>
          <tr>
            <td>Jane Doe</td>
            <td>Sales</td>
            <td>$95,000</td>
            <td>Exceeds</td>
            <td>$20,000</td>
          </tr>
          <tr>
            <td>Bob Johnson</td>
            <td>Marketing</td>
            <td>$85,000</td>
            <td>Meets</td>
            <td>$8,500</td>
          </tr>
          <tr>
            <td>Alice Williams</td>
            <td>Operations</td>
            <td>$90,000</td>
            <td>Exceeds</td>
            <td>$12,000</td>
          </tr>
          <tr>
            <td>Charlie Brown</td>
            <td>Finance</td>
            <td>$110,000</td>
            <td>Meets</td>
            <td>$11,000</td>
          </tr>
        </tbody>
      </table>
    `;

    const addInputs = {
      slide_index: 0,
      html_table: htmlTable
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('✓ HTML table added');
    console.log('  - Mode:', result.mode);
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_html_table_mode.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testMixedContentTypes() {
  console.log('\nTest 4: Mixed content types (auto-detection)...');

  const createInputs = {
    title: 'Content Type Detection',
    slides: [{ markdown: '# Content Type Auto-Detection' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Mix different content types - library should auto-detect
    const addInputs = {
      slide_index: 0,
      elements: [
        {
          // Auto-detected as TEXT
          content: 'This is **plain text** with *formatting* and __underlines__ and `code`.',
          position: { x: 0.5, y: 1, w: 9, h: 0.8 }
        },
        {
          // Auto-detected as BULLETS
          content: `- First bullet with **bold**
- Second bullet with *italic*
  - Nested bullet point
  - Another nested point
- Third bullet with \`code\``,
          position: { x: 0.5, y: 2.2, w: 4, h: 2.5 }
        },
        {
          // Auto-detected as TABLE
          content: `| Metric | Value | Change |
|--------|-------|--------|
| Users | 10,000 | +25% |
| Revenue | $5M | +35% |
| Profit | $1M | +45% |`,
          position: { x: 5, y: 2.2, w: 4.5, h: 2.5 }
        },
        {
          // Auto-detected as TEXT (numbered list becomes bullets)
          content: `1. First step in process
2. Second step in process
3. Third step in process
4. Fourth step in process`,
          position: { x: 0.5, y: 5.2, w: 9, h: 1.5 }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('✓ Mixed content types added');
    console.log('  - Mode:', result.mode);
    console.log('  - Elements added:', result.elements_added);
    console.log('  - All types auto-detected from markdown!');

    const outputPath = path.join(outputDir, 'test_mixed_content_types.pptx');
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
  console.log('=== Testing add_content Action (3 Modes) ===\n');

  try {
    await testAutoLayoutMode();
    await testGranularMode();
    await testHTMLTableMode();
    await testMixedContentTypes();

    console.log('\n=== All add_content tests passed! ===');
    console.log('💡 Highlights:');
    console.log('   - Auto-layout: Perfect for full-page content');
    console.log('   - Granular: Precise control over positioning');
    console.log('   - HTML table: Fast direct conversion');
    console.log('   - Auto-detection: Markdown → correct element type');
  } catch (error) {
    console.error('\n=== Tests failed ===');
    process.exit(1);
  }
}

if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
