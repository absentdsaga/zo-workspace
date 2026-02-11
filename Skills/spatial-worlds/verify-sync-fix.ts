#!/usr/bin/env bun
import puppeteer from 'puppeteer';

const GAME_URL = 'https://spatial-worlds-dioni.zocomputer.io/iso.html';
const WARMUP_TIME = 3000; // Wait for game to load
const TEST_DURATION = 5000; // 5 seconds of movement
const SCREENSHOT_INTERVAL = 1000; // Screenshot every 1 second

async function main() {
  console.log('🧪 Testing Multiplayer Position Sync Fix');
  console.log('=========================================\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    ],
  });

  try {
    // Open two browser windows (Player 1 and Player 2)
    console.log('📱 Opening Player 1...');
    const page1 = await browser.newPage();
    await page1.setViewport({ width: 1280, height: 720 });
    await page1.goto(GAME_URL, { waitUntil: 'networkidle2' });

    console.log('📱 Opening Player 2...');
    const page2 = await browser.newPage();
    await page2.setViewport({ width: 1280, height: 720 });
    await page2.goto(GAME_URL, { waitUntil: 'networkidle2' });

    console.log(`⏳ Waiting ${WARMUP_TIME}ms for game to initialize...\n`);
    await new Promise(resolve => setTimeout(resolve, WARMUP_TIME));

    // Start movement on Player 1 (hold right arrow)
    console.log('🎮 Player 1: Moving right →');
    await page1.keyboard.down('ArrowRight');

    // Capture screenshots at intervals
    const screenshots = [];
    for (let i = 0; i < TEST_DURATION / SCREENSHOT_INTERVAL; i++) {
      await new Promise(resolve => setTimeout(resolve, SCREENSHOT_INTERVAL));

      console.log(`📸 Capturing screenshot ${i + 1}...`);
      const [shot1, shot2] = await Promise.all([
        page1.screenshot({ path: `/home/workspace/sync-test-p1-${i}.png` }),
        page2.screenshot({ path: `/home/workspace/sync-test-p2-${i}.png` }),
      ]);

      screenshots.push({ p1: `/home/workspace/sync-test-p1-${i}.png`, p2: `/home/workspace/sync-test-p2-${i}.png` });
    }

    // Stop movement
    await page1.keyboard.up('ArrowRight');

    console.log('\n✅ Test Complete!');
    console.log('==================\n');
    console.log('Screenshots saved:');
    screenshots.forEach((s, i) => {
      console.log(`  ${i + 1}. Player 1: ${s.p1}`);
      console.log(`     Player 2: ${s.p2}`);
    });

    console.log('\n📊 Analysis:');
    console.log('  - Check if Player 1\'s sprite appears in the SAME position in both screenshots');
    console.log('  - Player 2 should see Player 1 moving right smoothly');
    console.log('  - If positions match = ✅ SYNC WORKING');
    console.log('  - If positions differ = ❌ STILL DESYNCED\n');

  } finally {
    await browser.close();
  }
}

main().catch(console.error);
