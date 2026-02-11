#!/usr/bin/env bun
import puppeteer from 'puppeteer';

/**
 * Test multiplayer position synchronization
 * Opens 2 browser windows, moves one player, captures screenshots
 */

async function testMultiplayerSync() {
  console.log('🧪 Starting multiplayer sync test...\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const [page1, page2] = await Promise.all([
    browser.newPage(),
    browser.newPage(),
  ]);

  // Set viewport size
  await Promise.all([
    page1.setViewport({ width: 1280, height: 720 }),
    page2.setViewport({ width: 1280, height: 720 }),
  ]);

  console.log('🌐 Loading game in both windows...');
  const url = 'https://spatial-worlds-dioni.zocomputer.io';
  await Promise.all([
    page1.goto(url, { waitUntil: 'networkidle2' }),
    page2.goto(url, { waitUntil: 'networkidle2' }),
  ]);

  // Wait for game to load
  await new Promise(r => setTimeout(r, 5000));
  console.log('✅ Both players loaded\n');

  // Take initial screenshot
  await Promise.all([
    page1.screenshot({ path: '/tmp/mp-player1-start.png' }),
    page2.screenshot({ path: '/tmp/mp-player2-start.png' }),
  ]);
  console.log('📸 Initial screenshots saved');

  // Get initial positions from both clients
  const getPosition = async (page: any, playerNum: number) => {
    const pos = await page.evaluate(() => {
      const debugText = document.querySelector('canvas')?.nextElementSibling?.textContent;
      const match = debugText?.match(/Position: (\d+), (\d+)/);
      if (match) {
        return { x: parseInt(match[1]), y: parseInt(match[2]) };
      }
      return null;
    });
    console.log(`📍 Player ${playerNum} position:`, pos);
    return pos;
  };

  console.log('\n🎮 Testing movement sync...\n');

  // Move player 1 right for 3 seconds
  console.log('➡️  Player 1 moving right...');
  await page1.keyboard.down('ArrowRight');
  await new Promise(r => setTimeout(r, 3000));
  await page1.keyboard.up('ArrowRight');

  // Wait for sync
  await new Promise(r => setTimeout(r, 500));

  // Capture positions from both views
  await Promise.all([
    page1.screenshot({ path: '/tmp/mp-player1-moved.png' }),
    page2.screenshot({ path: '/tmp/mp-player2-moved.png' }),
  ]);

  const pos1 = await getPosition(page1, 1);
  const pos2 = await getPosition(page2, 2);

  console.log('\n📊 Sync Test Results:');
  console.log('Player 1 sees themselves at:', pos1);
  console.log('Player 2 sees Player 1 at:', pos2);

  if (pos1 && pos2) {
    const dx = Math.abs(pos1.x - pos2.x);
    const dy = Math.abs(pos1.y - pos2.y);
    const distance = Math.sqrt(dx * dx + dy * dy);

    console.log(`\n❗ Position desync: ${Math.round(distance)}px`);

    if (distance < 50) {
      console.log('✅ PASS: Players synced within 50px tolerance');
    } else {
      console.log('❌ FAIL: Players desynced by more than 50px');
    }
  }

  console.log('\n📸 Screenshots saved to /tmp/mp-*.png');
  console.log('🔍 Check server logs in /dev/shm/spatial-worlds.log\n');

  await new Promise(r => setTimeout(r, 2000));
  await browser.close();
}

testMultiplayerSync().catch(console.error);
