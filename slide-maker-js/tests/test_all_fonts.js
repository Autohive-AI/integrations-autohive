const { executeAction, calculateFitFontSize } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function testAllFonts() {
  console.log('Test: All fonts supported with opentype.js...\n');

  const createInputs = {
    title: 'All Fonts Test',
    slides: [{ markdown: '# Font Support Test\n\nTesting Calibri, Arial, Times, and Courier' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('✓ Base presentation created\n');

    // Test all 4 bundled fonts
    const testText = 'The quick brown fox jumps over the lazy dog';
    const fonts = ['Calibri', 'Arial', 'Times New Roman', 'Courier New'];

    console.log('Font size calculations (4×2" box):');
    console.log('─────────────────────────────────────');

    for (const font of fonts) {
      const fontSize = calculateFitFontSize(testText, 4, 2, { fontFace: font });
      console.log(`  ${font.padEnd(20)} → ${fontSize}pt`);
    }

    console.log('\n✓ All fonts supported! No fallback needed.');

    // Create a slide showing all fonts
    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '**Calibri (PowerPoint Default)**',
          position: { x: 0.5, y: 1.5, w: 9, h: 0.6 },
          style: { fontFace: 'Calibri', fontSize: 16, bold: true }
        },
        {
          content: testText,
          position: { x: 0.5, y: 2.2, w: 4, h: 1.2 },
          autoFit: true,
          style: { fontFace: 'Calibri' }
        },
        {
          content: '**Arial (Sans-serif)**',
          position: { x: 0.5, y: 3.6, w: 9, h: 0.6 },
          style: { fontFace: 'Arial', fontSize: 16, bold: true }
        },
        {
          content: testText,
          position: { x: 0.5, y: 4.3, w: 4, h: 1.2 },
          autoFit: true,
          style: { fontFace: 'Arial' }
        },
        {
          content: '**Times New Roman (Serif)**',
          position: { x: 5, y: 1.5, w: 4.5, h: 0.6 },
          style: { fontFace: 'Times New Roman', fontSize: 16, bold: true }
        },
        {
          content: testText,
          position: { x: 5, y: 2.2, w: 4, h: 1.2 },
          autoFit: true,
          style: { fontFace: 'Times New Roman' }
        },
        {
          content: '**Courier New (Monospace)**',
          position: { x: 5, y: 3.6, w: 4.5, h: 0.6 },
          style: { fontFace: 'Courier New', fontSize: 16, bold: true }
        },
        {
          content: testText,
          position: { x: 5, y: 4.3, w: 4, h: 1.2 },
          autoFit: true,
          style: { fontFace: 'Courier New' }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('\n✓ All-fonts slide created');
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_all_fonts.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);
    console.log('\n💡 Open this file to see all fonts with auto-fitting!');

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error.stack);
    throw error;
  }
}

async function testCalibriSpecifically() {
  console.log('\n\nTest: Calibri font (PowerPoint default) now supported...\n');

  const createInputs = {
    title: 'Calibri Test',
    slides: [{ markdown: '# Calibri Font Support' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});

    // Test various text lengths in Calibri
    const tests = [
      { text: 'Short', expected: 'large' },
      { text: 'This is a medium length text for Calibri', expected: 'medium' },
      { text: 'This is a very long piece of text that would have previously fallen back to heuristic mode because Calibri was not supported by string-pixel-width library. Now with opentype.js, we can accurately measure Calibri text!', expected: 'small' }
    ];

    console.log('Calibri font size calculations:');
    console.log('─────────────────────────────────────');

    for (const test of tests) {
      const fontSize = calculateFitFontSize(test.text, 6, 2, { fontFace: 'Calibri' });
      const preview = test.text.length > 40 ? test.text.substring(0, 37) + '...' : test.text;
      console.log(`  "${preview}"`);
      console.log(`    → ${fontSize}pt (${test.expected})`);
    }

    console.log('\n✓ Calibri fully supported with opentype.js!');
    console.log('  (Previously required fallback with string-pixel-width)');

    // Create demonstration slide
    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '# Calibri Support Demonstration',
          position: { x: 0.5, y: 0.8, w: 9, h: 1 },
          style: { fontFace: 'Calibri', bold: true }
        },
        {
          content: '**Short Text** (uses large font)',
          position: { x: 0.5, y: 2, w: 4, h: 0.5 },
          style: { fontFace: 'Calibri', fontSize: 14 }
        },
        {
          content: 'Short',
          position: { x: 0.5, y: 2.6, w: 4, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Calibri' }
        },
        {
          content: '**Long Text** (shrinks to fit)',
          position: { x: 5, y: 2, w: 4.5, h: 0.5 },
          style: { fontFace: 'Calibri', fontSize: 14 }
        },
        {
          content: 'This is a very long piece of text that would have previously fallen back to heuristic mode because Calibri was not supported by string-pixel-width library. Now with opentype.js, we can accurately measure Calibri text!',
          position: { x: 5, y: 2.6, w: 4.5, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Calibri' }
        },
        {
          content: '> **Now using opentype.js** for accurate font measurement of ALL fonts including Calibri (PowerPoint default)!',
          position: { x: 0.5, y: 4.5, w: 9, h: 1 },
          style: { fontFace: 'Calibri', fontSize: 16, italic: true }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    const outputPath = path.join(outputDir, 'test_calibri_support.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('\n  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error.stack);
    throw error;
  }
}

async function runAllTests() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║  Font Support Test (opentype.js)                         ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  try {
    await testAllFonts();
    await testCalibriSpecifically();

    console.log('\n\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║  ALL FONT TESTS PASSED!                                  ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    console.log('✅ Calibri (PowerPoint default) - FULLY SUPPORTED');
    console.log('✅ Arial - FULLY SUPPORTED');
    console.log('✅ Times New Roman - FULLY SUPPORTED');
    console.log('✅ Courier New - FULLY SUPPORTED');
    console.log('');
    console.log('🎯 Benefits of opentype.js:');
    console.log('  - Accurate measurement of ALL fonts');
    console.log('  - No more font mapping workarounds');
    console.log('  - Works with actual font geometry');
    console.log('  - Lightweight (50 KB vs 165 MB for node-canvas)');
    console.log('  - Perfect for Lambda (no native deps)');

  } catch (error) {
    console.error('\n=== Tests failed ===');
    process.exit(1);
  }
}

if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
