#!/usr/bin/env bun
// Check browser console for errors and take screenshot
// Usage: bun check-browser-console.js <url> [output-screenshot-path]

import puppeteer from 'puppeteer';

const url = process.argv[2];
const screenshotPath = process.argv[3] || '/home/workspace/browser-screenshot.png';

if (!url) {
  console.error('Usage: bun check-browser-console.js <url> [screenshot-path]');
  process.exit(1);
}

console.log('🔍 Checking browser console for:', url);

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

const page = await browser.newPage();

const errors = [];
const warnings = [];

page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
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

page.on('pageerror', error => {
  console.log('  💥 [PAGE ERROR]', error.message);
  errors.push(`Page error: ${error.message}`);
});

try {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });
  await new Promise(resolve => setTimeout(resolve, 3000));

  await page.screenshot({ path: screenshotPath });
  console.log(`\n📸 Screenshot: ${screenshotPath}`);

  console.log('\n📋 Summary:');
  console.log('  Errors:', errors.length);
  console.log('  Warnings:', warnings.length);

  if (errors.length === 0) {
    console.log('\n✅ NO ERRORS!');
  } else {
    console.log('\n❌ ERRORS:');
    errors.forEach(e => console.log('  -', e));
  }

  process.exit(errors.length > 0 ? 1 : 0);

} catch (e) {
  console.error('❌ Failed:', e.message);
  process.exit(1);
}

await browser.close();
