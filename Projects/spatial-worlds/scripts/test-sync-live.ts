#!/usr/bin/env bun

import { chromium, type Browser, type Page } from 'playwright';
import { writeFileSync } from 'fs';

const URL = 'http://localhost:3000';

async function captureFrame(page: Page, label: string): Promise<Buffer> {
  return await page.screenshot({ type: 'png' });
}

async function extractPosition(page: Page): Promise<{ x: number; y: number; elevation: number } | null> {
  const text = await page.evaluate(() => {
    const overlay = document.querySelector('.position-overlay');
    return overlay?.textContent || '';
  });
  
  const match = text.match(/Position:\s*\((\d+),\s*(\d+)\s*\[L(\d+)\]\)/);
  if (!match) return null;
  
  return {
    x: parseInt(match[1]),
    y: parseInt(match[2]),
    elevation: parseInt(match[3])
  };
}

async function main() {
  console.log('🚀 Starting live multiplayer sync test...');
  
  const browser = await chromium.launch({ headless: true });
  
  // Open two browser contexts (separate sessions)
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();
  
  const page1 = await context1.newPage();
  const page2 = await context2.newPage();
  
  console.log('📱 Opening client 1...');
  await page1.goto(URL);
  await page1.waitForTimeout(2000); // Wait for game to load
  
  console.log('📱 Opening client 2...');
  await page2.goto(URL);
  await page2.waitForTimeout(2000);
  
  console.log('✅ Both clients loaded');
  
  // Move player 1 to different positions and capture both views
  const movements = [
    { key: 'ArrowRight', duration: 1000, label: 'right' },
    { key: 'ArrowDown', duration: 1000, label: 'down' },
    { key: 'ArrowLeft', duration: 1000, label: 'left' },
    { key: 'ArrowUp', duration: 1000, label: 'up' },
  ];
  
  for (const movement of movements) {
    console.log(`\n🎮 Moving ${movement.label}...`);
    
    // Start moving
    await page1.keyboard.down(movement.key);
    
    // Capture frames while moving
    for (let i = 0; i < 5; i++) {
      await page1.waitForTimeout(200);
      
      const [frame1, frame2, pos1, pos2] = await Promise.all([
        captureFrame(page1, 'client1'),
        captureFrame(page2, 'client2'),
        extractPosition(page1),
        extractPosition(page2)
      ]);
      
      const timestamp = Date.now();
      writeFileSync(`/home/workspace/client1_${movement.label}_${i}.png`, frame1);
      writeFileSync(`/home/workspace/client2_${movement.label}_${i}.png`, frame2);
      
      console.log(`  Frame ${i}:`);
      console.log(`    Client 1 position: ${JSON.stringify(pos1)}`);
      console.log(`    Client 2 position: ${JSON.stringify(pos2)}`);
      
      if (pos1 && pos2) {
        const dx = Math.abs(pos1.x - pos2.x);
        const dy = Math.abs(pos1.y - pos2.y);
        console.log(`    Offset: dx=${dx}px, dy=${dy}px`);
      }
    }
    
    // Stop moving
    await page1.keyboard.up(movement.key);
    await page1.waitForTimeout(500);
  }
  
  console.log('\n✅ Test complete! Check the PNG files for visual comparison.');
  
  await browser.close();
}

main().catch(console.error);
