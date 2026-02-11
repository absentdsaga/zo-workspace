#!/usr/bin/env bun
import puppeteer from 'puppeteer';

const GAME_URL = 'https://spatial-worlds-dioni.zocomputer.io/';

async function main() {
  console.log('🧪 QA: Multiplayer Position Sync Test\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });

  try {
    console.log('📱 Opening Player 1...');
    const page1 = await browser.newPage();
    await page1.setViewport({ width: 1280, height: 720 });
    await page1.goto(GAME_URL, { waitUntil: 'networkidle2' });

    console.log('📱 Opening Player 2...');
    const page2 = await browser.newPage();
    await page2.setViewport({ width: 1280, height: 720 });
    await page2.goto(GAME_URL, { waitUntil: 'networkidle2' });

    console.log('⏳ Waiting for game initialization (5s)...\n');
    await new Promise(r => setTimeout(r, 5000));

    // Check for console errors
    console.log('📋 Checking for JavaScript errors...');
    const errors1: string[] = [];
    const errors2: string[] = [];

    page1.on('console', msg => {
      if (msg.type() === 'error') errors1.push(msg.text());
    });
    page2.on('console', msg => {
      if (msg.type() === 'error') errors2.push(msg.text());
    });

    // Move Player 1 to the right
    console.log('🎮 Player 1: Moving right for 3 seconds...');
    await page1.keyboard.down('ArrowRight');
    await new Promise(r => setTimeout(r, 3000));
    await page1.keyboard.up('ArrowRight');

    console.log('⏸️  Waiting for position to stabilize (1s)...\n');
    await new Promise(r => setTimeout(r, 1000));

    // Get Player 1's position from their own view
    const p1Position = await page1.evaluate(() => {
      const player = (window as any).game?.scene?.scenes[0]?.player;
      if (!player) return null;
      return { x: Math.round(player.x), y: Math.round(player.y) };
    });

    // Get Player 1's position from Player 2's view (remote player)
    const p1PositionFromP2 = await page2.evaluate(() => {
      const scene = (window as any).game?.scene?.scenes[0];
      if (!scene?.multiplayerManager) return null;

      const remotePlayers = scene.multiplayerManager.getRemotePlayers();
      if (remotePlayers.length === 0) return null;

      const remotePlayer = remotePlayers[0].sprite;
      return { x: Math.round(remotePlayer.x), y: Math.round(remotePlayer.y) };
    });

    // Capture screenshots
    console.log('📸 Capturing screenshots...');
    await page1.screenshot({ path: '/home/workspace/p1-view.png' });
    await page2.screenshot({ path: '/home/workspace/p2-view.png' });

    // Results
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST RESULTS');
    console.log('='.repeat(60) + '\n');

    console.log('Player 1 Position (from P1 view):', p1Position);
    console.log('Player 1 Position (from P2 view):', p1PositionFromP2);
    console.log('');

    if (!p1Position) {
      console.log('❌ FAILED: Could not get Player 1 position from P1 view');
      console.log('   - Game may not have loaded properly');
      console.log('   - Check screenshots: p1-view.png, p2-view.png\n');
      return;
    }

    if (!p1PositionFromP2) {
      console.log('❌ FAILED: Could not get Player 1 position from P2 view');
      console.log('   - Multiplayer connection may have failed');
      console.log('   - Player 2 may not see Player 1');
      console.log('   - Check screenshots: p1-view.png, p2-view.png\n');
      return;
    }

    // Check if positions match (allow 5px tolerance due to lerp)
    const dx = Math.abs(p1Position.x - p1PositionFromP2.x);
    const dy = Math.abs(p1Position.y - p1PositionFromP2.y);
    const tolerance = 10; // 10px tolerance

    if (dx <= tolerance && dy <= tolerance) {
      console.log('✅ PASSED: Positions are synchronized!');
      console.log(`   Position difference: (${dx}px, ${dy}px) - within tolerance (${tolerance}px)`);
      console.log('   Remote players see accurate positions ✨\n');
    } else {
      console.log('❌ FAILED: Positions are NOT synchronized');
      console.log(`   Position difference: (${dx}px, ${dy}px) - exceeds tolerance (${tolerance}px)`);
      console.log('   There is still a desync issue 🐛\n');
    }

    // Check for errors
    if (errors1.length > 0) {
      console.log('⚠️  Player 1 Console Errors:');
      errors1.forEach(e => console.log('   -', e));
      console.log('');
    }

    if (errors2.length > 0) {
      console.log('⚠️  Player 2 Console Errors:');
      errors2.forEach(e => console.log('   -', e));
      console.log('');
    }

    console.log('Screenshots saved:');
    console.log('  - /home/workspace/p1-view.png (Player 1 perspective)');
    console.log('  - /home/workspace/p2-view.png (Player 2 perspective)\n');

  } finally {
    await browser.close();
  }
}

main().catch(console.error);
