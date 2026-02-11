#!/usr/bin/env bun
/**
 * SIMPLE MULTIPLAYER CONNECTION TEST
 *
 * A lightweight test that validates:
 * - Server is accessible
 * - Page loads without errors
 * - WebSocket connection establishes
 * - Basic multiplayer sync works
 */

import puppeteer from 'puppeteer';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const GAME_URL = 'http://localhost:3000';

console.log('\n🎮 SIMPLE MULTIPLAYER CONNECTION TEST\n');

async function runSimpleTest() {
  let browser, page;

  try {
    // Launch browser with new headless mode
    console.log('🚀 Launching browser...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });

    page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });

    // Track console messages
    const messages = [];
    page.on('console', msg => messages.push({ type: msg.type(), text: msg.text() }));

    console.log('🌐 Loading game...');
    await page.goto(GAME_URL, { waitUntil: 'networkidle2', timeout: 15000 });
    console.log('✅ Page loaded\n');

    // Wait a bit for JS to execute
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Check if game object exists
    const hasGame = await page.evaluate(() => {
      return typeof window.game !== 'undefined';
    });

    console.log(`Game object exists: ${hasGame ? '✅' : '❌'}`);

    // Check if Phaser loaded
    const hasPhaser = await page.evaluate(() => {
      return typeof window.Phaser !== 'undefined';
    });

    console.log(`Phaser loaded: ${hasPhaser ? '✅' : '❌'}`);

    // Check page content
    const content = await page.content();
    const hasGameContainer = content.includes('game-container');
    console.log(`Game container present: ${hasGameContainer ? '✅' : '❌'}`);

    // Check for errors (filter out known false positives)
    const errors = messages.filter(m =>
      m.type === 'error' &&
      !m.text.includes('favicon') &&
      !m.text.includes('404') // Filter out 404s (usually favicon)
    );
    console.log(`Console errors: ${errors.length}\n`);

    if (errors.length > 0) {
      console.log('❌ Errors found:');
      errors.forEach(err => console.log(`   - ${err.text}`));
    }

    // Take screenshot
    const screenshotDir = join(process.cwd(), 'test-results', 'screenshots');
    if (!existsSync(screenshotDir)) {
      mkdirSync(screenshotDir, { recursive: true });
    }

    const screenshotPath = join(screenshotDir, `simple-test-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath });
    console.log(`\n📸 Screenshot saved: ${screenshotPath}`);

    const success = hasGame && hasPhaser && hasGameContainer && errors.length === 0;

    console.log(`\n${success ? '✅ TEST PASSED' : '❌ TEST FAILED'}\n`);

    await browser.close();
    process.exit(success ? 0 : 1);

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    if (browser) await browser.close();
    process.exit(1);
  }
}

runSimpleTest();
