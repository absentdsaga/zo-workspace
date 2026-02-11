#!/usr/bin/env bun
/**
 * Verify multiplayer sync by testing with 2 clients
 * This test MUST pass before showing to user
 */

import puppeteer from 'puppeteer';
import { spawn } from 'child_process';
import { writeFileSync } from 'fs';

async function verifyMultiplayerSync() {
  console.log('🧪 MULTIPLAYER SYNC VERIFICATION TEST\n');
  console.log('This test must pass before showing fix to user.\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const [page1, page2] = await Promise.all([
      browser.newPage(),
      browser.newPage(),
    ]);

    await Promise.all([
      page1.setViewport({ width: 1280, height: 720 }),
      page2.setViewport({ width: 1280, height: 720 }),
    ]);

    const url = 'https://spatial-worlds-dioni.zocomputer.io';
    console.log(`🌐 Loading game in 2 windows: ${url}\n`);

    await Promise.all([
      page1.goto(url, { waitUntil: 'networkidle0', timeout: 20000 }),
      page2.goto(url, { waitUntil: 'networkidle0', timeout: 20000 }),
    ]);

    // Wait for game to initialize
    await new Promise(r => setTimeout(r, 6000));
    console.log('✅ Both clients loaded\n');

    // Enable console logging to see multiplayer events
    page1.on('console', msg => {
      const text = msg.text();
      if (text.includes('Remote player') || text.includes('position')) {
        console.log('[P1]', text);
      }
    });

    page2.on('console', msg => {
      const text = msg.text();
      if (text.includes('Remote player') || text.includes('position')) {
        console.log('[P2]', text);
      }
    });

    // Take baseline screenshots
    await Promise.all([
      page1.screenshot({ path: '/tmp/sync-p1-start.png' }),
      page2.screenshot({ path: '/tmp/sync-p2-start.png' }),
    ]);
    console.log('📸 Baseline screenshots saved\n');

    // Test 1: Move Player 1 right for 2 seconds
    console.log('🎮 TEST 1: Moving Player 1 right...');
    await page1.keyboard.down('ArrowRight');
    await new Promise(r => setTimeout(r, 2000));
    await page1.keyboard.up('ArrowRight');
    await new Promise(r => setTimeout(r, 500)); // Wait for network sync

    // Capture positions
    const getPlayerPosition = async (page: any) => {
      return await page.evaluate(() => {
        const canvas = document.querySelector('canvas');
        if (!canvas) return null;

        // Try to get position from debug text
        const debugText = Array.from(document.querySelectorAll('*'))
          .find(el => el.textContent?.includes('Position:'))?.textContent;

        const match = debugText?.match(/Position:\s*(\d+),\s*(\d+)/);
        if (match) {
          return { x: parseInt(match[1]), y: parseInt(match[2]) };
        }
        return null;
      });
    };

    const p1Pos = await getPlayerPosition(page1);
    const p2Pos = await getPlayerPosition(page2);

    await Promise.all([
      page1.screenshot({ path: '/tmp/sync-p1-moved.png' }),
      page2.screenshot({ path: '/tmp/sync-p2-moved.png' }),
    ]);

    console.log('📍 Player 1 sees themselves at:', p1Pos);
    console.log('📍 Player 2 sees them at:', p2Pos);

    let testPassed = false;
    let desynDist = 999;

    if (p1Pos && p2Pos) {
      const dx = Math.abs(p1Pos.x - p2Pos.x);
      const dy = Math.abs(p1Pos.y - p2Pos.y);
      desynDist = Math.sqrt(dx * dx + dy * dy);

      console.log(`\n📊 Position desync: ${Math.round(desynDist)}px`);
      console.log(`   ΔX: ${dx}px, ΔY: ${dy}px\n`);

      if (desynDist < 50) {
        console.log('✅ TEST PASSED: Positions synced within 50px tolerance');
        testPassed = true;
      } else {
        console.log('❌ TEST FAILED: Positions desynced by >50px');
        console.log('   This indicates multiplayer sync is broken.\n');
      }
    } else {
      console.log('❌ TEST FAILED: Could not read player positions from UI');
    }

    // Save test report
    const report = {
      timestamp: new Date().toISOString(),
      testPassed,
      desyncDistance: Math.round(desynDist),
      player1Position: p1Pos,
      player2Position: p2Pos,
      screenshots: [
        '/tmp/sync-p1-start.png',
        '/tmp/sync-p2-start.png',
        '/tmp/sync-p1-moved.png',
        '/tmp/sync-p2-moved.png',
      ],
    };

    writeFileSync('/tmp/multiplayer-sync-report.json', JSON.stringify(report, null, 2));
    console.log('📄 Test report saved to /tmp/multiplayer-sync-report.json\n');

    await browser.close();

    if (!testPassed) {
      console.log('⛔ DO NOT SHOW TO USER - Multiplayer sync still broken!\n');
      process.exit(1);
    }

    console.log('🎉 Multiplayer sync verified! Safe to show to user.\n');
    return report;

  } catch (error) {
    console.error('❌ Test error:', error);
    await browser.close();
    process.exit(1);
  }
}

verifyMultiplayerSync().catch(console.error);
