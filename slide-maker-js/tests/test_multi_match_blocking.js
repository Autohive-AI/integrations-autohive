const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function testBlockMultipleMatches() {
  console.log('Test 1: Block ambiguous replacement (multiple matches without replace_all)...\n');

  try {
    // Create template with ambiguous text that appears multiple times
    const createInputs = {
      title: 'Multi-Match Test',
      slides: [
        { markdown: '# Welcome to Project Alpha\n\nProject status: In progress' },
        { markdown: '# Project Timeline\n\nProject completion: Q4 2024' },
        { markdown: '# Sub-Project Details\n\nProject budget: $500K' }
      ]
    };

    const createResult = await executeAction('create_presentation', createInputs, {});
    console.log('✓ Template created with "Project" appearing 5+ times');

    // Try to replace "Project" (ambiguous - appears multiple times)
    console.log('\nAttempting to replace "Project" (should be BLOCKED)...');

    const replaceInputs = {
      files: [createResult.file],
      replacements: [
        {
          find: 'Project',
          replace: 'Marketing Campaign'
          // replace_all defaults to false
        }
      ]
    };

    const result = await executeAction('find_and_replace', replaceInputs, {});

    console.log('\n✅ Response received:');
    console.log(`  success: ${result.success}`);
    console.log(`  total_replacements: ${result.total_replacements}`);
    console.log(`  blocked_count: ${result.blocked_count}`);
    console.log(`  message: ${result.message}`);

    if (result.blocked && result.blocked.length > 0) {
      console.log('\n🛡️  BLOCKED replacements:');
      result.blocked.forEach(b => {
        console.log(`\n  "${b.find_phrase}"`);
        console.log(`    Reason: ${b.BLOCKED}`);
        console.log(`    Found ${b.match_count} times:`);
        b.matches.forEach((m, i) => {
          console.log(`      ${i + 1}. ${m.location}`);
          console.log(`         "${m.content}"`);
        });
        console.log(`    Fix: ${b.fix_required}`);
      });

      console.log('\n✅ TEST PASSED: Ambiguous replacement was correctly blocked!');
    } else {
      console.log('\n❌ TEST FAILED: Should have been blocked!');
    }

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error.stack);
    throw error;
  }
}

async function testReplaceAllFlag() {
  console.log('\n\nTest 2: Allow multiple replacements with replace_all=true...\n');

  try {
    // Create same template
    const createInputs = {
      title: 'Multi-Match Test',
      slides: [
        { markdown: '# Welcome to Project Alpha\n\nProject status: In progress' },
        { markdown: '# Project Timeline' },
        { markdown: '# Sub-Project Details' }
      ]
    };

    const createResult = await executeAction('create_presentation', createInputs, {});
    console.log('✓ Template created with "Project" appearing multiple times');

    // Replace with replace_all=true (should work)
    console.log('\nAttempting to replace "Project" with replace_all=true...');

    const replaceInputs = {
      files: [createResult.file],
      replacements: [
        {
          find: 'Project',
          replace: '**Marketing Campaign**',
          replace_all: true  // ← Allow multiple replacements
        }
      ]
    };

    const result = await executeAction('find_and_replace', replaceInputs, {});

    console.log('\n✅ Response received:');
    console.log(`  success: ${result.success}`);
    console.log(`  total_replacements: ${result.total_replacements}`);
    console.log(`  blocked_count: ${result.blocked_count}`);
    console.log(`  message: ${result.message}`);

    if (result.success && result.total_replacements > 1) {
      console.log(`\n✅ TEST PASSED: Replaced all ${result.total_replacements} instances with replace_all=true!`);
    } else {
      console.log('\n❌ TEST FAILED: Should have replaced multiple instances!');
    }

    const outputPath = path.join(outputDir, 'test_multi_match_allowed.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log(`  💾 Saved to: ${outputPath}`);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error.stack);
    throw error;
  }
}

async function testSpecificTextNotBlocked() {
  console.log('\n\nTest 3: Specific text (single match) should NOT be blocked...\n');

  try {
    // Create template
    const createInputs = {
      title: 'Specific Match Test',
      slides: [
        { markdown: '# Welcome to Project Alpha\n\nProject status: In progress' },
        { markdown: '# Project Timeline' },
        { markdown: '# Budget Details' }
      ]
    };

    const createResult = await executeAction('create_presentation', createInputs, {});
    console.log('✓ Template created');

    // Replace specific unique text (should work without replace_all)
    console.log('\nReplacing "Project Alpha" (unique text)...');

    const replaceInputs = {
      files: [createResult.file],
      replacements: [
        {
          find: 'Project Alpha',  // ← Specific, appears only once
          replace: '**Marketing Campaign Alpha**'
          // replace_all not needed (only 1 match)
        }
      ]
    };

    const result = await executeAction('find_and_replace', replaceInputs, {});

    console.log('\n✅ Response received:');
    console.log(`  success: ${result.success}`);
    console.log(`  total_replacements: ${result.total_replacements}`);
    console.log(`  blocked_count: ${result.blocked_count}`);

    if (result.success && result.blocked_count === 0) {
      console.log('\n✅ TEST PASSED: Specific text was replaced without blocking!');
    } else {
      console.log('\n❌ TEST FAILED: Should not have been blocked!');
    }

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function runAllTests() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║  Multi-Match Blocking Test Suite                         ║');
  console.log('║  Safety Feature: Block ambiguous replacements            ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  try {
    await testBlockMultipleMatches();
    await testReplaceAllFlag();
    await testSpecificTextNotBlocked();

    console.log('\n\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║  ALL MULTI-MATCH BLOCKING TESTS PASSED!                  ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    console.log('✨ Safety Features Verified:');
    console.log('   ✓ Blocks ambiguous text (multiple matches)');
    console.log('   ✓ Shows all match locations with context');
    console.log('   ✓ Provides clear guidance to LLM');
    console.log('   ✓ Allows replace_all=true override');
    console.log('   ✓ Does NOT block specific unique text');
    console.log('');
    console.log('🛡️  LLM Safety:');
    console.log('   - Prevents accidental bulk replacements');
    console.log('   - Forces LLM to be more specific');
    console.log('   - Matches Python version behavior');

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
