#!/usr/bin/env node
/**
 * Detailed diagnostic test - captures position data and elevation logs
 * without requiring video recording
 */
import puppeteer from 'puppeteer';
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

const GAME_URL = 'http://localhost:3000';
const RESULTS_DIR = join(process.cwd(), 'test-results', 'diagnostics');
mkdirSync(RESULTS_DIR, { recursive: true });

async function runDiagnostics() {
  console.log('🔍 DETAILED DIAGNOSTICS TEST\n');
  console.log('================================================\n');

  const diagnosticData = {
    startTime: new Date().toISOString(),
    tests: [],
    positionHistory: [],
    elevationLogs: [],
    consoleErrors: []
  };

  // Launch 2 browsers for multiplayer test
  console.log('🚀 Launching 2 browser instances...');
  const browser1 = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });
  const browser2 = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page1 = await browser1.newPage();
  const page2 = await browser2.newPage();

  // Capture console logs
  page1.on('console', msg => {
    const text = msg.text();
    if (text.includes('🗺️') || text.includes('🏔️') || text.includes('Elevation')) {
      diagnosticData.elevationLogs.push({ player: 1, time: new Date().toISOString(), text });
    }
  });

  page2.on('console', msg => {
    const text = msg.text();
    if (text.includes('🗺️') || text.includes('🏔️') || text.includes('Elevation')) {
      diagnosticData.elevationLogs.push({ player: 2, time: new Date().toISOString(), text });
    }
  });

  page1.on('pageerror', err => diagnosticData.consoleErrors.push({ player: 1, error: err.message }));
  page2.on('pageerror', err => diagnosticData.consoleErrors.push({ player: 2, error: err.message }));

  try {
    // Load game in both browsers
    console.log('🌐 Loading game in both browsers...');
    await Promise.all([
      page1.goto(GAME_URL, { waitUntil: 'networkidle0', timeout: 20000 }),
      page2.goto(GAME_URL, { waitUntil: 'networkidle0', timeout: 20000 })
    ]);

    console.log('⏳ Waiting for game initialization...');
    await Promise.all([
      page1.waitForFunction(
        () => window.game?.scene?.getScene('IsoGameScene')?.player,
        { timeout: 15000 }
      ),
      page2.waitForFunction(
        () => window.game?.scene?.getScene('IsoGameScene')?.player,
        { timeout: 15000 }
      )
    ]);

    console.log('✅ Both games initialized\n');

    // Wait for multiplayer connection
    await new Promise(r => setTimeout(r, 2000));

    // Test 1: Position Sync During Movement
    console.log('📍 TEST 1: Position Sync During Movement');
    console.log('   Moving Player1 right for 2 seconds...');

    const beforeMove = await getDetailedState(page1, page2);
    diagnosticData.positionHistory.push({ label: 'before_movement', ...beforeMove });

    await page1.keyboard.down('d');

    // Sample positions every 200ms during movement
    for (let i = 0; i < 10; i++) {
      await new Promise(r => setTimeout(r, 200));
      const during = await getDetailedState(page1, page2);
      diagnosticData.positionHistory.push({
        label: `during_movement_${i}`,
        timeMs: i * 200,
        ...during
      });
    }

    await page1.keyboard.up('d');

    // Wait for lerp to catch up
    await new Promise(r => setTimeout(r, 1500));

    const afterMove = await getDetailedState(page1, page2);
    diagnosticData.positionHistory.push({ label: 'after_movement', ...afterMove });

    const syncDelta = Math.abs(afterMove.player1.local.x - afterMove.player2.remotePlayer1.x);
    console.log(`   Player1 at: (${afterMove.player1.local.x}, ${afterMove.player1.local.y})`);
    console.log(`   Player2 sees Player1 at: (${afterMove.player2.remotePlayer1.x}, ${afterMove.player2.remotePlayer1.y})`);
    console.log(`   Position delta: ${syncDelta}px ${syncDelta < 100 ? '✅' : '❌'}\n`);

    diagnosticData.tests.push({
      name: 'Position Sync',
      passed: syncDelta < 100,
      delta: syncDelta,
      details: afterMove
    });

    // Test 2: Elevation Detection
    console.log('🏔️  TEST 2: Elevation Detection');
    console.log('   Moving Player1 to elevated platform (northeast corner)...');

    // Move to elevated area
    await page1.keyboard.down('w');
    await page1.keyboard.down('d');
    await new Promise(r => setTimeout(r, 4000));
    await page1.keyboard.up('w');
    await page1.keyboard.up('d');
    await new Promise(r => setTimeout(r, 500));

    const onPlatform = await getDetailedState(page1, page2);
    diagnosticData.positionHistory.push({ label: 'on_elevated_platform', ...onPlatform });

    console.log(`   Player1 position: (${Math.round(onPlatform.player1.local.x)}, ${Math.round(onPlatform.player1.local.y)})`);
    console.log(`   Player1 elevation: ${onPlatform.player1.local.elevation}`);
    console.log(`   Expected: elevation > 0 for elevated platform`);
    console.log(`   Result: ${onPlatform.player1.local.elevation > 0 ? '✅ Auto-elevation working!' : '❌ Still at ground level'}\n`);

    diagnosticData.tests.push({
      name: 'Auto-Elevation',
      passed: onPlatform.player1.local.elevation > 0,
      elevation: onPlatform.player1.local.elevation,
      position: { x: onPlatform.player1.local.x, y: onPlatform.player1.local.y }
    });

    // Test 3: Manual Elevation Controls
    console.log('⬆️  TEST 3: Manual Elevation Controls (E key)');
    const beforeE = onPlatform.player1.local.elevation;
    await page1.keyboard.press('e');
    await new Promise(r => setTimeout(r, 300));
    await page1.keyboard.press('e');
    await new Promise(r => setTimeout(r, 300));

    const afterE = await getDetailedState(page1, page2);
    diagnosticData.positionHistory.push({ label: 'after_manual_elevation', ...afterE });

    console.log(`   Elevation before E presses: ${beforeE}`);
    console.log(`   Elevation after E presses: ${afterE.player1.local.elevation}`);
    console.log(`   Changed: ${afterE.player1.local.elevation > beforeE ? '✅' : '❌'}\n`);

    diagnosticData.tests.push({
      name: 'Manual Elevation',
      passed: afterE.player1.local.elevation > beforeE,
      elevationBefore: beforeE,
      elevationAfter: afterE.player1.local.elevation
    });

    // Test 4: Bidirectional Sync
    console.log('🔄 TEST 4: Bidirectional Sync');
    console.log('   Moving Player2 left while Player1 moves right...');

    const beforeBidi = await getDetailedState(page1, page2);

    await page1.keyboard.down('d');
    await page2.keyboard.down('a');
    await new Promise(r => setTimeout(r, 1500));
    await page1.keyboard.up('d');
    await page2.keyboard.up('a');
    await new Promise(r => setTimeout(r, 1500));

    const afterBidi = await getDetailedState(page1, page2);
    diagnosticData.positionHistory.push({ label: 'after_bidirectional', ...afterBidi });

    const player1Moved = Math.abs(afterBidi.player1.local.x - beforeBidi.player1.local.x) > 50;
    const player2Moved = Math.abs(afterBidi.player2.local.x - beforeBidi.player2.local.x) > 50;
    const p1SeesP2 = Math.abs(afterBidi.player1.remotePlayer2.x - afterBidi.player2.local.x) < 100;
    const p2SeesP1 = Math.abs(afterBidi.player2.remotePlayer1.x - afterBidi.player1.local.x) < 100;

    console.log(`   Player1 moved: ${player1Moved ? '✅' : '❌'}`);
    console.log(`   Player2 moved: ${player2Moved ? '✅' : '❌'}`);
    console.log(`   Player1 sees Player2 correctly: ${p1SeesP2 ? '✅' : '❌'}`);
    console.log(`   Player2 sees Player1 correctly: ${p2SeesP1 ? '✅' : '❌'}\n`);

    diagnosticData.tests.push({
      name: 'Bidirectional Sync',
      passed: player1Moved && player2Moved && p1SeesP2 && p2SeesP1,
      details: { player1Moved, player2Moved, p1SeesP2, p2SeesP1 }
    });

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    diagnosticData.error = error.message;
  } finally {
    await browser1.close();
    await browser2.close();
  }

  diagnosticData.endTime = new Date().toISOString();

  // Save results
  const resultFile = join(RESULTS_DIR, `diagnostics-${Date.now()}.json`);
  writeFileSync(resultFile, JSON.stringify(diagnosticData, null, 2));
  console.log(`\n📊 Diagnostic data saved: ${resultFile}`);

  // Summary
  console.log('\n================================================');
  console.log('📋 SUMMARY\n');
  const passed = diagnosticData.tests.filter(t => t.passed).length;
  const total = diagnosticData.tests.length;
  console.log(`Tests: ${passed}/${total} passed`);
  diagnosticData.tests.forEach(test => {
    console.log(`   ${test.passed ? '✅' : '❌'} ${test.name}`);
  });

  console.log(`\n📝 Elevation logs: ${diagnosticData.elevationLogs.length}`);
  if (diagnosticData.elevationLogs.length > 0) {
    console.log('\nLast 10 elevation logs:');
    diagnosticData.elevationLogs.slice(-10).forEach(log => {
      console.log(`   [Player${log.player}] ${log.text}`);
    });
  } else {
    console.log('   ⚠️  No elevation logs captured - debug logging may not be working');
  }

  console.log(`\n🐛 Console errors: ${diagnosticData.consoleErrors.length}`);
  if (diagnosticData.consoleErrors.length > 0) {
    diagnosticData.consoleErrors.forEach(err => {
      console.log(`   [Player${err.player}] ${err.error}`);
    });
  }

  console.log('\n================================================\n');
}

async function getDetailedState(page1, page2) {
  const [state1, state2] = await Promise.all([
    page1.evaluate(() => {
      const scene = window.game.scene.getScene('IsoGameScene');
      const local = scene.player;
      const localIso = local.getData('iso');
      const remotePlayers = scene.multiplayerManager.getRemotePlayers();

      return {
        local: {
          id: scene.multiplayerManager.localPlayerId,
          x: Math.round(local.x),
          y: Math.round(local.y),
          elevation: localIso?.elevation || 0
        },
        remotePlayers: remotePlayers.map(rp => ({
          id: rp.id,
          x: Math.round(rp.sprite.x),
          y: Math.round(rp.sprite.y),
          elevation: rp.sprite.getData('iso')?.elevation || 0
        }))
      };
    }),
    page2.evaluate(() => {
      const scene = window.game.scene.getScene('IsoGameScene');
      const local = scene.player;
      const localIso = local.getData('iso');
      const remotePlayers = scene.multiplayerManager.getRemotePlayers();

      return {
        local: {
          id: scene.multiplayerManager.localPlayerId,
          x: Math.round(local.x),
          y: Math.round(local.y),
          elevation: localIso?.elevation || 0
        },
        remotePlayers: remotePlayers.map(rp => ({
          id: rp.id,
          x: Math.round(rp.sprite.x),
          y: Math.round(rp.sprite.y),
          elevation: rp.sprite.getData('iso')?.elevation || 0
        }))
      };
    })
  ]);

  return {
    player1: {
      local: state1.local,
      remotePlayer2: state1.remotePlayers.find(rp => rp.id === state2.local.id) || { x: 0, y: 0, elevation: 0 }
    },
    player2: {
      local: state2.local,
      remotePlayer1: state2.remotePlayers.find(rp => rp.id === state1.local.id) || { x: 0, y: 0, elevation: 0 }
    }
  };
}

runDiagnostics().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
