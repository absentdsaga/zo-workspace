#!/usr/bin/env node

// Test multiplayer + voice chat connection
const puppeteer = require('puppeteer');

(async () => {
  console.log('🧪 Testing Spatial Worlds Multiplayer + Voice...\n');

  const browser = await puppeteer.launch({
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--use-fake-ui-for-media-stream', // Auto-grant mic permission
      '--use-fake-device-for-media-stream',
      '--autoplay-policy=no-user-gesture-required'
    ]
  });

  const page = await browser.newPage();
  
  // Capture console messages
  const logs = [];
  page.on('console', msg => {
    const text = msg.text();
    logs.push(text);
    console.log(`[Browser] ${text}`);
  });

  // Navigate to game
  console.log('📍 Loading https://spatial-worlds-dioni.zocomputer.io/\n');
  await page.goto('https://spatial-worlds-dioni.zocomputer.io/', {
    waitUntil: 'networkidle2',
    timeout: 30000
  });

  // Wait for game to initialize
  console.log('⏳ Waiting 8 seconds for game initialization...\n');
  await page.waitForTimeout(8000);

  // Check what loaded
  console.log('\n📊 Connection Status:');
  console.log('='.repeat(50));
  
  const multiplayerConnected = logs.some(l => l.includes('Connected to multiplayer') || l.includes('You are player'));
  const voiceInitialized = logs.some(l => l.includes('Voice chat initialized') || l.includes('Joining Daily.co'));
  const errors = logs.filter(l => l.toLowerCase().includes('error') || l.toLowerCase().includes('failed'));
  
  console.log(`✅ Multiplayer WebSocket: ${multiplayerConnected ? 'CONNECTED' : '❌ NOT CONNECTED'}`);
  console.log(`✅ Voice Chat: ${voiceInitialized ? 'INITIALIZED' : '❌ NOT INITIALIZED'}`);
  console.log(`🚨 Errors: ${errors.length}`);
  
  if (errors.length > 0) {
    console.log('\n⚠️  Error Log:');
    errors.forEach(e => console.log(`   ${e}`));
  }

  // Test movement
  console.log('\n🎮 Testing Movement...');
  await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(500);
  await page.keyboard.press('ArrowDown');
  await page.waitForTimeout(500);
  await page.keyboard.press('ArrowLeft');
  await page.waitForTimeout(500);
  
  const movementLogs = logs.filter(l => 
    l.includes('position') || 
    l.includes('Broadcasted') ||
    l.includes('Moving')
  ).slice(-5);
  
  if (movementLogs.length > 0) {
    console.log('✅ Movement detected:');
    movementLogs.forEach(l => console.log(`   ${l}`));
  } else {
    console.log('❌ No movement detected');
  }

  console.log('\n' + '='.repeat(50));
  console.log('🏁 Test Complete\n');

  await page.waitForTimeout(2000);
  await browser.close();
})();
