const xml2js = require('xml2js');
const fs = require('fs');
const path = require('path');
const JSZip = require('jszip');

// Import the functions we need to test
const {
  findAndReplaceInSlideXML,
  findAllParagraphs,
  extractTextFromParagraph
} = require('../slide_maker');

async function testXML2JSApproach() {
  console.log('Testing xml2js-based find_and_replace...\n');

  // Load HK Template
  const templatePath = path.join(__dirname, '../../slider/HK Template.pptx');
  const templateBuffer = fs.readFileSync(templatePath);

  const zip = await JSZip.loadAsync(templateBuffer);
  const slideXml = await zip.file('ppt/slides/slide1.xml').async('text');

  console.log('✓ Loaded slide1.xml');
  console.log(`  Contains "[Project Title]": ${slideXml.includes('[Project Title]')}`);

  // Parse with xml2js
  const parser = new xml2js.Parser({
    explicitArray: true,
    preserveChildrenOrder: true,
    xmlns: true
  });

  console.log('\nParsing with xml2js...');
  const slideObj = await parser.parseStringPromise(slideXml);
  console.log('✓ Parsed successfully');

  // Find paragraphs using our function
  console.log('\nFinding paragraphs...');
  const paragraphs = findAllParagraphs(slideObj);
  console.log(`✓ Found ${paragraphs.length} paragraphs`);

  // Check each paragraph for our text
  let foundParagraph = null;
  for (let i = 0; i < paragraphs.length; i++) {
    const para = paragraphs[i].paragraph;
    const { fullText } = extractTextFromParagraph(para);

    console.log(`\nParagraph ${i}:`);
    console.log(`  Text: "${fullText.substring(0, 100).replace(/\n/g, '\\n').replace(/\r/g, '\\r')}"`);
    console.log(`  Contains "[Project Title]": ${fullText.includes('[Project Title]')}`);

    if (fullText.includes('[Project Title]')) {
      foundParagraph = para;
      console.log(`  ✓ FOUND IT!`);
      break;
    }
  }

  if (foundParagraph) {
    console.log('\n✅ Paragraph with "[Project Title]" found via xml2js!');
    console.log('   The xml2js approach is working correctly.');

    // Now test the full find_and_replace function
    console.log('\nTesting full findAndReplaceInSlideXML function...');

    const newXml = await findAndReplaceInSlideXML(
      slideXml,
      '[Project Title]',
      '**Digital Marketing Strategy**'
    );

    console.log(`  XML modified: ${newXml !== slideXml}`);
    console.log(`  Contains "[Project Title]": ${newXml.includes('[Project Title]')}`);
    console.log(`  Contains "Digital Marketing": ${newXml.includes('Digital Marketing')}`);

    if (newXml !== slideXml) {
      console.log('\n✅ Replacement succeeded!');
    } else {
      console.log('\n❌ Replacement failed - XML unchanged');
    }
  } else {
    console.log('\n❌ Paragraph not found via xml2js - there is a bug in findAllParagraphs or extractTextFromParagraph');
  }
}

testXML2JSApproach().catch(console.error);
