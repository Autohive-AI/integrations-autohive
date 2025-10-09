const content = `<a:r><a:rPr sz="2400" dirty="0"><a:solidFill><a:schemeClr val="bg1"/></a:solidFill><a:latin typeface="Calibri"/></a:rPr><a:t>STATEMENT OF WORK
[Project Title]</a:t></a:r>`;

console.log('Testing text extraction regex...\n');

console.log('Content:');
console.log(content);

console.log('\n--- Test 1: Current regex ---');
const regex1 = /<a:t[^>]*>(.*?)<\/a:t>/g;
const matches1 = [...content.matchAll(regex1)];
console.log(`Regex: ${regex1}`);
console.log(`Matches: ${matches1.length}`);
matches1.forEach((m, i) => console.log(`  Match ${i}: "${m[1].replace(/\n/g, '\\n')}"`));

console.log('\n--- Test 2: Without attributes match ---');
const regex2 = /<a:t>(.*?)<\/a:t>/g;
const matches2 = [...content.matchAll(regex2)];
console.log(`Regex: ${regex2}`);
console.log(`Matches: ${matches2.length}`);
matches2.forEach((m, i) => console.log(`  Match ${i}: "${m[1].replace(/\n/g, '\\n')}"`));

console.log('\n--- Test 3: With dotall flag ---');
const regex3 = /<a:t[^>]*>(.*?)<\/a:t>/gs;
const matches3 = [...content.matchAll(regex3)];
console.log(`Regex: ${regex3}`);
console.log(`Matches: ${matches3.length}`);
matches3.forEach((m, i) => console.log(`  Match ${i}: "${m[1].replace(/\n/g, '\\n')}"`));

console.log('\n--- Test 4: Simple match test ---');
const hasTag = content.includes('<a:t>');
const simpleRegex = /<a:t>/;
const simpleMatch = simpleRegex.test(content);
console.log(`Content includes '<a:t>': ${hasTag}`);
console.log(`Regex test: ${simpleMatch}`);

// Check what the [^>]* is actually matching
console.log('\n--- Test 5: Debug [^>]* ---');
const debugRegex = /<a:t([^>]*)>/;
const debugMatch = content.match(debugRegex);
console.log(`Match result:`, debugMatch);
