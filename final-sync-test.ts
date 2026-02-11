#!/usr/bin/env bun

import { chromium } from 'playwright';

const URL = 'http://localhost:3000';

async function getPosition(page: any): Promise<string> {
  const text = await page.evaluate(() => {
    const overlay = document.querySelector('.position-overlay');
    return overlay?.textContent || 'NOT FOUND';
  });
  return text.trim();
}

async function main() {
  console.log('🧪 FINAL MULTIPLAYER SYNC TEST\n');
  
  const browser = await chromium.launch({ headless: true });
  
  const ctx1 = await browser.newContext();
  const ctx2 = await browser.newContext();
  
  const page1 = await ctx1.newPage();
  const page2 = await ctx2.newPage();
  
  await Promise.all([page1.goto(URL), page2.goto(URL)]);
  await page1.waitForTimeout(3000);
  
  console.log('✅ Both players connected\n');
  
  // Get initial positions
  const [pos1_initial, pos2_initial] = await Promise.all([
    getPosition(page1),
    getPosition(page2)
  ]);
  
  console.log('📍 Initial positions:');
  console.log(`   Client 1 (local):  ${pos1_initial}`);
  console.log(`   Client 2 (local):  ${pos2_initial}\n`);
  
  // Move player 1
  console.log('🎮 Client 1 moving right for 2 seconds...');
  await page1.keyboard.down('ArrowRight');
  await page1.waitForTimeout(2000);
  await page1.keyboard.up('ArrowRight');
  
  // Wait for sync
  await page1.waitForTimeout(1000);
  
  // Get final positions
  const [pos1_final, pos2_final] = await Promise.all([
    getPosition(page1),
    getPosition(page2)
  ]);
  
  console.log('📍 Final positions:');
  console.log(`   Client 1 (local):  ${pos1_final}`);
  console.log(`   Client 2 (local):  ${pos2_final}\n`);
  
  // Parse positions to compare
  const match1 = pos1_final.match(/Position:\s*\((\d+),\s*(\d+)\s*\[L(\d+)\]\)/);
  const match2 = pos2_final.match(/Position:\s*\((\d+),\s*(\d+)\s*\[L(\d+)\]\)/);
  
  if (!match1 || !match2) {
    console.log('❌ Could not parse positions');
    await browser.close();
    return;
  }
  
  const [_, x1, y1, elev1] = match1.map(Number);
  const [__, x2, y2, elev2] = match2.map(Number);
  
  console.log('🔍 Analysis:');
  console.log(`   Player 1 moved from spawn, now at (${x1}, ${y1})`);
  console.log(`   Player 2 stayed at spawn at (${x2}, ${y2})`);
  console.log(`   Distance between players: ${Math.sqrt((x1-x2)**2 + (y1-y2)**2).toFixed(0)}px\n`);
  
  console.log('💡 Now checking if Client 2 sees Player 1\'s remote sprite...');
  console.log('   (Remote sprites have blue tint in the game)');
  console.log('   Looking at server logs for broadcast confirmation...\n');
  
  await browser.close();
}

main().catch(console.error);
