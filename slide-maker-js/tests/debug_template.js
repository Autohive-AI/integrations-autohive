const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

async function debugHKTemplate() {
  console.log('Debugging HK Template find_and_replace...\n');

  // Load the actual HK Template
  const templatePath = path.join(__dirname, '../../slider/HK Template.pptx');

  if (!fs.existsSync(templatePath)) {
    console.error('HK Template not found at:', templatePath);
    return;
  }

  const templateBuffer = fs.readFileSync(templatePath);
  const templateBase64 = templateBuffer.toString('base64');

  console.log('✓ Loaded HK Template.pptx');
  console.log(`  Size: ${(templateBuffer.length / 1024).toFixed(1)} KB`);

  // Try to replace [Project Title]
  const inputs = {
    files: [{
      name: 'HK Template.pptx',
      contentType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      content: templateBase64
    }],
    replacements: [
      {
        find: '[Project Title]',
        replace: '**Digital Marketing Strategy Implementation**'
      }
    ]
  };

  console.log('\nAttempting find_and_replace...');
  console.log(`  Find: "${inputs.replacements[0].find}"`);
  console.log(`  Replace: "${inputs.replacements[0].replace}"`);

  try {
    const result = await executeAction('find_and_replace', inputs, {});

    console.log('\n✓ find_and_replace completed');
    console.log(`  Total replacements: ${result.total_replacements}`);
    console.log(`  Replacements processed: ${result.replacements_processed}`);

    if (result.total_replacements === 0) {
      console.log('\n⚠️  NO REPLACEMENTS MADE!');
      console.log('  This means "[Project Title]" was not found in the XML.');
      console.log('  Debugging...\n');

      // Extract and check slides manually
      const JSZip = require('jszip');
      const zip = await JSZip.loadAsync(templateBuffer);

      const slideFiles = Object.keys(zip.files)
        .filter(name => name.match(/ppt\/slides\/slide\d+\.xml$/))
        .sort();

      console.log(`  Found ${slideFiles.length} slides`);

      for (const slideFile of slideFiles) {
        const slideXml = await zip.file(slideFile).async('text');

        // Check if this slide contains the text
        if (slideXml.includes('[Project Title]')) {
          console.log(`\n  ✓ Found "[Project Title]" in ${slideFile}`);

          // Show the raw context
          const idx = slideXml.indexOf('[Project Title]');
          console.log(`\n  Raw XML context (50 chars before, text, 50 after):`);
          const before = slideXml.substring(idx - 50, idx);
          const after = slideXml.substring(idx + 15, idx + 65);
          console.log(`  "${before.replace(/\n/g, '\\n')}[Project Title]${after.replace(/\n/g, '\\n')}"`);

          // Extract the paragraph containing it
          const paragraphRegex = /(<a:p\b[^>]*>)(.*?)(<\/a:p>)/gs;
          let match;
          let found = false;
          let matchCount = 0;

          while ((match = paragraphRegex.exec(slideXml)) !== null) {
            matchCount++;
            if (match[2].includes('[Project Title]')) {
              console.log(`\n  ✓ Paragraph regex matched! (Match #${matchCount})`);
              console.log(`     Opening tag: ${match[1]}`);
              console.log(`     Content length: ${match[2].length} chars`);
              console.log(`     Content (first 300 chars):`);
              console.log(`     ${match[2].substring(0, 300).replace(/\n/g, '\\n')}`);

              // Extract text runs
              const textRegex = /<a:t[^>]*>(.*?)<\/a:t>/g;
              const textMatches = [...match[2].matchAll(textRegex)];

              console.log(`\n     Text regex matches: ${textMatches.length}`);

              if (textMatches.length === 0) {
                console.log(`     ⚠️  No <a:t> tags matched!`);
                console.log(`     Checking if <a:t> exists in content...`);
                console.log(`     Content includes "<a:t>": ${match[2].includes('<a:t>')}`);
                console.log(`     Content includes "</a:t>": ${match[2].includes('</a:t>')}`);
              }

              const texts = textMatches.map(m => m[1]);

              console.log(`\n     Text runs in this paragraph:`);
              texts.forEach((t, i) => {
                console.log(`       Run ${i}: "${t.replace(/\n/g, '\\n')}"`);
              });

              const fullText = texts.join('');
              console.log(`\n     Concatenated text: "${fullText.replace(/\n/g, '\\n')}"`);
              console.log(`     Contains "[Project Title]": ${fullText.includes('[Project Title]')}`);

              found = true;
              break;
            }
          }

          console.log(`\n  Total paragraph matches: ${matchCount}`);

          if (!found) {
            console.log(`     ❌ Paragraph containing "[Project Title]" not matched by regex!`);
          }
        }
      }
    } else {
      console.log(`\n  ✅ SUCCESS! Replaced ${result.total_replacements} instance(s)`);

      // Save result
      const outputDir = path.join(__dirname, 'output');
      const outputPath = path.join(outputDir, 'HK_Template_filled_debug.pptx');
      const buffer = Buffer.from(result.file.content, 'base64');
      fs.writeFileSync(outputPath, buffer);
      console.log(`  💾 Saved to: ${outputPath}`);
    }

  } catch (error) {
    console.error('\n✗ Error:', error.message);
    console.error(error.stack);
  }
}

debugHKTemplate();
