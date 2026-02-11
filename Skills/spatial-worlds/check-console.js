// Check browser console for errors
import puppeteer from 'puppeteer';

const url = 'https://spatial-worlds-dioni.zocomputer.io';

console.log('🔍 Checking browser console for:', url);
console.log('');

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

const page = await browser.newPage();

const logs = [];
const errors = [];
const warnings = [];

// Capture console messages
page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();

  logs.push({ type, text });

  if (type === 'log') console.log('  [LOG]', text);
  if (type === 'error') {
    console.log('  ❌ [ERROR]', text);
    errors.push(text);
  }
  if (type === 'warning') {
    console.log('  ⚠️  [WARN]', text);
    warnings.push(text);
  }
});

// Capture page errors
page.on('pageerror', error => {
  console.log('  💥 [PAGE ERROR]', error.message);
  errors.push(`Page error: ${error.message}`);
});

// Capture network failures
page.on('requestfailed', request => {
  console.log('  🌐 [NETWORK FAIL]', request.url(), request.failure().errorText);
});

try {
  console.log('📡 Loading page...\n');

  await page.goto(url, {
    waitUntil: 'networkidle2',
    timeout: 15000
  });

  // Wait for game to initialize
  await page.waitForTimeout(3000);

  // Get canvas element info
  const canvasInfo = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return null;

    return {
      width: canvas.width,
      height: canvas.height,
      exists: true
    };
  });

  console.log('\n📊 Canvas Info:', canvasInfo);

  // Check for Phaser
  const phaserInfo = await page.evaluate(() => {
    if (typeof Phaser === 'undefined') return { exists: false };

    return {
      exists: true,
      version: Phaser.VERSION
    };
  });

  console.log('🎮 Phaser:', phaserInfo);

  // Take screenshot
  await page.screenshot({ path: '/home/workspace/browser-screenshot.png' });
  console.log('\n📸 Screenshot saved to /home/workspace/browser-screenshot.png');

  console.log('\n📋 Summary:');
  console.log('  Total logs:', logs.length);
  console.log('  Errors:', errors.length);
  console.log('  Warnings:', warnings.length);

  if (errors.length > 0) {
    console.log('\n❌ ERRORS FOUND:');
    errors.forEach(e => console.log('  -', e));
  }

} catch (e) {
  console.error('❌ Failed to load page:', e.message);
  process.exit(1);
}

await browser.close();
