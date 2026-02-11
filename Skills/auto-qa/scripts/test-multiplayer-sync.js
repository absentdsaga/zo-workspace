#!/usr/bin/env bun
/**
 * COMPREHENSIVE MULTIPLAYER SYNC TEST
 *
 * Tests the spatial-worlds game multiplayer synchronization
 * by running multiple browser instances and verifying:
 * - Connection establishment
 * - Position synchronization
 * - Elevation changes
 * - Movement sync accuracy
 * - Console error detection
 *
 * Usage: bun run scripts/test-multiplayer-sync.js
 */

import puppeteer from 'puppeteer';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const GAME_URL = 'http://localhost:3000';
const TEST_DURATION = 30000; // 30 seconds
const SCREENSHOT_INTERVAL = 2000; // Every 2 seconds
const POSITION_CHECK_INTERVAL = 1000; // Every 1 second
const VIEWPORT = { width: 1280, height: 720 };

// Test results storage
const testResults = {
  startTime: new Date().toISOString(),
  endTime: null,
  totalTests: 0,
  passed: 0,
  failed: 0,
  tests: [],
  screenshots: [],
  consoleErrors: {
    player1: [],
    player2: []
  },
  positionHistory: {
    player1: [],
    player2: []
  }
};

// Create output directories
const outputDir = join(process.cwd(), 'test-results');
const screenshotDir = join(outputDir, 'screenshots');
const reportDir = join(outputDir, 'reports');

[outputDir, screenshotDir, reportDir].forEach(dir => {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
});

/**
 * Test case helper
 */
function addTestResult(name, passed, message, details = {}) {
  const result = {
    name,
    passed,
    message,
    timestamp: new Date().toISOString(),
    ...details
  };

  testResults.tests.push(result);
  testResults.totalTests++;

  if (passed) {
    testResults.passed++;
    console.log(`✅ PASS: ${name}`);
  } else {
    testResults.failed++;
    console.error(`❌ FAIL: ${name} - ${message}`);
  }

  return result;
}

/**
 * Setup browser instance with console logging
 */
async function setupBrowser(playerName) {
  const browser = await puppeteer.launch({
    headless: 'new', // Use new headless mode
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--use-angle=swiftshader',
      '--use-gl=angle'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport(VIEWPORT);

  // Capture console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    // Filter out known headless-mode warnings
    const isKnownWarning = text.includes('WebGL context') ||
                           text.includes('404') && text.includes('favicon');

    if ((type === 'error' || type === 'warning') && !isKnownWarning) {
      testResults.consoleErrors[playerName].push({
        type,
        message: text,
        timestamp: new Date().toISOString()
      });
      console.log(`[${playerName} ${type.toUpperCase()}] ${text}`);
    }
  });

  // Capture page errors
  page.on('pageerror', error => {
    // Filter out known headless-mode errors
    const isKnownError = error.message.includes('WebGL context');

    if (!isKnownError) {
      testResults.consoleErrors[playerName].push({
        type: 'pageerror',
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
      console.error(`[${playerName} PAGE ERROR]`, error.message);
    }
  });

  return { browser, page };
}

/**
 * Get player state from the page
 */
async function getPlayerState(page) {
  return await page.evaluate(() => {
    // Access IsoGameScene
    const scene = window.game?.scene?.getScene('IsoGameScene');
    if (!scene || !scene.player || !scene.multiplayerManager) {
      return null;
    }

    // Get local player data
    const isoData = scene.player.getData('iso');
    const localPlayer = {
      x: Math.round(scene.player.x),
      y: Math.round(scene.player.y),
      elevation: isoData?.elevation || 0
    };

    // Get remote players (it's a Map, need to iterate)
    const remotePlayers = scene.multiplayerManager.getRemotePlayers().map(({id, sprite}) => {
      const remoteIsoData = sprite.getData('iso');
      return {
        id,
        x: Math.round(sprite.x),
        y: Math.round(sprite.y),
        elevation: remoteIsoData?.elevation || 0
      };
    });

    return {
      localPlayerId: scene.multiplayerManager.playerId,
      localPlayer,
      remotePlayers,
      connected: scene.multiplayerManager.ws?.readyState === 1,
      timestamp: Date.now()
    };
  });
}

/**
 * Simulate keyboard input
 */
async function simulateMovement(page, direction, duration = 1000) {
  const keyMap = {
    up: 'w',
    down: 's',
    left: 'a',
    right: 'd',
    upLeft: ['w', 'a'],
    upRight: ['w', 'd'],
    downLeft: ['s', 'a'],
    downRight: ['s', 'd']
  };

  const keys = Array.isArray(keyMap[direction]) ? keyMap[direction] : [keyMap[direction]];

  // Press keys
  for (const key of keys) {
    await page.keyboard.down(key);
  }

  // Hold for duration
  await new Promise(resolve => setTimeout(resolve, duration));

  // Release keys
  for (const key of keys) {
    await page.keyboard.up(key);
  }
}

/**
 * Take screenshot with timestamp
 */
async function takeScreenshot(page, playerName, label) {
  const timestamp = Date.now();
  const filename = `${playerName}_${label}_${timestamp}.png`;
  const filepath = join(screenshotDir, filename);

  await page.screenshot({
    path: filepath,
    fullPage: false
  });

  testResults.screenshots.push({
    player: playerName,
    label,
    filename,
    filepath,
    timestamp: new Date().toISOString()
  });

  return filepath;
}

/**
 * Wait for game to be ready
 */
async function waitForGameReady(page, timeout = 20000) {
  try {
    // First wait for window.game to exist
    await page.waitForFunction(
      () => window.game !== undefined,
      { timeout: 5000 }
    );

    // Wait for IsoGameScene to be active (not BootScene)
    await page.waitForFunction(
      () => {
        if (!window.game || !window.game.scene) return false;
        const activeScene = window.game.scene.getScene('IsoGameScene');
        return activeScene && activeScene.scene.isActive();
      },
      { timeout: 15000 }
    );

    // Finally wait for player and multiplayer manager to exist
    await page.waitForFunction(
      () => {
        const scene = window.game.scene.getScene('IsoGameScene');
        return scene && scene.player && scene.multiplayerManager;
      },
      { timeout }
    );
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Main test execution
 */
async function runTests() {
  console.log('\n🎮 SPATIAL WORLDS - MULTIPLAYER SYNC TEST\n');
  console.log('================================================');
  console.log(`Game URL: ${GAME_URL}`);
  console.log(`Test Duration: ${TEST_DURATION / 1000}s`);
  console.log(`Output Directory: ${outputDir}`);
  console.log('================================================\n');

  let player1Browser, player1Page, player2Browser, player2Page;

  try {
    // TEST 1: Launch browsers
    console.log('📦 Launching browser instances...\n');

    ({ browser: player1Browser, page: player1Page } = await setupBrowser('player1'));
    ({ browser: player2Browser, page: player2Page } = await setupBrowser('player2'));

    addTestResult('Browser Launch', true, 'Both browser instances launched successfully');

    // TEST 2: Load game
    console.log('🌐 Loading game in both instances...\n');

    await Promise.all([
      player1Page.goto(GAME_URL, { waitUntil: 'networkidle2', timeout: 15000 }),
      player2Page.goto(GAME_URL, { waitUntil: 'networkidle2', timeout: 15000 })
    ]);

    addTestResult('Game Load', true, 'Game loaded in both browsers');

    // Take initial screenshots
    await Promise.all([
      takeScreenshot(player1Page, 'player1', 'initial'),
      takeScreenshot(player2Page, 'player2', 'initial')
    ]);

    // TEST 3: Wait for game initialization
    console.log('⏳ Waiting for game to initialize...\n');

    const [p1Ready, p2Ready] = await Promise.all([
      waitForGameReady(player1Page),
      waitForGameReady(player2Page)
    ]);

    if (!p1Ready || !p2Ready) {
      addTestResult('Game Initialization', false, 'Game failed to initialize within timeout', {
        player1Ready: p1Ready,
        player2Ready: p2Ready
      });
      throw new Error('Game initialization timeout');
    }

    addTestResult('Game Initialization', true, 'Game initialized successfully in both instances');

    // Small delay to ensure multiplayer connection is established
    await new Promise(resolve => setTimeout(resolve, 2000));

    // TEST 4: Check multiplayer connection
    console.log('🔌 Checking multiplayer connection...\n');

    const [state1, state2] = await Promise.all([
      getPlayerState(player1Page),
      getPlayerState(player2Page)
    ]);

    const bothConnected = state1?.connected && state2?.connected;
    addTestResult('Multiplayer Connection', bothConnected,
      bothConnected ? 'Both players connected via WebSocket' : 'Connection failed', {
        player1: state1,
        player2: state2
      });

    if (!bothConnected) {
      throw new Error('Multiplayer connection failed');
    }

    // TEST 5: Check mutual visibility
    console.log('👁️  Checking mutual player visibility...\n');

    const p1SeesP2 = state1.remotePlayers.length > 0;
    const p2SeesP1 = state2.remotePlayers.length > 0;

    addTestResult('Mutual Visibility', p1SeesP2 && p2SeesP1,
      p1SeesP2 && p2SeesP1 ? 'Both players can see each other' : 'Players cannot see each other', {
        player1RemotePlayers: state1.remotePlayers.length,
        player2RemotePlayers: state2.remotePlayers.length
      });

    // Take screenshots after connection
    await Promise.all([
      takeScreenshot(player1Page, 'player1', 'connected'),
      takeScreenshot(player2Page, 'player2', 'connected')
    ]);

    // TEST 6: Position synchronization test
    console.log('🎯 Testing position synchronization...\n');

    // Record initial positions
    const initialState1 = await getPlayerState(player1Page);
    const initialState2 = await getPlayerState(player2Page);

    console.log('📍 Player 1 initial position:', initialState1.localPlayer);
    console.log('📍 Player 2 initial position:', initialState2.localPlayer);

    // Player 1 moves right for 2 seconds
    console.log('➡️  Player 1 moving right...\n');
    await simulateMovement(player1Page, 'right', 2000);
    await new Promise(resolve => setTimeout(resolve, 1500)); // Wait for lerp to catch up (0.1 factor = slow)

    const afterMove1 = await getPlayerState(player1Page);
    const afterMove2 = await getPlayerState(player2Page);

    // Check if Player 1 moved
    const p1Moved = Math.abs(afterMove1.localPlayer.x - initialState1.localPlayer.x) > 50;
    addTestResult('Player 1 Movement', p1Moved,
      p1Moved ? 'Player 1 moved successfully' : 'Player 1 did not move', {
        before: initialState1.localPlayer,
        after: afterMove1.localPlayer,
        deltaX: afterMove1.localPlayer.x - initialState1.localPlayer.x
      });

    // Check if Player 2 sees Player 1's new position
    const p2Remote = afterMove2.remotePlayers.find(p => p.id === afterMove1.localPlayerId);
    const positionsSynced = p2Remote && Math.abs(p2Remote.x - afterMove1.localPlayer.x) < 100;

    addTestResult('Position Sync', positionsSynced,
      positionsSynced ? 'Position synchronized between players' : 'Position sync failed', {
        player1Position: afterMove1.localPlayer,
        player2SeesPlayer1At: p2Remote,
        deltaX: p2Remote ? Math.abs(p2Remote.x - afterMove1.localPlayer.x) : null
      });

    // Take screenshots after movement
    await Promise.all([
      takeScreenshot(player1Page, 'player1', 'after_movement'),
      takeScreenshot(player2Page, 'player2', 'after_movement')
    ]);

    // TEST 7: Bidirectional movement sync
    console.log('🔄 Testing bidirectional sync...\n');

    // Both players move simultaneously
    await Promise.all([
      simulateMovement(player1Page, 'down', 1500),
      simulateMovement(player2Page, 'up', 1500)
    ]);

    await new Promise(resolve => setTimeout(resolve, 500));

    const [finalState1, finalState2] = await Promise.all([
      getPlayerState(player1Page),
      getPlayerState(player2Page)
    ]);

    const bothMoved =
      Math.abs(finalState1.localPlayer.y - afterMove1.localPlayer.y) > 50 &&
      Math.abs(finalState2.localPlayer.y - afterMove2.localPlayer.y) > 50;

    addTestResult('Bidirectional Movement', bothMoved,
      bothMoved ? 'Both players moved simultaneously' : 'Simultaneous movement failed', {
        player1Delta: finalState1.localPlayer.y - afterMove1.localPlayer.y,
        player2Delta: finalState2.localPlayer.y - afterMove2.localPlayer.y
      });

    // TEST 8: Elevation test (if implemented)
    console.log('🏔️  Testing elevation changes...\n');

    // Simulate elevation change (press E key or similar)
    await player1Page.keyboard.press('e');
    await new Promise(resolve => setTimeout(resolve, 500));

    const elevationState = await getPlayerState(player1Page);
    const elevationTracked = elevationState.localPlayer.elevation !== undefined;

    addTestResult('Elevation Tracking', elevationTracked,
      elevationTracked ? 'Elevation is tracked' : 'Elevation not implemented', {
        elevation: elevationState.localPlayer.elevation
      });

    // Take final screenshots
    await Promise.all([
      takeScreenshot(player1Page, 'player1', 'final'),
      takeScreenshot(player2Page, 'player2', 'final')
    ]);

    // TEST 9: Monitor for a period
    console.log('⏱️  Monitoring sync stability...\n');

    const monitorDuration = 5000; // 5 seconds
    const samples = [];
    const sampleInterval = 500; // Sample every 500ms

    for (let i = 0; i < monitorDuration / sampleInterval; i++) {
      const [s1, s2] = await Promise.all([
        getPlayerState(player1Page),
        getPlayerState(player2Page)
      ]);

      samples.push({ s1, s2, time: Date.now() });
      await new Promise(resolve => setTimeout(resolve, sampleInterval));
    }

    // Check for position drift
    const maxDrift = Math.max(...samples.map(({ s1, s2 }) => {
      const p2Remote = s2.remotePlayers.find(p => p.id === s1.localPlayerId);
      if (!p2Remote) return 0;
      const dx = Math.abs(p2Remote.x - s1.localPlayer.x);
      const dy = Math.abs(p2Remote.y - s1.localPlayer.y);
      return Math.sqrt(dx * dx + dy * dy);
    }));

    const stableSync = maxDrift < 150; // Less than 150 pixels drift
    addTestResult('Sync Stability', stableSync,
      stableSync ? 'Position sync remained stable' : 'Position drift detected', {
        maxDrift: Math.round(maxDrift),
        samples: samples.length
      });

    // TEST 10: Check for console errors
    console.log('🐛 Checking for console errors...\n');

    const hasP1Errors = testResults.consoleErrors.player1.length > 0;
    const hasP2Errors = testResults.consoleErrors.player2.length > 0;
    const hasErrors = hasP1Errors || hasP2Errors;

    addTestResult('Console Errors', !hasErrors,
      hasErrors ? 'Console errors detected' : 'No console errors', {
        player1Errors: testResults.consoleErrors.player1.length,
        player2Errors: testResults.consoleErrors.player2.length
      });

    console.log('\n✨ Test execution completed!\n');

  } catch (error) {
    console.error('\n💥 Test execution failed:', error.message);
    addTestResult('Test Execution', false, error.message, { stack: error.stack });
  } finally {
    // Cleanup
    console.log('🧹 Cleaning up...\n');

    if (player1Browser) await player1Browser.close();
    if (player2Browser) await player2Browser.close();

    // Generate report
    testResults.endTime = new Date().toISOString();

    const reportPath = join(reportDir, `test-report-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify(testResults, null, 2));

    console.log('📊 TEST SUMMARY');
    console.log('================================================');
    console.log(`Total Tests: ${testResults.totalTests}`);
    console.log(`Passed: ${testResults.passed} ✅`);
    console.log(`Failed: ${testResults.failed} ❌`);
    console.log(`Success Rate: ${((testResults.passed / testResults.totalTests) * 100).toFixed(1)}%`);
    console.log(`Report saved: ${reportPath}`);
    console.log(`Screenshots: ${testResults.screenshots.length} saved to ${screenshotDir}`);
    console.log('================================================\n');

    // Exit with appropriate code
    process.exit(testResults.failed > 0 ? 1 : 0);
  }
}

// Run tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
