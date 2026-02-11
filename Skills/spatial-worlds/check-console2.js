// Check browser console for errors
import puppeteer from 'puppeteer';

const url = 'https://spatial-worlds-dioni.zocomputer.io';

console.log('🔍 Checking browser console for:', url);

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

const page = await browser.newPage();

const errors = [];

page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  if (type === 'log') console.log('  [LOG]', text);
  if (type === 'error') {
    console.log('  ❌ [ERROR]', text);
    errors.push(text);
  }
});

page.on('pageerror', error => {
  console.log('  💥 [PAGE ERROR]', error.message);
  errors.push(`Page error: ${error.message}`);
});

try {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });

  // Wait a bit for game to initialize
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Take screenshot
  await page.screenshot({ path: '/home/workspace/browser-screenshot.png' });
  console.log('\n📸 Screenshot saved to /home/workspace/browser-screenshot.png');

  console.log('\n📋 Summary:');
  console.log('  Errors:', errors.length);

  if (errors.length === 0) {
    console.log('\n✅ NO ERRORS! Game should be working.');
  } else {
    console.log('\n❌ ERRORS FOUND:');
    errors.forEach(e => console.log('  -', e));
  }

} catch (e) {
  console.error('❌ Failed:', e.message);
  process.exit(1);
}

await browser.close();
