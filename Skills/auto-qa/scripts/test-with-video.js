#!/usr/bin/env node
import puppeteer from 'puppeteer';
import { spawn } from 'child_process';
import { join } from 'path';

const GAME_URL = 'http://localhost:3000';
const VIDEO_DIR = join(process.cwd(), 'test-results', 'videos');
const VIDEO_FILE = join(VIDEO_DIR, `gameplay-${Date.now()}.webm`);

// Create video directory
import { mkdirSync } from 'fs';
mkdirSync(VIDEO_DIR, { recursive: true });

async function recordGameplay() {
  console.log('🎥 GAMEPLAY VIDEO RECORDING TEST\n');
  console.log('================================================');

  const browser = await puppeteer.launch({
    headless: false, // Run with GUI so we can see it
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1280,720',
      '--display=:99', // Virtual display
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  // Capture console logs
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  page.on('pageerror', err => console.error('PAGE ERROR:', err.message));

  console.log('🌐 Loading game...');
  await page.goto(GAME_URL, { waitUntil: 'networkidle0' });

  console.log('⏳ Waiting for game to initialize...');

  // Check what's available
  const gameCheck = await page.evaluate(() => {
    return {
      hasWindow: typeof window !== 'undefined',
      hasGame: typeof window.game !== 'undefined',
      hasScene: window.game?.scene !== undefined,
      sceneCount: window.game?.scene?.scenes?.length || 0,
      scenes: window.game?.scene?.scenes?.map(s => s.constructor.name) || []
    };
  });
  console.log('Game check:', JSON.stringify(gameCheck, null, 2));

  await page.waitForFunction(
    () => {
      const scene = window.game?.scene?.getScene('IsoGameScene');
      return scene && scene.player && scene.multiplayerManager;
    },
    { timeout: 30000 }
  );

  console.log('✅ Game ready! Starting 30-second recording...\n');

  // Start ffmpeg screen recording
  const ffmpeg = spawn('ffmpeg', [
    '-y',
    '-f', 'x11grab',
    '-video_size', '1280x720',
    '-i', ':99',
    '-t', '30',
    '-c:v', 'libvpx',
    '-quality', 'realtime',
    '-cpu-used', '5',
    '-b:v', '1M',
    VIDEO_FILE
  ]);

  ffmpeg.stderr.on('data', (data) => {
    // Suppress ffmpeg noise
  });

  // Simulate gameplay for 30 seconds
  console.log('🎮 Testing gameplay:');
  console.log('   - Moving in all directions');
  console.log('   - Testing elevation changes');
  console.log('   - Walking to corners of map\n');

  await page.evaluate(() => {
    console.log('🎮 Starting automated gameplay...');
  });

  // Move right for 3 seconds
  console.log('➡️  Moving right...');
  await page.keyboard.down('d');
  await new Promise(r => setTimeout(r, 3000));
  await page.keyboard.up('d');

  // Move to elevated platform (northeast corner)
  console.log('🏔️  Moving to elevated platform (northeast)...');
  await page.keyboard.down('w');
  await page.keyboard.down('d');
  await new Promise(r => setTimeout(r, 4000));
  await page.keyboard.up('w');
  await page.keyboard.up('d');

  // Wait and check elevation
  await new Promise(r => setTimeout(r, 1000));
  const state1 = await page.evaluate(() => {
    const scene = window.game.scene.getScene('IsoGameScene');
    const isoData = scene.player.getData('iso');
    return {
      x: Math.round(scene.player.x),
      y: Math.round(scene.player.y),
      elevation: isoData?.elevation || 0
    };
  });
  console.log(`   Position: (${state1.x}, ${state1.y}) Elevation: ${state1.elevation}`);

  // Try manual elevation change
  console.log('⬆️  Pressing E to increase elevation...');
  await page.keyboard.press('e');
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.press('e');
  await new Promise(r => setTimeout(r, 500));

  const state2 = await page.evaluate(() => {
    const scene = window.game.scene.getScene('IsoGameScene');
    const isoData = scene.player.getData('iso');
    return {
      elevation: isoData?.elevation || 0
    };
  });
  console.log(`   New elevation: ${state2.elevation}`);

  // Move around more
  console.log('🔄 Moving around map...');
  await page.keyboard.down('s');
  await new Promise(r => setTimeout(r, 3000));
  await page.keyboard.up('s');

  await page.keyboard.down('a');
  await new Promise(r => setTimeout(r, 3000));
  await page.keyboard.up('a');

  // Circle back
  await page.keyboard.down('w');
  await new Promise(r => setTimeout(r, 2000));
  await page.keyboard.up('w');

  // Get final console logs
  const consoleLogs = [];
  page.on('console', msg => {
    if (msg.text().includes('🗺️') || msg.text().includes('🏔️')) {
      consoleLogs.push(msg.text());
    }
  });

  await new Promise(r => setTimeout(r, 5000));

  console.log('\n📊 Console logs captured:');
  consoleLogs.slice(-10).forEach(log => console.log('   ' + log));

  // Wait for ffmpeg to finish
  await new Promise(resolve => {
    ffmpeg.on('close', resolve);
  });

  console.log(`\n✅ Video saved: ${VIDEO_FILE}`);
  console.log('   Duration: 30 seconds');
  console.log('   Resolution: 1280x720');

  await browser.close();
}

recordGameplay().catch(console.error);
