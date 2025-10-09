const pptxgen = require('pptxgenjs');
const MarkdownIt = require('markdown-it');
const Mustache = require('mustache');
const cheerio = require('cheerio');
const opentype = require('opentype.js');
const path = require('path');
const fs = require('fs');
const JSZip = require('jszip');
const xml2js = require('xml2js');

// ==================== IN-MEMORY STORAGE ====================
// Presentations stored by ID during Lambda execution
const presentations = new Map();

// Font cache (load fonts once, reuse throughout Lambda execution)
const fontCache = new Map();

// ==================== BUFFER UTILITIES ====================

/**
 * Normalize various input formats to Node Buffer
 * (Adapted from image-resizer pattern)
 */
async function normalizeToBuffer(value) {
  if (!value) return null;

  // Already a Node Buffer
  if (Buffer.isBuffer(value)) return value;

  // JSON-serialized Buffer { type: 'Buffer', data: [...] }
  if (typeof value === 'object' && value.type === 'Buffer' && Array.isArray(value.data)) {
    return Buffer.from(value.data);
  }

  // TypedArray / ArrayBuffer-like
  if (typeof value === 'object' && value.buffer && typeof value.byteLength === 'number') {
    return Buffer.from(value);
  }
  if (typeof ArrayBuffer !== 'undefined' && value instanceof ArrayBuffer) {
    return Buffer.from(value);
  }

  if (typeof value === 'string') {
    const s = value.trim();

    // Base64 or base64url (most common for our use case)
    let b64 = s.replace(/\s+/g, '');
    b64 = b64.replace(/-/g, '+').replace(/_/g, '/');
    // Pad to multiple of 4
    while (b64.length % 4 !== 0) b64 += '=';
    return Buffer.from(b64, 'base64');
  }

  // Fallback: try base64
  try {
    const str = String(value);
    let b64 = str.replace(/-/g, '+').replace(/_/g, '/');
    while (b64.length % 4 !== 0) b64 += '=';
    return Buffer.from(b64, 'base64');
  } catch {
    return null;
  }
}

/**
 * Process files array from input
 * Returns Map of filename -> Buffer
 */
function processFiles(files) {
  const processed = new Map();
  if (!files || !Array.isArray(files)) return processed;

  for (const file of files) {
    if (file.content && file.name) {
      try {
        const buffer = Buffer.from(file.content, 'base64');
        processed.set(file.name, buffer);
      } catch (e) {
        console.error(`Failed to process file ${file.name}:`, e);
      }
    }
  }

  return processed;
}

// ==================== MARKDOWN PARSING UTILITIES ====================

/**
 * Auto-detect element type from markdown content
 * Returns: 'table', 'bullets', or 'text'
 */
function detectElementType(markdown) {
  if (!markdown || typeof markdown !== 'string') return 'text';

  // Check for table (| ... | format with separator line)
  if (/\|.*\|/.test(markdown) && /\|[-:\s]+\|/.test(markdown)) {
    return 'table';
  }

  // Check for lists (-, *, +, or 1., 2., etc.)
  if (/^\s*[-*+]\s/m.test(markdown) || /^\s*\d+\.\s/m.test(markdown)) {
    return 'bullets';
  }

  // Default: plain text
  return 'text';
}

/**
 * Parse markdown table to 2D array
 * Input:  | Col1 | Col2 |
 *         |------|------|
 *         | A    | B    |
 * Output: [["Col1", "Col2"], ["A", "B"]]
 */
function parseMarkdownTable(markdown) {
  const lines = markdown.trim().split('\n');
  const data = [];

  for (const line of lines) {
    // Skip separator lines (|---|---|)
    if (/\|[-:\s]+\|/.test(line)) continue;

    // Parse row: split by |, trim whitespace
    let cells = line.split('|').map(c => c.trim());
    // Remove empty cells from start and end (if line starts/ends with |)
    if (cells.length > 0 && cells[0] === '') cells = cells.slice(1);
    if (cells.length > 0 && cells[cells.length - 1] === '') cells = cells.slice(0, -1);

    if (cells.length > 0) {
      data.push(cells);
    }
  }

  return data;
}

/**
 * Parse markdown bullets to array with levels
 * Input:  - Item 1
 *           - Sub 1
 *         - Item 2
 * Output: [
 *   {text: "Item 1", level: 0},
 *   {text: "Sub 1", level: 1},
 *   {text: "Item 2", level: 0}
 * ]
 */
function parseMarkdownBullets(markdown) {
  const lines = markdown.split('\n');
  const items = [];

  for (const line of lines) {
    // Match list items: -, *, +, or numbered (1., 2., etc.)
    const match = line.match(/^(\s*)([-*+]|\d+\.)\s+(.+)$/);
    if (match) {
      const indent = match[1];
      const text = match[3];
      // Calculate level based on indentation (2 spaces = 1 level)
      const level = Math.min(Math.floor(indent.length / 2), 8);

      items.push({ text, level });
    }
  }

  return items;
}

/**
 * Parse inline markdown formatting to PPTXgenJS text runs
 * Converts **bold**, *italic*, __underline__, `code` to styled text objects
 */
function parseInlineMarkdown(markdown) {
  const md = new MarkdownIt();
  const html = md.renderInline(markdown);
  const $ = cheerio.load(html, null, false); // Don't add html/body tags

  const textRuns = [];

  function processNode(node) {
    if (node.type === 'text') {
      if (node.data && node.data.trim()) {
        textRuns.push({ text: node.data });
      }
    } else if (node.name === 'strong' || node.name === 'b') {
      const text = $(node).text();
      if (text.trim()) {
        textRuns.push({ text, options: { bold: true } });
      }
    } else if (node.name === 'em' || node.name === 'i') {
      const text = $(node).text();
      if (text.trim()) {
        textRuns.push({ text, options: { italic: true } });
      }
    } else if (node.name === 'u') {
      const text = $(node).text();
      if (text.trim()) {
        textRuns.push({ text, options: { underline: { style: 'sng' } } });
      }
    } else if (node.name === 'code') {
      const text = $(node).text();
      if (text.trim()) {
        textRuns.push({ text, options: { fontFace: 'Courier New' } });
      }
    } else if (node.children) {
      for (const child of node.children) {
        processNode(child);
      }
    }
  }

  // Process all children
  const root = $.root()[0];
  if (root && root.children) {
    for (const child of root.children) {
      processNode(child);
    }
  }

  // If no runs found, return plain text
  if (textRuns.length === 0) {
    return [{ text: markdown }];
  }

  return textRuns;
}

/**
 * Parse HTML table to 2D array (for HTML direct conversion)
 */
function parseHTMLTable(html) {
  const $ = cheerio.load(html);
  const rows = [];

  $('tr').each((i, tr) => {
    const cells = [];
    $(tr).find('th, td').each((j, cell) => {
      cells.push($(cell).text().trim());
    });
    if (cells.length > 0) {
      rows.push(cells);
    }
  });

  return rows;
}

// ==================== AUTO-FITTING TEXT ====================

/**
 * Download font from Google Fonts API and cache it
 *
 * @param {string} fontFamily - Font family name (e.g., 'Roboto', 'Open Sans')
 * @returns {Promise<object|null>} OpenType font object or null if download failed
 */
async function downloadAndCacheFont(fontFamily) {
  try {
    // Map Microsoft proprietary fonts to Google Font alternatives
    // Microsoft fonts are NOT in Google Fonts (proprietary), but there are metric-compatible alternatives
    const microsoftToGoogleMap = {
      'arial': { alternative: 'Arimo', note: 'Arial is proprietary. Using Arimo (metric-compatible alternative).' },
      'times new roman': { alternative: 'Tinos', note: 'Times New Roman is proprietary. Using Tinos (metric-compatible).' },
      'times': { alternative: 'Tinos', note: 'Times is proprietary. Using Tinos (metric-compatible).' },
      'courier new': { alternative: 'Cousine', note: 'Courier New is proprietary. Using Cousine (metric-compatible).' },
      'courier': { alternative: 'Cousine', note: 'Courier is proprietary. Using Cousine (metric-compatible).' },
      'calibri': { alternative: null, note: 'Calibri is proprietary (Microsoft). No metric-compatible alternative in Google Fonts. Please bundle Calibri.ttf manually.' },
      'segoe ui': { alternative: null, note: 'Segoe UI is proprietary (Microsoft). Consider using Open Sans instead.' }
    };

    const fontKey = fontFamily.toLowerCase();
    let downloadFontName = fontFamily;

    // Check if this is a Microsoft font
    if (microsoftToGoogleMap[fontKey]) {
      const mapping = microsoftToGoogleMap[fontKey];

      if (mapping.alternative) {
        console.log(`  ℹ️  ${mapping.note}`);
        downloadFontName = mapping.alternative;
      } else {
        console.warn(`  ⚠️  ${mapping.note}`);
        return null; // No alternative available
      }
    }

    console.log(`  🔍 Font "${downloadFontName}" not found locally, attempting download from Google Fonts...`);

    // Google Fonts CSS API (returns TTF URLs)
    const cssUrl = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(downloadFontName)}`;

    // Fetch CSS with user-agent that requests TTF format
    const cssResponse = await fetch(cssUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; Node.js)'
      }
    });

    if (!cssResponse.ok) {
      console.warn(`  ❌ Font not available on Google Fonts: ${downloadFontName}`);
      return null;
    }

    const cssText = await cssResponse.text();

    // Extract TTF URL from CSS
    // Format: url(https://fonts.gstatic.com/s/fontname/version/file.ttf)
    const urlMatch = cssText.match(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+\.ttf)\)/);

    if (!urlMatch) {
      console.warn(`  ❌ No TTF URL found in CSS for: ${fontFamily}`);
      return null;
    }

    const ttfUrl = urlMatch[1];
    console.log(`  📥 Downloading from: ${ttfUrl.substring(0, 60)}...`);

    // Download the actual font file
    const fontResponse = await fetch(ttfUrl);

    if (!fontResponse.ok) {
      console.warn(`  ❌ Download failed: ${fontResponse.status}`);
      return null;
    }

    const arrayBuffer = await fontResponse.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    console.log(`  ✓ Downloaded ${fontFamily} (${(buffer.length / 1024).toFixed(0)} KB)`);

    // Parse font from buffer
    const font = opentype.parse(buffer.buffer);

    // Cache in memory
    fontCache.set(fontFamily, font);

    // Try to save to fonts directory for future Lambda invocations
    try {
      const safeFontName = fontFamily.replace(/[^a-zA-Z0-9]/g, '-');
      const savePath = path.join(__dirname, 'fonts', `${safeFontName}.ttf`);

      // In Lambda, /tmp is writable but __dirname might not be
      // Try __dirname first, then /tmp
      try {
        fs.writeFileSync(savePath, buffer);
        console.log(`  💾 Saved to: ${savePath}`);
      } catch (dirError) {
        // Try /tmp for Lambda
        const tmpPath = `/tmp/${safeFontName}.ttf`;
        fs.writeFileSync(tmpPath, buffer);
        console.log(`  💾 Saved to: ${tmpPath} (Lambda /tmp)`);
      }
    } catch (saveError) {
      // Saving is optional - font is still cached in memory
      console.log(`  ℹ️  Font cached in memory (disk save skipped)`);
    }

    return font;

  } catch (error) {
    console.warn(`  ❌ Error downloading font ${fontFamily}:`, error.message);
    return null;
  }
}

/**
 * Load font file using opentype.js
 * Checks local fonts directory and cache
 *
 * @param {string} fontName - Font name (e.g., 'Arial', 'Calibri')
 * @returns {object|null} OpenType font object or null if not found
 */
function loadFont(fontName) {
  // Check cache first
  if (fontCache.has(fontName)) {
    return fontCache.get(fontName);
  }

  // Font file mapping for bundled fonts
  const fontFiles = {
    'arial': 'Arial.ttf',
    'calibri': 'Calibri.ttf',
    'times new roman': 'Times.ttf',
    'times': 'Times.ttf',
    'courier new': 'Courier.ttf',
    'courier': 'Courier.ttf'
  };

  const fontKey = fontName.toLowerCase();
  const fontFile = fontFiles[fontKey];

  // Try to load from fonts directory
  if (fontFile) {
    const fontPath = path.join(__dirname, 'fonts', fontFile);

    try {
      if (fs.existsSync(fontPath)) {
        const font = opentype.loadSync(fontPath);
        fontCache.set(fontName, font);
        return font;
      }
    } catch (error) {
      console.warn(`Failed to load font ${fontName}:`, error.message);
    }
  }

  // Check /tmp directory (Lambda might have downloaded it there)
  const safeFontName = fontName.replace(/[^a-zA-Z0-9]/g, '-');
  const tmpPath = `/tmp/${safeFontName}.ttf`;

  try {
    if (fs.existsSync(tmpPath)) {
      const font = opentype.loadSync(tmpPath);
      fontCache.set(fontName, font);
      return font;
    }
  } catch (error) {
    // Ignore - will fall through to return null
  }

  return null; // Font not found locally
}

/**
 * Measure text width using opentype.js (actual font geometry)
 *
 * @param {string} text - Text to measure
 * @param {object} font - OpenType font object
 * @param {number} fontSize - Font size in points
 * @returns {number} Text width in pixels
 */
function measureTextWidth(text, font, fontSize) {
  try {
    const path = font.getPath(text, 0, 0, fontSize);
    const bbox = path.getBoundingBox();
    return bbox.x2 - bbox.x1;
  } catch (error) {
    // Fallback: estimate based on character count
    return text.length * fontSize * 0.6; // Rough estimate
  }
}

/**
 * Calculate optimal font size to fit text within box dimensions
 * Uses opentype.js for accurate calculation with heuristic fallback
 *
 * @param {string} text - Text content to fit
 * @param {number} boxWidth - Box width in inches
 * @param {number} boxHeight - Box height in inches
 * @param {object} options - Font options (fontFace, bold, minSize, maxSize)
 * @returns {number} Optimal font size in points
 */
function calculateFitFontSize(text, boxWidth, boxHeight, options = {}) {
  const {
    fontFace = 'Arial',
    bold = false,
    minSize = 10,
    maxSize = 44
  } = options;

  // Handle empty or invalid text
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    return 18; // Default size
  }

  // Convert inches to pixels (72 DPI standard for PowerPoint)
  const boxWidthPx = boxWidth * 72;
  const boxHeightPx = boxHeight * 72;

  // Try to load font using opentype.js
  const font = loadFont(fontFace);

  if (font) {
    // ✅ ACCURATE MODE: Use actual font geometry
    let fontSize = maxSize;

    while (fontSize >= minSize) {
      // Measure text width using actual font geometry
      const textWidthPx = measureTextWidth(text, font, fontSize);

      // Estimate number of lines needed
      const lines = Math.ceil(textWidthPx / boxWidthPx);

      // Estimate total height with line spacing (1.2x multiplier is standard)
      const lineHeight = fontSize * 1.2;
      const textHeightPx = lines * lineHeight;

      // Check if text fits
      if (textWidthPx <= boxWidthPx && textHeightPx <= boxHeightPx) {
        return fontSize;
      }

      fontSize -= 2; // Decrease by 2pt increments
    }

    return minSize; // Minimum size if nothing fits

  } else {
    // ⚠️ FALLBACK MODE: Font not available, use heuristic
    return calculateFitFontSizeHeuristic(text, boxWidth, boxHeight, options);
  }
}

/**
 * Heuristic-based font size calculation (fallback when font file not available)
 * Based on character count and box area
 *
 * @param {string} text - Text content
 * @param {number} boxWidth - Box width in inches
 * @param {number} boxHeight - Box height in inches
 * @param {object} options - Font options
 * @returns {number} Estimated font size in points
 */
function calculateFitFontSizeHeuristic(text, boxWidth, boxHeight, options = {}) {
  const {
    bold = false,
    minSize = 10,
    maxSize = 44
  } = options;

  const charCount = text.length;

  // Handle very short text - should use large font
  if (charCount <= 20) {
    // For short text, use box dimensions to determine font size
    const smallerDimension = Math.min(boxWidth, boxHeight);
    let fontSize = smallerDimension * 20; // Rough: 1 inch = ~20pt for short text
    return Math.max(minSize, Math.min(maxSize, Math.round(fontSize)));
  }

  // For longer text, calculate based on character density
  // Average character width at 18pt ≈ 0.1 inches for Arial
  const avgCharWidthAt18pt = 0.1;
  const avgCharHeightAt18pt = 0.25; // Including line spacing

  // Estimate how many characters can fit per line at 18pt
  const charsPerLineAt18pt = boxWidth / avgCharWidthAt18pt;
  const linesNeededAt18pt = Math.ceil(charCount / charsPerLineAt18pt);

  // Check if we need to scale down from 18pt
  const heightNeededAt18pt = linesNeededAt18pt * avgCharHeightAt18pt;

  let fontSize = 18;

  if (heightNeededAt18pt > boxHeight) {
    // Need to scale down
    const scaleFactor = boxHeight / heightNeededAt18pt;
    fontSize = 18 * scaleFactor;
  } else if (charCount < 50 && boxWidth * boxHeight > 8) {
    // Medium length text in large box - can scale up
    const scaleFactor = Math.min(1.5, Math.sqrt((boxWidth * boxHeight) / 8));
    fontSize = 18 * scaleFactor;
  }

  // Adjust for bold (takes more space)
  if (bold) {
    fontSize *= 0.95;
  }

  // Clamp to reasonable range
  fontSize = Math.max(minSize, Math.min(maxSize, Math.round(fontSize)));

  return fontSize;
}

/**
 * Detect if text has formatting that affects sizing
 * @param {string|array} content - Text content or text runs array
 * @returns {boolean} True if content has bold/italic formatting
 */
function hasFormatting(content) {
  if (Array.isArray(content)) {
    return content.some(run => run.options && (run.options.bold || run.options.italic));
  }
  if (typeof content === 'string') {
    return /\*\*|\*|__/.test(content); // Check for markdown formatting
  }
  return false;
}

// ==================== AUTO-LAYOUT MODE ====================

/**
 * Parse full markdown document to elements with vertical flow
 * Supports: # H1-H6, paragraphs, - bullets, 1. numbered lists, | tables |, > blockquotes, ```code```
 */
function parseMarkdownToElements(markdown) {
  const md = new MarkdownIt();
  const html = md.render(markdown);
  const $ = cheerio.load(html);

  const elements = [];
  let currentY = 0.5; // Starting Y position
  const marginX = 0.5;
  const contentWidth = 9; // Standard slide width minus margins

  $('h1, h2, h3, h4, h5, h6, p, ul, ol, table, blockquote, pre').each((i, elem) => {
    const tag = elem.name;

    if (tag === 'h1') {
      // H1 = Main title (centered, large)
      const text = $(elem).text();
      elements.push({
        type: 'text',
        content: parseInlineMarkdown($(elem).html()),
        position: { x: marginX, y: currentY, w: contentWidth, h: 1.5 },
        style: { fontSize: 44, bold: true, align: 'center' }
      });
      currentY += 2.0;

    } else if (tag.match(/h[2-6]/)) {
      // H2-H6 = Headings (decreasing sizes)
      const level = parseInt(tag[1]);
      const sizes = [null, 44, 32, 28, 24, 20, 18]; // H1-H6
      const text = $(elem).text();
      elements.push({
        type: 'text',
        content: parseInlineMarkdown($(elem).html()),
        position: { x: marginX, y: currentY, w: contentWidth, h: 0.8 },
        style: { fontSize: sizes[level], bold: true }
      });
      currentY += 1.0;

    } else if (tag === 'p') {
      // Paragraph = Body text
      const text = $(elem).text();
      if (text.trim()) {
        elements.push({
          type: 'text',
          content: parseInlineMarkdown($(elem).html()),
          position: { x: marginX, y: currentY, w: contentWidth, h: 0.6 },
          style: { fontSize: 18 }
        });
        currentY += 0.8;
      }

    } else if (tag === 'ul' || tag === 'ol') {
      // Unordered/ordered list = Bullets
      const items = [];
      $(elem).find('li').each((j, li) => {
        // Handle nested lists
        const text = $(li).clone().children().remove().end().text().trim();
        if (text) {
          items.push({ text, level: 0 }); // Simplified: all level 0 for now
        }
      });

      if (items.length > 0) {
        elements.push({
          type: 'bullets',
          items: items,
          numbered: tag === 'ol',
          position: { x: marginX, y: currentY, w: contentWidth, h: 0.5 + items.length * 0.3 }
        });
        currentY += 0.8 + items.length * 0.3;
      }

    } else if (tag === 'table') {
      // Table
      const rows = [];
      $(elem).find('tr').each((j, tr) => {
        const cells = [];
        $(tr).find('th, td').each((k, cell) => {
          cells.push($(cell).text().trim());
        });
        if (cells.length > 0) {
          rows.push(cells);
        }
      });

      if (rows.length > 0) {
        elements.push({
          type: 'table',
          data: rows,
          position: { x: marginX, y: currentY, w: contentWidth, h: 0.5 + rows.length * 0.3 }
        });
        currentY += 0.8 + rows.length * 0.3;
      }

    } else if (tag === 'blockquote') {
      // Blockquote = Indented text
      const text = $(elem).text().trim();
      if (text) {
        elements.push({
          type: 'text',
          content: [{ text: text }],
          position: { x: marginX + 0.5, y: currentY, w: contentWidth - 0.5, h: 0.8 },
          style: { fontSize: 16, italic: true, color: '666666' }
        });
        currentY += 1.0;
      }

    } else if (tag === 'pre') {
      // Code block = Monospace text
      const text = $(elem).text().trim();
      if (text) {
        elements.push({
          type: 'text',
          content: [{ text: text, options: { fontFace: 'Courier New' } }],
          position: { x: marginX, y: currentY, w: contentWidth, h: 0.5 + text.split('\n').length * 0.2 },
          style: { fontSize: 14, fontFace: 'Courier New' }
        });
        currentY += 0.8 + text.split('\n').length * 0.2;
      }
    }
  });

  return elements;
}

// ==================== ELEMENT CREATION ====================

/**
 * Add element to PPTXgenJS slide
 */
function addElementToSlide(slide, element) {
  const { type, content, data, items, numbered, position, style, autoFit } = element;

  if (type === 'text') {
    // Text box
    const textContent = Array.isArray(content) ? content : [{ text: content }];

    // Auto-fit by default (can be disabled with autoFit: false)
    let fontSize = style?.fontSize;

    // Only auto-fit if: fontSize not explicitly set AND autoFit not explicitly disabled
    const shouldAutoFit = (autoFit !== false) && !fontSize && position;

    if (shouldAutoFit) {
      // Extract plain text for measurement
      const plainText = textContent
        .map(run => (typeof run === 'string' ? run : run.text || ''))
        .join('');

      // Calculate optimal font size
      fontSize = calculateFitFontSize(plainText, position.w, position.h, {
        fontFace: style?.fontFace || 'Arial',
        bold: style?.bold || hasFormatting(textContent),
        minSize: style?.minFontSize || 10,
        maxSize: style?.maxFontSize || 44
      });
    }

    const options = {
      x: position.x,
      y: position.y,
      w: position.w,
      h: position.h,
      fontSize: fontSize || 18,
      bold: style?.bold || false,
      italic: style?.italic || false,
      align: style?.align || 'left',
      color: style?.color || '000000',
      fontFace: style?.fontFace || 'Arial',
      valign: 'top'
    };

    slide.addText(textContent, options);

  } else if (type === 'table') {
    // Table
    const rows = data.map(row => row.map(cell => ({ text: cell })));
    slide.addTable(rows, {
      x: position.x,
      y: position.y,
      w: position.w,
      h: position.h,
      border: { pt: 1, color: 'CCCCCC' },
      fill: { color: 'F7F7F7' },
      fontSize: 12
    });

  } else if (type === 'bullets') {
    // Bullet list
    const textObjs = items.map(item => ({
      text: item.text,
      options: {
        bullet: numbered ? { type: 'number' } : true,
        indentLevel: item.level || 0
      }
    }));

    slide.addText(textObjs, {
      x: position.x,
      y: position.y,
      w: position.w,
      h: position.h,
      fontSize: 18
    });
  }
}

// ==================== PRESENTATION SERIALIZATION ====================

/**
 * Serialize PPTXgenJS presentation to base64
 */
async function serializePresentation(pres) {
  const buffer = await pres.write('arraybuffer');
  return Buffer.from(buffer).toString('base64');
}

/**
 * Build standard file response object
 */
async function buildFileResponse(pres, filename = 'presentation.pptx') {
  const content = await serializePresentation(pres);
  return {
    content,
    name: filename.endsWith('.pptx') ? filename : `${filename}.pptx`,
    contentType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
  };
}

// ==================== ACTION HANDLERS ====================

/**
 * Action: create_presentation
 * Create new presentation with optional master slide template
 */
async function createPresentation(inputs, context) {
  const { title, author, master, slides, custom_filename } = inputs;

  // Create new presentation
  const pres = new pptxgen();

  // Set metadata
  if (title) pres.title = title;
  if (author) pres.author = author;

  // Define master slide if provided
  let masterDefined = false;
  let masterName = null;

  if (master && master.title) {
    const masterConfig = {
      title: master.title,
      background: master.background || { color: 'FFFFFF' },
      objects: master.objects || [],
      slideNumber: master.slideNumber || null
    };

    pres.defineSlideMaster(masterConfig);
    masterDefined = true;
    masterName = master.title;
  }

  // Create initial slides if provided
  let slideCount = 0;
  if (slides && Array.isArray(slides)) {
    for (const slideData of slides) {
      const slideOptions = masterName ? { masterName } : undefined;
      const slide = pres.addSlide(slideOptions);

      if (slideData.markdown) {
        // Parse markdown and add elements
        const elements = parseMarkdownToElements(slideData.markdown);
        for (const elem of elements) {
          addElementToSlide(slide, elem);
        }
      }

      slideCount++;
    }
  }

  // If no slides created, add one blank slide
  if (slideCount === 0) {
    const slideOptions = masterName ? { masterName } : undefined;
    pres.addSlide(slideOptions);
    slideCount = 1;
  }

  // Generate presentation ID
  const presentationId = `pres_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Store in memory
  presentations.set(presentationId, { pres, masterName });

  // Build response
  const filename = custom_filename || `${presentationId}.pptx`;
  const file = await buildFileResponse(pres, filename);

  return {
    presentation_id: presentationId,
    slide_count: slideCount,
    master_defined: masterDefined,
    master_name: masterName,
    file
  };
}

/**
 * Action: generate_slides
 * Generate multiple slides from data array + template (POWER FEATURE)
 */
async function generateSlides(inputs, context) {
  const { files, template, data, master } = inputs;

  // Load or get cached presentation
  let pres, masterName;
  if (files && files.length > 0) {
    // For now, we'll need to recreate from scratch since PPTXgenJS can't read
    // This is a limitation - in production, might need to maintain state
    throw new Error('Loading existing presentations not yet supported in this version. Use create_presentation first, then call this in same session.');
  } else {
    // Try to find most recent presentation
    if (presentations.size === 0) {
      throw new Error('No presentation found. Create a presentation first.');
    }
    // Get most recent
    const entries = Array.from(presentations.entries());
    const latest = entries[entries.length - 1];
    pres = latest[1].pres;
    masterName = master || latest[1].masterName;
  }

  // Parse template and generate slides
  const { markdown_template } = template;
  let slidesGenerated = 0;

  for (const dataObj of data) {
    // Render template with data using Mustache
    const renderedMarkdown = Mustache.render(markdown_template, dataObj);

    // Create slide
    const slideOptions = masterName ? { masterName } : undefined;
    const slide = pres.addSlide(slideOptions);

    // Parse markdown and add elements
    const elements = parseMarkdownToElements(renderedMarkdown);
    for (const elem of elements) {
      addElementToSlide(slide, elem);
    }

    slidesGenerated++;
  }

  // Get total slides (PPTXgenJS doesn't have direct count, estimate)
  const totalSlides = slidesGenerated; // Simplified

  // Build response
  const file = await buildFileResponse(pres);

  return {
    slides_generated: slidesGenerated,
    template_used: markdown_template.substring(0, 100) + '...',
    total_slides: totalSlides,
    file
  };
}

/**
 * Pre-load fonts for elements (downloads from Google Fonts if needed)
 *
 * @param {array} elements - Array of elements that might use fonts
 * @returns {Promise<void>}
 */
async function preloadFontsForElements(elements) {
  if (!elements || !Array.isArray(elements)) return;

  // Collect unique fonts from all elements
  const fontsNeeded = new Set();

  for (const elem of elements) {
    const fontFace = elem.style?.fontFace;
    if (fontFace) {
      fontsNeeded.add(fontFace);
    }
  }

  // Download any missing fonts
  for (const fontName of fontsNeeded) {
    // Check if already cached or bundled
    if (!fontCache.has(fontName)) {
      const font = loadFont(fontName);
      if (!font) {
        // Not found locally - try downloading
        await downloadAndCacheFont(fontName);
      }
    }
  }
}

/**
 * Action: add_content
 * Add content to slide using markdown or HTML
 */
async function addContent(inputs, context) {
  const { files, slide_index, auto_layout, markdown, elements, html_table } = inputs;

  // Get presentation
  let pres;
  if (presentations.size === 0) {
    throw new Error('No presentation found. Create a presentation first.');
  }
  const entries = Array.from(presentations.entries());
  const latest = entries[entries.length - 1];
  pres = latest[1].pres;

  // Pre-load any custom fonts (downloads from Google Fonts if needed)
  if (elements && Array.isArray(elements)) {
    await preloadFontsForElements(elements);
  }

  // Get slide (PPTXgenJS uses 0-based index, but slides are added sequentially)
  // This is a limitation - PPTXgenJS doesn't provide easy access to existing slides by index
  // For MVP, we'll work with adding content to new slides or most recent

  let mode = 'granular';
  let elementsAdded = 0;

  if (html_table) {
    // HTML table mode
    mode = 'html_table';
    const slide = pres.addSlide();
    const tableData = parseHTMLTable(html_table);
    const rows = tableData.map(row => row.map(cell => ({ text: cell })));
    slide.addTable(rows, {
      x: 0.5,
      y: 1,
      w: 9,
      h: 5,
      border: { pt: 1, color: 'CCCCCC' }
    });
    elementsAdded = 1;

  } else if (auto_layout && markdown) {
    // Auto-layout mode
    mode = 'auto_layout';
    const slide = pres.addSlide();
    const parsedElements = parseMarkdownToElements(markdown);
    for (const elem of parsedElements) {
      addElementToSlide(slide, elem);
    }
    elementsAdded = parsedElements.length;

  } else if (elements && Array.isArray(elements)) {
    // Granular mode
    mode = 'granular';
    const slide = pres.addSlide();

    for (const elem of elements) {
      const type = detectElementType(elem.content);
      const pos = elem.position || { x: 0.5, y: 0.5, w: 8, h: 3 };

      if (type === 'table') {
        const tableData = parseMarkdownTable(elem.content);
        const rows = tableData.map(row => row.map(cell => ({ text: cell })));
        slide.addTable(rows, {
          x: pos.x,
          y: pos.y,
          w: pos.w,
          h: pos.h,
          border: { pt: 1, color: 'CCCCCC' }
        });
      } else if (type === 'bullets') {
        const items = parseMarkdownBullets(elem.content);
        const textObjs = items.map(item => ({
          text: item.text,
          options: { bullet: true, indentLevel: item.level }
        }));
        slide.addText(textObjs, {
          x: pos.x,
          y: pos.y,
          w: pos.w,
          h: pos.h,
          fontSize: 18
        });
      } else {
        // Text - auto-fitting enabled by default
        const textRuns = parseInlineMarkdown(elem.content);

        // Auto-fit by default unless fontSize explicitly provided or autoFit explicitly disabled
        let fontSize = elem.style?.fontSize;
        const shouldAutoFit = (elem.autoFit !== false) && !fontSize;

        if (shouldAutoFit) {
          const plainText = textRuns.map(run => run.text || '').join('');
          fontSize = calculateFitFontSize(plainText, pos.w, pos.h, {
            fontFace: elem.style?.fontFace || 'Arial',
            bold: elem.style?.bold || hasFormatting(textRuns),
            minSize: elem.style?.minFontSize || 10,
            maxSize: elem.style?.maxFontSize || 44
          });
        } else if (!fontSize) {
          fontSize = 18; // Default if auto-fit disabled
        }

        slide.addText(textRuns, {
          x: pos.x,
          y: pos.y,
          w: pos.w,
          h: pos.h,
          fontSize: fontSize,
          ...elem.style
        });
      }

      elementsAdded++;
    }
  }

  // Build response
  const file = await buildFileResponse(pres);

  return {
    mode,
    elements_added: elementsAdded,
    total_slides: elementsAdded, // Simplified
    file
  };
}

/**
 * Action: add_chart_and_images
 * Add charts and/or images to slide
 */
async function addChartAndImages(inputs, context) {
  const { files, slide_index, items } = inputs;

  // Get presentation
  let pres;
  if (presentations.size === 0) {
    throw new Error('No presentation found. Create a presentation first.');
  }
  const entries = Array.from(presentations.entries());
  const latest = entries[entries.length - 1];
  pres = latest[1].pres;

  // Create new slide
  const slide = pres.addSlide();

  let itemsAdded = 0;

  for (const item of items) {
    const { type, chartType, data, position, options } = item;

    if (type === 'chart') {
      // Add chart
      const chartData = [];
      if (Array.isArray(data)) {
        // Assume data format: [{ name, labels, values }]
        for (const series of data) {
          chartData.push({
            name: series.name,
            labels: series.labels,
            values: series.values
          });
        }
      }

      slide.addChart(pres.ChartType[chartType.toUpperCase()] || chartType, chartData, {
        x: position.x,
        y: position.y,
        w: position.w,
        h: position.h,
        ...options
      });

      itemsAdded++;

    } else if (type === 'image') {
      // Add image
      slide.addImage({
        data: data,
        x: position.x,
        y: position.y,
        w: position.w,
        h: position.h,
        ...options
      });

      itemsAdded++;
    }
  }

  // Build response
  const file = await buildFileResponse(pres);

  return {
    items_added: itemsAdded,
    total_slides: 1, // Simplified
    file
  };
}

// ==================== FIND AND REPLACE (XML MANIPULATION) ====================

/**
 * Escape XML special characters
 */
function escapeXML(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Extract box dimensions from PowerPoint XML shape
 * Returns dimensions in inches
 */
function extractBoxDimensions(shapeXml) {
  // Look for <a:ext cx="..." cy="..."/> (EMUs - English Metric Units)
  const extMatch = shapeXml.match(/<a:ext[^>]+cx="(\d+)"[^>]+cy="(\d+)"/);

  if (extMatch) {
    const widthEMU = parseInt(extMatch[1]);
    const heightEMU = parseInt(extMatch[2]);

    // Convert EMUs to inches (914400 EMUs = 1 inch)
    return {
      w: widthEMU / 914400,
      h: heightEMU / 914400
    };
  }

  // Default if not found
  return { w: 8, h: 2 };
}

/**
 * Extract font face from PowerPoint XML run properties
 */
function extractFontFace(runPropsXml) {
  // Look for <a:latin typeface="FontName"/>
  const match = runPropsXml.match(/<a:latin typeface="([^"]+)"/);
  return match ? match[1] : 'Arial';
}

/**
 * Recursively find all paragraphs (<a:p>) in XML object tree
 * Returns array of paragraph objects with their parent reference
 */
function findAllParagraphs(obj, path = [], results = []) {
  if (!obj || typeof obj !== 'object') return results;

  // Check if this is a paragraph (<a:p>)
  if (obj['a:p'] && Array.isArray(obj['a:p'])) {
    obj['a:p'].forEach((para, index) => {
      results.push({
        paragraph: para,
        parent: obj,
        parentKey: 'a:p',
        index: index,
        path: [...path, 'a:p', index]
      });
    });
  }

  // Recursively search in all properties (including arrays)
  for (const key in obj) {
    const value = obj[key];

    if (Array.isArray(value)) {
      value.forEach((item, idx) => {
        if (item && typeof item === 'object') {
          findAllParagraphs(item, [...path, key, idx], results);
        }
      });
    } else if (value && typeof value === 'object') {
      findAllParagraphs(value, [...path, key], results);
    }
  }

  return results;
}

/**
 * Extract text from all runs in a paragraph
 * Returns concatenated text and run information
 */
function extractTextFromParagraph(paragraph) {
  const runs = paragraph['a:r'] || [];
  const texts = [];

  for (const run of runs) {
    const textNode = run['a:t'];
    if (textNode) {
      // Text might be string or array with one element
      const text = Array.isArray(textNode) ? textNode[0] : textNode;
      const actualText = typeof text === 'string' ? text : (text._ || text || '');
      texts.push(actualText);
    }
  }

  return {
    fullText: texts.join(''),
    runs: runs,
    textCount: texts.length
  };
}

/**
 * Create XML run objects for markdown-formatted text
 * Returns array of run objects ready for xml2js
 */
function createFormattedRuns(textRuns, fontSize, fontFace) {
  const fontSizeHundredths = Math.round(fontSize * 100);
  const runs = [];

  for (const run of textRuns) {
    const text = typeof run === 'string' ? run : run.text || '';
    if (!text) continue;

    const runObj = {
      'a:rPr': [{
        $: {
          'lang': 'en-US',
          'sz': fontSizeHundredths.toString(),
          'dirty': '0'
        },
        'a:latin': [{
          $: { 'typeface': fontFace }
        }]
      }],
      'a:t': [text]
    };

    // Add formatting attributes
    if (run.options?.bold) {
      runObj['a:rPr'][0].$.b = '1';
    }
    if (run.options?.italic) {
      runObj['a:rPr'][0].$.i = '1';
    }
    if (run.options?.underline) {
      runObj['a:rPr'][0].$.u = 'sng';
    }

    runs.push(runObj);
  }

  return runs;
}

/**
 * Find and replace text in PowerPoint slide XML using xml2js parser
 * Handles text split across multiple runs
 * Applies markdown formatting to replacement text
 * Integrates auto-fitting
 */
async function findAndReplaceInSlideXML(slideXml, find, replace, shapeXml) {
  try {
    // Parse XML to JavaScript object
    // Important: Keep namespace prefixes (p:, a:, etc.) in tag names
    const parser = new xml2js.Parser({
      explicitArray: true,
      preserveChildrenOrder: true,
      tagNameProcessors: [], // Don't strip namespaces
      attrNameProcessors: [], // Don't process attribute names
      xmlns: false, // Don't parse namespaces separately
      explicitRoot: true
    });

    const slideObj = await parser.parseStringPromise(slideXml);

    // Extract box dimensions for auto-fitting
    const boxDims = extractBoxDimensions(slideXml);

    // Extract original font face
    const originalFont = extractFontFace(slideXml);

    // Parse markdown in replacement text
    const textRuns = parseInlineMarkdown(replace);
    const plainText = textRuns.map(run => (typeof run === 'string' ? run : run.text || '')).join('');

    // Calculate font size using auto-fitting
    const hasBold = textRuns.some(run => run.options?.bold);
    const fontSize = await calculateFitFontSize(plainText, boxDims.w, boxDims.h, {
      fontFace: originalFont,
      bold: hasBold
    });

    // Find all paragraphs in the slide
    const paragraphs = findAllParagraphs(slideObj);

    let replacementMade = false;

    // Process each paragraph
    for (const paraInfo of paragraphs) {
      const para = paraInfo.paragraph;

      // Extract text from all runs
      const { fullText, runs } = extractTextFromParagraph(para);

      // Check if this paragraph contains the search text
      if (fullText.includes(find)) {
        // Create new runs with markdown formatting
        const newRuns = createFormattedRuns(textRuns, fontSize, originalFont);

        // Replace the runs in the paragraph
        para['a:r'] = newRuns;

        replacementMade = true;
      }
    }

    // Only rebuild XML if a replacement was made
    if (!replacementMade) {
      return slideXml; // No changes
    }

    // Rebuild XML from modified object
    const builder = new xml2js.Builder({
      xmldec: { 'version': '1.0', 'encoding': 'UTF-8', 'standalone': 'yes' },
      renderOpts: { 'pretty': false }  // No pretty-printing (PowerPoint prefers compact)
    });

    const newXml = builder.buildObject(slideObj);

    return newXml;

  } catch (error) {
    // If xml2js parsing fails, fall back to returning original XML
    console.warn(`XML parsing failed for find/replace: ${error.message}`);
    return slideXml;
  }
}

/**
 * Apply all replacements to a single slide object
 * Modifies the slide object in place
 * Returns count of replacements made
 */
async function applyReplacementsToSlide(slideObj, replacements, slideXmlForDims) {
  const replacementCounts = new Map();

  // Initialize counts
  for (const replacement of replacements) {
    replacementCounts.set(replacement.find, 0);
  }

  // Extract box dimensions for auto-fitting (from original XML)
  const boxDims = extractBoxDimensions(slideXmlForDims);
  const originalFont = extractFontFace(slideXmlForDims);

  // Find all paragraphs in this slide
  const paragraphs = findAllParagraphs(slideObj);

  // Process each paragraph
  for (const paraInfo of paragraphs) {
    const para = paraInfo.paragraph;

    // Extract text from all runs
    const { fullText, runs } = extractTextFromParagraph(para);

    // Check ALL replacements against this paragraph
    for (const replacement of replacements) {
      if (fullText.includes(replacement.find)) {
        // Parse markdown in replacement text
        const textRuns = parseInlineMarkdown(replacement.replace);
        const plainText = textRuns.map(run => (typeof run === 'string' ? run : run.text || '')).join('');

        // Calculate font size using auto-fitting
        const hasBold = textRuns.some(run => run.options?.bold);
        const fontSize = await calculateFitFontSize(plainText, boxDims.w, boxDims.h, {
          fontFace: originalFont,
          bold: hasBold
        });

        // Create new runs with markdown formatting
        const newRuns = createFormattedRuns(textRuns, fontSize, originalFont);

        // Replace the runs in the paragraph
        para['a:r'] = newRuns;

        // Increment count for this replacement
        const count = replacementCounts.get(replacement.find) || 0;
        replacementCounts.set(replacement.find, count + 1);

        // Only replace once per paragraph
        break;
      }
    }
  }

  return replacementCounts;
}

/**
 * Count all matches for a find phrase across all slides
 * Returns array of match locations with context
 */
async function countAllMatches(zip, slideFiles, findText) {
  const matches = [];
  const parser = new xml2js.Parser({
    explicitArray: true,
    preserveChildrenOrder: true,
    tagNameProcessors: [],
    attrNameProcessors: [],
    xmlns: false,
    explicitRoot: true
  });

  for (const slideFile of slideFiles) {
    const slideXml = await zip.file(slideFile).async('text');

    // Quick check before parsing
    if (!slideXml.includes(findText)) {
      continue;
    }

    try {
      // Parse slide
      const slideObj = await parser.parseStringPromise(slideXml);
      const paragraphs = findAllParagraphs(slideObj);

      // Check each paragraph
      paragraphs.forEach((paraInfo, paraIdx) => {
        const { fullText } = extractTextFromParagraph(paraInfo.paragraph);

        if (fullText.includes(findText)) {
          const slideNum = parseInt(slideFile.match(/slide(\d+)/)[1]);

          matches.push({
            type: "text_paragraph",
            slide_index: slideNum - 1,
            slide_number: slideNum,
            paragraph_index: paraIdx,
            content: fullText.substring(0, 80) + (fullText.length > 80 ? '...' : ''),
            location: `Slide ${slideNum}, Paragraph ${paraIdx}`
          });
        }
      });
    } catch (error) {
      // Skip slides that fail to parse
      console.warn(`Failed to parse ${slideFile} for match counting: ${error.message}`);
    }
  }

  return matches;
}

/**
 * Action: find_and_replace
 * Find and replace text in existing PowerPoint template
 * Supports markdown formatting and auto-fitting
 * OPTIMIZED: Parses each slide ONCE, applies ALL replacements, rebuilds ONCE
 * SAFETY: Blocks replacements if multiple matches found without replace_all=true
 */
async function findAndReplace(inputs, context) {
  const { files, replacements } = inputs;

  // Find PPTX file
  const pptxFile = files.find(f => f.name.toLowerCase().endsWith('.pptx'));
  if (!pptxFile) {
    throw new Error('No PPTX file found in files parameter');
  }

  // Decode base64 to buffer
  const pptxBuffer = await normalizeToBuffer(pptxFile.content);

  // Load PPTX as ZIP
  const zip = await JSZip.loadAsync(pptxBuffer);

  // Find all slide files
  const slideFiles = Object.keys(zip.files)
    .filter(name => name.match(/ppt\/slides\/slide\d+\.xml$/))
    .sort();

  // ==================== PHASE 1: PRE-SCAN FOR MATCHES (SAFETY CHECK) ====================
  const blocked = [];
  const replacementPlan = [];

  console.log('Pre-scanning for matches...');

  for (const replacement of replacements) {
    const findText = replacement.find;
    const replaceAll = replacement.replace_all || false;

    // Count all matches for this find phrase
    const matches = await countAllMatches(zip, slideFiles, findText);

    if (matches.length === 0) {
      // Not found
      replacementPlan.push({
        ...replacement,
        action: 'skip_not_found',
        matches: []
      });
    } else if (matches.length > 1 && !replaceAll) {
      // BLOCK - multiple matches without permission
      blocked.push({
        BLOCKED: `'${findText}' found ${matches.length} times - requires replace_all=true`,
        find_phrase: findText,
        match_count: matches.length,
        matches: matches.slice(0, 5),  // First 5 match locations
        fix_required: `Either add more context to find phrase to make it unique (e.g., "${findText} specific text"), OR set replace_all=true to confirm replacing all ${matches.length} instances`
      });
      replacementPlan.push({
        ...replacement,
        action: 'block_multiple',
        matches: matches
      });
    } else {
      // OK to replace (single match OR replace_all=true)
      replacementPlan.push({
        ...replacement,
        action: 'replace',
        matches: matches
      });
    }
  }

  console.log(`Pre-scan complete: ${replacementPlan.filter(p => p.action === 'replace').length} to replace, ${blocked.length} blocked`);

  // ==================== PHASE 2: APPLY NON-BLOCKED REPLACEMENTS ====================
  const replacementDetails = [];
  const replacementsToApply = replacementPlan.filter(p => p.action === 'replace');

  // Initialize details for ALL replacements
  for (const plan of replacementPlan) {
    replacementDetails.push({
      find: plan.find,
      replace: plan.replace,
      matches_found: plan.action === 'replace' ? plan.matches.length : plan.matches.length,
      status: plan.action === 'replace' ? (plan.matches.length > 0 ? 'replaced' : 'not_found') :
              plan.action === 'block_multiple' ? 'blocked' : 'not_found'
    });
  }

  // Only process if there are replacements to make
  if (replacementsToApply.length > 0) {
    const parser = new xml2js.Parser({
      explicitArray: true,
      preserveChildrenOrder: true,
      tagNameProcessors: [],
      attrNameProcessors: [],
      xmlns: false,
      explicitRoot: true
    });

    const builder = new xml2js.Builder({
      xmldec: { 'version': '1.0', 'encoding': 'UTF-8', 'standalone': 'yes' },
      renderOpts: { 'pretty': false }
    });

    for (const slideFile of slideFiles) {
      const slideXml = await zip.file(slideFile).async('text');

      // Quick check: skip if no placeholders in this slide
      const hasAnyPlaceholder = replacementsToApply.some(r => slideXml.includes(r.find));
      if (!hasAnyPlaceholder) {
        continue;
      }

      try {
        // Parse ONCE
        const slideObj = await parser.parseStringPromise(slideXml);

        // Apply only non-blocked replacements
        const counts = await applyReplacementsToSlide(slideObj, replacementsToApply, slideXml);

        // Check if any changes were made
        let slideModified = false;
        counts.forEach((count, find) => {
          if (count > 0) {
            slideModified = true;
          }
        });

        // Rebuild ONCE (only if modified)
        if (slideModified) {
          const newXml = builder.buildObject(slideObj);
          zip.file(slideFile, newXml);
        }

      } catch (error) {
        console.warn(`Failed to process ${slideFile}: ${error.message}`);
      }
    }
  }

  // Repackage PPTX
  const newBuffer = await zip.generateAsync({
    type: 'nodebuffer',
    compression: 'DEFLATE',
    compressionOptions: { level: 9 }
  });

  // Calculate totals
  const totalReplacements = replacementDetails.filter(r => r.status === 'replaced').reduce((sum, d) => sum + d.matches_found, 0);
  const notFound = replacementDetails.filter(r => r.status === 'not_found');
  const found = replacementDetails.filter(r => r.status === 'replaced');
  const blockedDetails = replacementDetails.filter(r => r.status === 'blocked');

  // Build message
  let message = '';
  if (totalReplacements > 0 && blocked.length === 0) {
    message = `Successfully replaced ${totalReplacements} placeholder(s) across all slides`;
  } else if (totalReplacements > 0 && blocked.length > 0) {
    message = `Partially successful: replaced ${totalReplacements} placeholder(s), but ${blocked.length} replacement(s) blocked due to multiple matches`;
  } else if (blocked.length > 0) {
    message = `${blocked.length} replacement(s) blocked due to multiple matches. Use replace_all=true or provide more specific text. See 'blocked' array for details.`;
  } else if (notFound.length > 0) {
    message = `No placeholders found. The template may not contain the specified placeholders, or they may be spelled differently.`;
  }

  // Build warning
  let warning = null;
  if (notFound.length > 0 || blocked.length > 0) {
    const warnings = [];
    if (notFound.length > 0) {
      warnings.push(`${notFound.length} not found: ${notFound.map(r => `"${r.find}"`).join(', ')}`);
    }
    if (blocked.length > 0) {
      warnings.push(`${blocked.length} blocked (multiple matches): ${blocked.map(b => `"${b.find_phrase}"`).join(', ')}`);
    }
    warning = warnings.join('; ');
  }

  return {
    success: totalReplacements > 0 && blocked.length === 0,
    total_replacements: totalReplacements,
    replacements_requested: replacements.length,
    replacements_found: found.length,
    replacements_not_found: notFound.length,
    blocked_count: blocked.length,
    blocked: blocked,
    details: replacementDetails,
    warning: warning,
    message: message,
    file: {
      content: newBuffer.toString('base64'),
      name: pptxFile.name.replace('.pptx', '_filled.pptx'),
      contentType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }
  };
}

// ==================== MAIN ENTRY POINT ====================

/**
 * Main action executor
 * Called by Autohive platform
 */
async function executeAction(actionName, inputs, context) {
  switch (actionName) {
    case 'create_presentation':
      return await createPresentation(inputs, context);

    case 'generate_slides':
      return await generateSlides(inputs, context);

    case 'add_content':
      return await addContent(inputs, context);

    case 'add_chart_and_images':
      return await addChartAndImages(inputs, context);

    case 'find_and_replace':
      return await findAndReplace(inputs, context);

    default:
      throw new Error(`Unknown action: ${actionName}`);
  }
}

// ==================== EXPORTS ====================

const integration = { executeAction };

module.exports = {
  integration,
  executeAction,
  // Export utilities for testing
  detectElementType,
  parseMarkdownTable,
  parseMarkdownBullets,
  parseInlineMarkdown,
  parseMarkdownToElements,
  calculateFitFontSize,
  downloadAndCacheFont,
  findAllParagraphs,
  extractTextFromParagraph
};
