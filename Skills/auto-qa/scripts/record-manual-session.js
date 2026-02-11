#!/usr/bin/env node
/**
 * Opens a browser for manual testing while recording the session
 * This avoids the WebGL limitations of Xvfb
 */
import puppeteer from 'puppeteer';
import { spawn } from 'child_process';
import { join } from 'path';
import { mkdirSync } from 'fs';

const GAME_URL = 'http://localhost:3000';
const VIDEO_DIR = join(process.cwd(), 'test-results', 'videos');
const VIDEO_FILE = join(VIDEO_DIR, `manual-session-${Date.now()}.webm`);

mkdirSync(VIDEO_DIR, { recursive: true });

async function recordSession() {
  console.log('🎥 MANUAL SESSION RECORDER\n');
  console.log('================================================\n');
  console.log('This will:');
  console.log('1. Open browser with the game');
  console.log('2. Record 60 seconds of gameplay');
  console.log('3. Save video for analysis\n');
  console.log('YOU control the game - test position sync, elevation, etc.\n');
  console.log('Press Ctrl+C to stop early\n');
  console.log('================================================\n');

  const browser = await puppeteer.launch({
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1280,720',
      '--window-position=0,0',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  // Capture console for elevation debugging
  const elevationLogs = [];
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('🗺️') || text.includes('🏔️') || text.includes('Elevation')) {
      elevationLogs.push({ time: new Date().toISOString(), text });
      console.log('ELEVATION:', text);
    }
  });

  console.log('🌐 Loading game...');
  await page.goto(GAME_URL, { waitUntil: 'networkidle0' });

  console.log('⏳ Waiting for game to initialize...');
  await page.waitForFunction(
    () => {
      const scene = window.game?.scene?.getScene('IsoGameScene');
      return scene && scene.player;
    },
    { timeout: 15000 }
  );

  console.log('\n✅ Game ready!\n');
  console.log('🎬 Starting 60-second recording...');
  console.log('\n📋 TEST CHECKLIST:');
  console.log('   [ ] Move in multiple directions');
  console.log('   [ ] Walk onto elevated platforms');
  console.log('   [ ] Press Q/E to manually change elevation');
  console.log('   [ ] Check if player elevation changes automatically');
  console.log('   [ ] Look at character sprite (check for invisible legs)');
  console.log('   [ ] Open another browser to test position sync\n');

  // Get window ID for recording
  const windowInfo = await page.evaluate(() => ({
    width: window.innerWidth,
    height: window.innerHeight
  }));

  // Use ffmpeg with proper display capture
  // Note: This requires the session to have a DISPLAY set
  const ffmpeg = spawn('ffmpeg', [
    '-y',
    '-video_size', '1280x720',
    '-framerate', '30',
    '-f', 'x11grab',
    '-i', process.env.DISPLAY || ':0',
    '-t', '60',
    '-c:v', 'libvpx',
    '-quality', 'realtime',
    '-cpu-used', '5',
    '-b:v', '2M',
    VIDEO_FILE
  ]);

  ffmpeg.stderr.on('data', (data) => {
    // Suppress ffmpeg noise, but show errors
    const text = data.toString();
    if (text.includes('error') || text.includes('Error')) {
      console.error('FFmpeg:', text);
    }
  });

  ffmpeg.on('close', (code) => {
    console.log(`\n✅ Recording finished (exit code: ${code})`);
    console.log(`📹 Video saved: ${VIDEO_FILE}`);
    console.log(`\n📊 Elevation logs captured: ${elevationLogs.length}`);
    if (elevationLogs.length > 0) {
      console.log('\nLast 10 elevation checks:');
      elevationLogs.slice(-10).forEach(log => {
        console.log(`   ${log.text}`);
      });
    }
  });

  // Wait for recording to finish
  await new Promise(resolve => {
    setTimeout(async () => {
      await browser.close();
      resolve();
    }, 60000);
  });
}

recordSession().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
