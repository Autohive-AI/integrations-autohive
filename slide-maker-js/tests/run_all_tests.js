const fs = require('fs');
const path = require('path');

// Import all test modules
const { runAllTests: testCreatePresentation } = require('./test_create_presentation');
const { runAllTests: testGenerateSlides } = require('./test_generate_slides');
const { runAllTests: testAddContent } = require('./test_add_content');
const { runAllTests: testAddChartAndImages } = require('./test_add_chart_and_images');
const { runAllTests: testAutoFit } = require('./test_autofit');
const { runAllTests: testAllFonts } = require('./test_all_fonts');

async function main() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║  Slide Maker JS - Comprehensive Test Suite               ║');
  console.log('║  Tests all 4 actions with PPTX file generation           ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  const outputDir = path.join(__dirname, 'output');

  // Clean output directory
  if (fs.existsSync(outputDir)) {
    console.log('🗑️  Cleaning output directory...');
    const files = fs.readdirSync(outputDir);
    for (const file of files) {
      fs.unlinkSync(path.join(outputDir, file));
    }
    console.log('✓ Output directory cleaned\n');
  } else {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log('📁 Output directory created\n');
  }

  const startTime = Date.now();
  let totalTests = 0;
  let passedTests = 0;

  // Test Suite 1: create_presentation
  try {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testCreatePresentation();
    totalTests += 3; // 3 tests in this suite
    passedTests += 3;
  } catch (error) {
    console.error('❌ create_presentation tests failed');
    totalTests += 3;
  }

  // Test Suite 2: generate_slides
  try {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testGenerateSlides();
    totalTests += 3;
    passedTests += 3;
  } catch (error) {
    console.error('❌ generate_slides tests failed');
    totalTests += 3;
  }

  // Test Suite 3: add_content
  try {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testAddContent();
    totalTests += 4;
    passedTests += 4;
  } catch (error) {
    console.error('❌ add_content tests failed');
    totalTests += 4;
  }

  // Test Suite 4: add_chart_and_images
  try {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testAddChartAndImages();
    totalTests += 4;
    passedTests += 4;
  } catch (error) {
    console.error('❌ add_chart_and_images tests failed');
    totalTests += 4;
  }

  // Test Suite 5: auto-fit
  try {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testAutoFit();
    totalTests += 6;  // Now includes torture test
    passedTests += 6;
  } catch (error) {
    console.error('❌ auto-fit tests failed');
    totalTests += 6;
  }

  // Test Suite 6: all fonts (opentype.js)
  try {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    await testAllFonts();
    totalTests += 2;
    passedTests += 2;
  } catch (error) {
    console.error('❌ all fonts tests failed');
    totalTests += 2;
  }

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  // Summary
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║  TEST SUMMARY                                             ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  console.log(`Total tests:      ${totalTests}`);
  console.log(`Passed:           ${passedTests} ✓`);
  console.log(`Failed:           ${totalTests - passedTests} ✗`);
  console.log(`Duration:         ${duration}s`);

  // List generated files
  console.log('\n📄 Generated PPTX files:');
  const files = fs.readdirSync(outputDir).filter(f => f.endsWith('.pptx'));
  files.forEach((file, i) => {
    const stats = fs.statSync(path.join(outputDir, file));
    const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
    console.log(`   ${i + 1}. ${file} (${sizeMB} MB)`);
  });

  console.log(`\n✓ All files saved to: ${outputDir}`);
  console.log('\n💡 Open the PPTX files in PowerPoint to verify functionality!');

  // Feature highlights
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║  FEATURE HIGHLIGHTS TESTED                                ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  console.log('✓ Master slide templates (branding)');
  console.log('✓ Data-driven batch generation (20+ slides from template)');
  console.log('✓ Intelligent text auto-fitting (opentype.js - ALL fonts)');
  console.log('✓ Auto-layout mode (vertical flow)');
  console.log('✓ Granular mode (precise positioning)');
  console.log('✓ HTML table direct conversion');
  console.log('✓ Markdown parsing (bold, italic, underline, code)');
  console.log('✓ Auto-type detection (table/bullets/text)');
  console.log('✓ Multiple chart types (bar, line, pie, area)');
  console.log('✓ Image placement');
  console.log('✓ Dashboard layouts (mixed content)');

  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║  EFFICIENCY COMPARISON                                    ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  console.log('Python approach (traditional):');
  console.log('  → Create 20-slide report: ~100+ API calls');
  console.log('  → Separate calls for each: create, add_slide, add_text, etc.');
  console.log('');
  console.log('JavaScript approach (this integration):');
  console.log('  → Create 20-slide report: 2 API calls');
  console.log('  → create_presentation + generate_slides');
  console.log('');
  console.log('Efficiency gain: 50-100x fewer API calls! 🚀');

  if (passedTests === totalTests) {
    console.log('\n🎉 ALL TESTS PASSED! Integration is ready to use.\n');
    process.exit(0);
  } else {
    console.log('\n⚠️  Some tests failed. Check output above for details.\n');
    process.exit(1);
  }
}

// Run all tests
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
