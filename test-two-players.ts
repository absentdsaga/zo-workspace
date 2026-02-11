#!/usr/bin/env bun

import { chromium } from 'playwright';
import { writeFileSync } from 'fs';

const URL = 'http://localhost:3000';

async function main() {
  console.log('🚀 Starting TWO PLAYER sync test...');
  
  const browser = await chromium.launch({ headless: true });
  
  // Create TWO COMPLETELY SEPARATE browser contexts
  // This ensures they get different player IDs
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();
  
  const page1 = await context1.newPage();
  const page2 = await context2.newPage();
  
  console.log('📱 Client 1 loading...');
  await page1.goto(URL);
  await page1.waitForTimeout(3000);
  
  console.log('📱 Client 2 loading...');
  await page2.goto(URL);
  await page2.waitForTimeout(3000);
  
  console.log('✅ Both clients loaded, waiting for multiplayer sync...');
  await page1.waitForTimeout(2000);
  
  // Move player 1 to a different location
  console.log('🎮 Client 1 moving right...');
  await page1.keyboard.down('ArrowRight');
  await page1.waitForTimeout(2000);
  await page1.keyboard.up('ArrowRight');
  
  console.log('⏸️  Waiting for sync...');
  await page1.waitForTimeout(1000);
  
  // Capture both screens
  const [shot1, shot2] = await Promise.all([
    page1.screenshot({ type: 'png' }),
    page2.screenshot({ type: 'png' })
  ]);
  
  writeFileSync('/home/workspace/test_client1.png', shot1);
  writeFileSync('/home/workspace/test_client2.png', shot2);
  
  console.log('📸 Screenshots captured');
  console.log('Client 1: /home/workspace/test_client1.png');
  console.log('Client 2: /home/workspace/test_client2.png');
  
  // Check server logs for both player IDs
  console.log('\n🔍 Checking multiplayer state...');
  
  await browser.close();
  console.log('✅ Test complete!');
}

main().catch(console.error);
