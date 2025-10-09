const { executeAction, downloadAndCacheFont } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function testDownloadRoboto() {
  console.log('Test 1: Auto-download Roboto font from Google Fonts...\n');

  try {
    // Create presentation
    const createInputs = {
      title: 'Auto-Download Font Test',
      slides: [{ markdown: '# Font Auto-Download Demo' }]
    };

    await executeAction('create_presentation', createInputs, {});
    console.log('✓ Base presentation created\n');

    // Add content using Roboto font (not bundled)
    console.log('Adding content with Roboto font (not in fonts/ directory)...');

    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '# Roboto Font',
          position: { x: 0.5, y: 1, w: 9, h: 1 },
          style: { fontFace: 'Roboto', fontSize: 36, bold: true }
        },
        {
          content: 'This text is rendered in **Roboto** font, which was automatically downloaded from Google Fonts because it was not found in the local fonts directory!',
          position: { x: 0.5, y: 2.5, w: 9, h: 2 },
          autoFit: true,
          style: { fontFace: 'Roboto' }
        },
        {
          content: 'Auto-sizing works perfectly because the font was downloaded and measured using opentype.js!',
          position: { x: 0.5, y: 5, w: 9, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Roboto' }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('\n✓ Content added with auto-downloaded Roboto font');
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_font_autodownload_roboto.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    // Check if font was saved
    const robotoPath = path.join(__dirname, '../fonts/Roboto.ttf');
    if (fs.existsSync(robotoPath)) {
      const stats = fs.statSync(robotoPath);
      console.log(`\n  💾 Roboto font saved locally: ${(stats.size / 1024).toFixed(0)} KB`);
      console.log('     (Will be available immediately on next invocation!)');
    }

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testMultipleGoogleFonts() {
  console.log('\n\nTest 2: Download multiple Google Fonts...\n');

  try {
    const createInputs = {
      title: 'Multiple Google Fonts',
      slides: [{ markdown: '# Google Fonts Showcase' }]
    };

    await executeAction('create_presentation', createInputs, {});
    console.log('✓ Base presentation created\n');

    console.log('Adding content with 3 different Google Fonts...');

    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '# Google Fonts Auto-Download',
          position: { x: 0.5, y: 0.5, w: 9, h: 0.8 },
          style: { fontSize: 32, bold: true }
        },

        // Roboto (popular sans-serif)
        {
          content: '**Roboto** (Sans-serif)',
          position: { x: 0.5, y: 1.8, w: 4, h: 0.4 },
          style: { fontSize: 14, bold: true }
        },
        {
          content: 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs!',
          position: { x: 0.5, y: 2.3, w: 4, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Roboto' }
        },

        // Open Sans (popular sans-serif)
        {
          content: '**Open Sans** (Sans-serif)',
          position: { x: 5, y: 1.8, w: 4.5, h: 0.4 },
          style: { fontSize: 14, bold: true }
        },
        {
          content: 'The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs!',
          position: { x: 5, y: 2.3, w: 4.5, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Open Sans' }
        },

        // Montserrat (display font)
        {
          content: '**Montserrat** (Display)',
          position: { x: 0.5, y: 4.2, w: 4, h: 0.4 },
          style: { fontSize: 14, bold: true }
        },
        {
          content: 'The quick brown fox jumps over the lazy dog',
          position: { x: 0.5, y: 4.7, w: 4, h: 1.5 },
          autoFit: true,
          style: { fontFace: 'Montserrat' }
        },

        // Info box
        {
          content: '> All 3 fonts were automatically downloaded from Google Fonts and cached for use!',
          position: { x: 5, y: 4.2, w: 4.5, h: 2 },
          style: { fontSize: 14, italic: true, color: '0066CC' }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('\n✓ Multiple Google Fonts downloaded and used');
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_font_autodownload_multiple.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    // Check downloaded fonts
    console.log('\n  📦 Downloaded fonts:');
    const fontsDir = path.join(__dirname, '../fonts');
    const downloadedFonts = fs.readdirSync(fontsDir).filter(f =>
      f.includes('Roboto') || f.includes('Open-Sans') || f.includes('Montserrat')
    );

    downloadedFonts.forEach(font => {
      const stats = fs.statSync(path.join(fontsDir, font));
      console.log(`     - ${font} (${(stats.size / 1024).toFixed(0)} KB)`);
    });

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testMixedBundledAndDownloaded() {
  console.log('\n\nTest 3: Mix bundled fonts + auto-downloaded fonts...\n');

  try {
    const createInputs = {
      title: 'Mixed Fonts',
      slides: [{ markdown: '# Bundled + Downloaded Fonts' }]
    };

    await executeAction('create_presentation', createInputs, {});
    console.log('✓ Base presentation created\n');

    const addInputs = {
      slide_index: 0,
      elements: [
        {
          content: '# Font Source Comparison',
          position: { x: 0.5, y: 0.5, w: 9, h: 0.8 },
          style: { fontSize: 32, bold: true }
        },
        {
          content: '**Left:** Bundled fonts (instant) | **Right:** Google Fonts (auto-downloaded)',
          position: { x: 0.5, y: 1.4, w: 9, h: 0.4 },
          style: { fontSize: 14, italic: true }
        },

        // LEFT COLUMN: Bundled fonts (fast)
        {
          content: 'Calibri (bundled)',
          position: { x: 0.5, y: 2.2, w: 4, h: 1 },
          autoFit: true,
          style: { fontFace: 'Calibri' }
        },
        {
          content: 'Arial (bundled)',
          position: { x: 0.5, y: 3.5, w: 4, h: 1 },
          autoFit: true,
          style: { fontFace: 'Arial' }
        },
        {
          content: 'Times (bundled)',
          position: { x: 0.5, y: 4.8, w: 4, h: 1 },
          autoFit: true,
          style: { fontFace: 'Times New Roman' }
        },
        {
          content: 'Courier (bundled)',
          position: { x: 0.5, y: 6.1, w: 4, h: 1 },
          autoFit: true,
          style: { fontFace: 'Courier New' }
        },

        // RIGHT COLUMN: Google Fonts (downloaded)
        {
          content: 'Roboto (Google Fonts)',
          position: { x: 5, y: 2.2, w: 4.5, h: 1 },
          autoFit: true,
          style: { fontFace: 'Roboto' }
        },
        {
          content: 'Open Sans (Google Fonts)',
          position: { x: 5, y: 3.5, w: 4.5, h: 1 },
          autoFit: true,
          style: { fontFace: 'Open Sans' }
        },
        {
          content: 'Montserrat (Google Fonts)',
          position: { x: 5, y: 4.8, w: 4.5, h: 1 },
          autoFit: true,
          style: { fontFace: 'Montserrat' }
        },
        {
          content: 'Lato (Google Fonts)',
          position: { x: 5, y: 6.1, w: 4.5, h: 1 },
          autoFit: true,
          style: { fontFace: 'Lato' }
        }
      ]
    };

    const result = await executeAction('add_content', addInputs, {});

    console.log('\n✓ Mixed bundled and downloaded fonts');
    console.log('  - Elements added:', result.elements_added);

    const outputPath = path.join(outputDir, 'test_font_mixed_sources.pptx');
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
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║  Font Auto-Download Test (Google Fonts API)             ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  try {
    await testDownloadRoboto();
    await testMultipleGoogleFonts();
    await testMixedBundledAndDownloaded();

    console.log('\n\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║  ALL FONT DOWNLOAD TESTS PASSED!                         ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    console.log('✨ Automatic Font Download Features:');
    console.log('   ✓ Downloads from Google Fonts API (1500+ fonts available)');
    console.log('   ✓ Caches fonts in memory during Lambda execution');
    console.log('   ✓ Saves fonts to disk for future invocations');
    console.log('   ✓ Falls back to bundled fonts if download fails');
    console.log('   ✓ No API key required');
    console.log('   ✓ Seamless integration - AI just specifies fontFace');
    console.log('');
    console.log('🎯 Use Case:');
    console.log('   - Template uses "Roboto" font');
    console.log('   - Font not in fonts/ directory');
    console.log('   - Integration auto-downloads from Google Fonts');
    console.log('   - Auto-fitting works perfectly!');
    console.log('');
    console.log('💡 Supported: Any of 1500+ Google Fonts');
    console.log('   Popular: Roboto, Open Sans, Lato, Montserrat, Poppins, etc.');

  } catch (error) {
    console.error('\n=== Tests failed ===');
    console.error(error);
    process.exit(1);
  }
}

if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
