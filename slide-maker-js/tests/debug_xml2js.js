const xml2js = require('xml2js');
const fs = require('fs');
const path = require('path');
const JSZip = require('jszip');

async function debugXML2JS() {
  console.log('Debugging xml2js parsing...\n');

  // Load HK Template
  const templatePath = path.join(__dirname, '../../slider/HK Template.pptx');
  const templateBuffer = fs.readFileSync(templatePath);

  const zip = await JSZip.loadAsync(templateBuffer);
  const slideXml = await zip.file('ppt/slides/slide1.xml').async('text');

  console.log('Raw XML snippet with [Project Title]:');
  const idx = slideXml.indexOf('[Project Title]');
  console.log(slideXml.substring(idx - 50, idx + 70));

  // Parse with xml2js
  const parser = new xml2js.Parser({
    explicitArray: true,
    preserveChildrenOrder: true,
    xmlns: true
  });

  console.log('\n--- Parsing with xml2js ---');
  const slideObj = await parser.parseStringPromise(slideXml);

  console.log('\nParsed object keys:');
  console.log(Object.keys(slideObj));

  console.log('\nSearching for paragraphs...');

  // Try to find paragraphs
  function findParagraphs(obj, depth = 0, path = '') {
    if (depth > 10) return; // Prevent infinite recursion

    for (const key in obj) {
      const newPath = path ? `${path}.${key}` : key;

      if (key === 'a:p' && Array.isArray(obj[key])) {
        console.log(`\n✓ Found paragraph at: ${newPath}`);
        console.log(`  Number of paragraphs: ${obj[key].length}`);

        // Check first paragraph
        const para = obj[key][0];
        console.log(`  Paragraph keys:`, Object.keys(para));

        // Check for runs
        if (para['a:r']) {
          console.log(`  ✓ Found ${para['a:r'].length} runs`);

          para['a:r'].forEach((run, i) => {
            console.log(`\n  Run ${i}:`);
            console.log(`    Keys:`, Object.keys(run));

            if (run['a:t']) {
              const textNode = run['a:t'];
              console.log(`    a:t type:`, typeof textNode, Array.isArray(textNode) ? '(array)' : '');
              console.log(`    a:t value:`, JSON.stringify(textNode).substring(0, 100));

              // Extract actual text
              const text = Array.isArray(textNode) ? textNode[0] : textNode;
              const actualText = typeof text === 'string' ? text : (text._ || text || '');
              console.log(`    Extracted text: "${actualText.replace(/\n/g, '\\n')}"`);
            }
          });
        }
      }

      if (obj[key] && typeof obj[key] === 'object') {
        findParagraphs(obj[key], depth + 1, newPath);
      }
    }
  }

  findParagraphs(slideObj);
}

debugXML2JS().catch(console.error);
