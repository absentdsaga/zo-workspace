#!/bin/bash
# Check browser console for JavaScript errors
# Usage: ./check-browser-console.sh <url>

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url>"
  exit 1
fi

echo "🔍 Checking browser console for: $URL"
echo ""

# Use playwright or puppeteer to check console
bun -e "
import puppeteer from 'puppeteer';

const url = '$URL';
const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();

const errors = [];
const warnings = [];

page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  if (type === 'error') errors.push(text);
  if (type === 'warning') warnings.push(text);
});

page.on('pageerror', error => {
  errors.push(\`Uncaught error: \${error.message}\`);
});

try {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 10000 });
  await page.waitForTimeout(2000);

  console.log('\\n📋 Console Output:\\n');
  if (errors.length > 0) {
    console.log('❌ ERRORS:');
    errors.forEach(e => console.log('  ', e));
  }
  if (warnings.length > 0) {
    console.log('\\n⚠️  WARNINGS:');
    warnings.forEach(w => console.log('  ', w));
  }
  if (errors.length === 0 && warnings.length === 0) {
    console.log('✅ No console errors or warnings!');
  }
} catch (e) {
  console.error('Failed to load page:', e.message);
  process.exit(1);
}

await browser.close();
"
