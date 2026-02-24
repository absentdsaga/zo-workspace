import puppeteer from 'puppeteer-core';
import { mkdir } from 'fs/promises';

const SLIDES = 15;
const OUTPUT = '/home/workspace/sagadao-deck-export/slides';

await mkdir(OUTPUT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: '/usr/bin/chromium',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  headless: true,
});

const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
await page.goto('http://localhost:52080', { waitUntil: 'networkidle0', timeout: 30000 });

await page.waitForSelector('#slide-0', { timeout: 10000 });
await new Promise(r => setTimeout(r, 2000));

for (let i = 0; i < SLIDES; i++) {
  await page.evaluate((idx) => {
    document.getElementById(`slide-${idx}`)?.scrollIntoView({ behavior: 'instant' });
  }, i);
  await new Promise(r => setTimeout(r, 800));

  const padded = String(i + 1).padStart(2, '0');
  await page.screenshot({
    path: `${OUTPUT}/slide-${padded}.png`,
    type: 'png',
  });
  console.log(`Captured slide ${i + 1}/${SLIDES}`);
}

await browser.close();
console.log(`\nDone! ${SLIDES} slides saved to ${OUTPUT}`);
