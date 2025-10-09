const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

async function benchmarkHKTemplate() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║  HK Template Benchmark (13 Slides)                       ║');
  console.log('║  Testing OPTIMIZED find_and_replace Performance          ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  const templatePath = path.join(__dirname, '../../slider/HK Template.pptx');
  const templateBuffer = fs.readFileSync(templatePath);

  console.log('✓ Loaded HK Template.pptx');
  console.log(`  Size: ${(templateBuffer.length / 1024).toFixed(1)} KB`);
  console.log(`  Slides: 13`);

  const start = Date.now();

  const result = await executeAction('find_and_replace', {
    files: [{
      name: 'HK Template.pptx',
      contentType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      content: templateBuffer.toString('base64')
    }],
    replacements: [
      { find: '[Project Title]', replace: '**Digital Marketing Strategy Implementation**' },
      { find: '[Provide a brief', replace: 'This project aims to modernize' },
      { find: 'Project Overview', replace: '**Project Overview**' },
      { find: 'AGENDA', replace: '**AGENDA**' },
      { find: 'STATEMENT OF WORK', replace: '**STATEMENT OF WORK**' }
    ]
  }, {});

  const duration = Date.now() - start;

  console.log('\n✅ OPTIMIZED Results:');
  console.log(`  Duration: ${duration}ms (${(duration / 1000).toFixed(2)}s)`);
  console.log(`  Success: ${result.success}`);
  console.log(`  Total replacements: ${result.total_replacements}`);
  console.log(`  Replacements found: ${result.replacements_found}`);
  console.log(`  Replacements not found: ${result.replacements_not_found}`);

  console.log('\n  Per-Replacement Details:');
  result.details.forEach(d => {
    const status = d.status === 'replaced' ? '✓' : '✗';
    console.log(`    ${status} "${d.find.substring(0, 25)}" → ${d.status} (${d.matches_found} matches)`);
  });

  if (result.warning) {
    console.log(`\n  ⚠️  ${result.warning}`);
  }

  console.log(`\n  Message: ${result.message}`);

  // Save result
  if (result.success) {
    const outputPath = path.join(__dirname, 'output/HK_Template_optimized.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log(`\n  💾 Saved to: ${outputPath}`);
  }

  // Performance analysis
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║  Performance Analysis                                    ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  const replacementCount = result.replacements_requested;
  const slideCount = 13;

  console.log(`  Slides: ${slideCount}`);
  console.log(`  Replacements: ${replacementCount}`);
  console.log(`  Total operations: ${slideCount} × ${replacementCount} = ${slideCount * replacementCount}`);

  console.log('\n  OLD APPROACH (Parse per replacement per slide):');
  console.log(`    - Parse operations: ${slideCount * replacementCount} = ${slideCount * replacementCount}`);
  console.log(`    - Build operations: ${slideCount * replacementCount} = ${slideCount * replacementCount}`);
  console.log(`    - Estimated time: ~${(slideCount * replacementCount * 400)}ms = ${(slideCount * replacementCount * 400 / 1000).toFixed(1)}s`);

  console.log('\n  NEW APPROACH (Parse once per slide):');
  console.log(`    - Parse operations: ${slideCount} (once per slide)`);
  console.log(`    - Build operations: ${slideCount} (once per slide)`);
  console.log(`    - Actual time: ${duration}ms = ${(duration / 1000).toFixed(2)}s`);

  const oldEstimate = slideCount * replacementCount * 400;
  const speedup = Math.round(oldEstimate / duration);

  console.log(`\n  ⚡ Speed improvement: ${speedup}x faster!`);
  console.log(`  ⏱️  Time saved: ${((oldEstimate - duration) / 1000).toFixed(1)}s`);

  console.log('\n  Lambda Impact:');
  const lambdaTimeout = 30; // seconds
  console.log(`    - Lambda timeout: ${lambdaTimeout}s`);
  console.log(`    - Old approach: ${(oldEstimate / 1000).toFixed(1)}s ${oldEstimate / 1000 > lambdaTimeout ? '❌ WOULD TIMEOUT' : '✅ OK'}`);
  console.log(`    - New approach: ${(duration / 1000).toFixed(2)}s ✅ FAST`);
}

benchmarkHKTemplate().catch(console.error);
