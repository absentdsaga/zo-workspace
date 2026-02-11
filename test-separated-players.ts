#!/usr/bin/env bun

import { chromium } from 'playwright';
import { writeFileSync } from 'fs';

const URL = 'http://localhost:3000';

async function main() {
  console.log('🚀 Starting SEPARATED PLAYERS test...');
  
  const browser = await chromium.launch({ headless: true });
  
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();
  
  const page1 = await context1.newPage();
  const page2 = await context2.newPage();
  
  console.log('📱 Loading clients...');
  await Promise.all([
    page1.goto(URL),
    page2.goto(URL)
  ]);
  await page1.waitForTimeout(3000);
  
  console.log('🎮 Moving Player 1 FAR to the right...');
  await page1.keyboard.down('ArrowRight');
  await page1.waitForTimeout(3000); // Move for 3 seconds
  await page1.keyboard.up('ArrowRight');
  
  console.log('🎮 Moving Player 2 FAR to the left...');
  await page2.keyboard.down('ArrowLeft');
  await page2.waitForTimeout(3000);
  await page2.keyboard.up('ArrowLeft');
  
  console.log('⏸️  Waiting for final sync...');
  await page1.waitForTimeout(1500);
  
  // Capture final positions
  const [shot1, shot2] = await Promise.all([
    page1.screenshot({ type: 'png' }),
    page2.screenshot({ type: 'png' })
  ]);
  
  writeFileSync('/home/workspace/test_separated.png', shot1);
  writeFileSync('/home/workspace/test_separated2.png', shot2);
  
  console.log('✅ Screenshots saved - players should be far apart now');
  
  await browser.close();
}

main().catch(console.error);
