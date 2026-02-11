#!/usr/bin/env node
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 720 });

console.log('Loading http://localhost:3000...');
await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });

// Wait for game to load
await new Promise(resolve => setTimeout(resolve, 3000));

const screenshotPath = '/tmp/spatial-worlds-screenshot.png';
await page.screenshot({ path: screenshotPath });

console.log(`✅ Screenshot saved to ${screenshotPath}`);

await browser.close();
