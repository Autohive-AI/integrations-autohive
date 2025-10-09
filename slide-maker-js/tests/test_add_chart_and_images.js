const { executeAction } = require('../slide_maker');
const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Sample 1x1 red pixel PNG in base64 (for testing image functionality)
const SAMPLE_IMAGE_BASE64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';

// Sample logo-like image (small blue square)
const SAMPLE_LOGO = 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNk+M9Qz0AEYBxVSF+FAP0QAgUr0g1LAAAAAElFTkSuQmCC';

async function testBarChart() {
  console.log('Test 1: Add bar chart...');

  const createInputs = {
    title: 'Chart Tests',
    slides: [{ markdown: '# Bar Chart Example' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    const addInputs = {
      slide_index: 0,
      items: [
        {
          type: 'chart',
          chartType: 'bar',
          data: [
            {
              name: '2023',
              labels: ['Q1', 'Q2', 'Q3', 'Q4'],
              values: [65, 78, 92, 110]
            },
            {
              name: '2024',
              labels: ['Q1', 'Q2', 'Q3', 'Q4'],
              values: [82, 95, 115, 138]
            }
          ],
          position: { x: 1, y: 1.5, w: 8, h: 4.5 },
          options: {
            title: 'Quarterly Revenue ($K)',
            showLegend: true,
            showTitle: true
          }
        }
      ]
    };

    const result = await executeAction('add_chart_and_images', addInputs, {});

    console.log('✓ Bar chart added');
    console.log('  - Items added:', result.items_added);

    const outputPath = path.join(outputDir, 'test_bar_chart.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testMultipleCharts() {
  console.log('\nTest 2: Add multiple chart types...');

  const createInputs = {
    title: 'Multiple Charts',
    slides: [
      { markdown: '# Slide 1: Bar vs Line' },
      { markdown: '# Slide 2: Pie Chart' },
      { markdown: '# Slide 3: Area Chart' }
    ]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Slide 1: Bar chart
    console.log('  - Adding bar chart to slide 1...');
    await executeAction('add_chart_and_images', {
      slide_index: 0,
      items: [{
        type: 'chart',
        chartType: 'bar',
        data: [{
          name: 'Sales',
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          values: [100, 150, 135, 180, 200]
        }],
        position: { x: 0.5, y: 1.5, w: 4, h: 3.5 }
      }]
    }, {});

    // Slide 1: Line chart
    console.log('  - Adding line chart to slide 1...');
    await executeAction('add_chart_and_images', {
      slide_index: 0,
      items: [{
        type: 'chart',
        chartType: 'line',
        data: [{
          name: 'Trend',
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          values: [95, 142, 158, 175, 195]
        }],
        position: { x: 5, y: 1.5, w: 4.5, h: 3.5 }
      }]
    }, {});

    // Slide 2: Pie chart
    console.log('  - Adding pie chart to slide 2...');
    await executeAction('add_chart_and_images', {
      slide_index: 1,
      items: [{
        type: 'chart',
        chartType: 'pie',
        data: [{
          name: 'Market Share',
          labels: ['Product A', 'Product B', 'Product C', 'Product D'],
          values: [35, 28, 22, 15]
        }],
        position: { x: 2, y: 1.5, w: 6, h: 4.5 }
      }]
    }, {});

    // Slide 3: Area chart
    console.log('  - Adding area chart to slide 3...');
    const result = await executeAction('add_chart_and_images', {
      slide_index: 2,
      items: [{
        type: 'chart',
        chartType: 'area',
        data: [{
          name: 'Growth',
          labels: ['2020', '2021', '2022', '2023', '2024'],
          values: [50, 75, 110, 165, 240]
        }],
        position: { x: 1, y: 1.5, w: 8, h: 4.5 }
      }]
    }, {});

    console.log('✓ Multiple charts added');

    const outputPath = path.join(outputDir, 'test_multiple_charts.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testImages() {
  console.log('\nTest 3: Add images...');

  const createInputs = {
    title: 'Image Tests',
    slides: [{ markdown: '# Image Placement Test' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    const addInputs = {
      slide_index: 0,
      items: [
        {
          type: 'image',
          data: `data:image/png;base64,${SAMPLE_LOGO}`,
          position: { x: 0.5, y: 0.5, w: 1, h: 1 }
        },
        {
          type: 'image',
          data: `data:image/png;base64,${SAMPLE_IMAGE_BASE64}`,
          position: { x: 8.5, y: 0.5, w: 1, h: 1 }
        },
        {
          type: 'image',
          data: `data:image/png;base64,${SAMPLE_LOGO}`,
          position: { x: 3, y: 2.5, w: 4, h: 3 }
        }
      ]
    };

    const result = await executeAction('add_chart_and_images', addInputs, {});

    console.log('✓ Images added');
    console.log('  - Items added:', result.items_added);

    const outputPath = path.join(outputDir, 'test_images.pptx');
    const buffer = Buffer.from(result.file.content, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log('  - Saved to:', outputPath);

    return result;
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    throw error;
  }
}

async function testDashboardSlide() {
  console.log('\nTest 4: Create dashboard slide (chart + images)...');

  const createInputs = {
    title: 'Dashboard',
    slides: [{ markdown: '# Q4 2024 Dashboard' }]
  };

  try {
    await executeAction('create_presentation', createInputs, {});
    console.log('  ✓ Base presentation created');

    // Add multiple charts and images to create dashboard
    const addInputs = {
      slide_index: 0,
      items: [
        // Logo in corner
        {
          type: 'image',
          data: `data:image/png;base64,${SAMPLE_LOGO}`,
          position: { x: 8.5, y: 0.5, w: 1, h: 0.5 }
        },
        // Main revenue chart
        {
          type: 'chart',
          chartType: 'bar',
          data: [{
            name: 'Revenue',
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            values: [120, 145, 135, 160, 180, 210]
          }],
          position: { x: 0.5, y: 1.5, w: 4.5, h: 2.8 }
        },
        // Customer growth line chart
        {
          type: 'chart',
          chartType: 'line',
          data: [{
            name: 'Customers',
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            values: [1200, 1450, 1680, 2100, 2500, 3100]
          }],
          position: { x: 5.2, y: 1.5, w: 4.3, h: 2.8 }
        },
        // Market share pie chart
        {
          type: 'chart',
          chartType: 'pie',
          data: [{
            name: 'Market Share',
            labels: ['Us', 'Competitor A', 'Competitor B', 'Others'],
            values: [28, 25, 18, 29]
          }],
          position: { x: 0.5, y: 4.5, w: 4.5, h: 2.3 }
        },
        // Trend area chart
        {
          type: 'chart',
          chartType: 'area',
          data: [{
            name: 'Profit Margin',
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            values: [18, 19, 21, 22, 24, 26]
          }],
          position: { x: 5.2, y: 4.5, w: 4.3, h: 2.3 }
        }
      ]
    };

    const result = await executeAction('add_chart_and_images', addInputs, {});

    console.log('✓ Dashboard slide created');
    console.log('  - Items added:', result.items_added);
    console.log('  - Contains: 4 charts + 1 logo image');

    const outputPath = path.join(outputDir, 'test_dashboard.pptx');
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
  console.log('=== Testing add_chart_and_images Action ===\n');

  try {
    await testBarChart();
    await testMultipleCharts();
    await testImages();
    await testDashboardSlide();

    console.log('\n=== All add_chart_and_images tests passed! ===');
    console.log('💡 Chart types tested:');
    console.log('   - Bar charts');
    console.log('   - Line charts');
    console.log('   - Pie charts');
    console.log('   - Area charts');
    console.log('   - Image placement');
    console.log('   - Combined dashboard layouts');
  } catch (error) {
    console.error('\n=== Tests failed ===');
    process.exit(1);
  }
}

if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests };
