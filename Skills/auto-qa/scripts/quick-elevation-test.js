#!/usr/bin/env node
/**
 * Quick test to verify elevation auto-detection is working
 * Captures console logs showing elevation changes
 */
import puppeteer from 'puppeteer';

const GAME_URL = 'http://localhost:3000';

async function testElevation() {
  console.log('🏔️  ELEVATION AUTO-DETECTION TEST\n');
  console.log('================================================\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--use-angle=swiftshader']
  });

  const page = await browser.newPage();

  // Capture ALL console logs
  const logs = [];
  page.on('console', msg => {
    const text = msg.text();
    logs.push(text);
    if (text.includes('🗺️') || text.includes('🏔️') || text.includes('Elevation')) {
      console.log('  ', text);
    }
  });

  page.on('pageerror', err => {
    if (!err.message.includes('WebGL')) {
      console.error('  ERROR:', err.message);
    }
  });

  try {
    console.log('🌐 Loading game...');
    await page.goto(GAME_URL, { waitUntil: 'networkidle0', timeout: 10000 });

    console.log('⏳ Waiting for game...');
    await page.waitForFunction(
      () => window.game?.scene?.getScene('IsoGameScene')?.player,
      { timeout: 10000 }
    );

    console.log('✅ Game loaded\n');
    console.log('📍 Testing elevation detection:\n');

    // Get initial position
    const initial = await page.evaluate(() => {
      const scene = window.game.scene.getScene('IsoGameScene');
      const iso = scene.player.getData('iso');
      return {
        x: Math.round(scene.player.x),
        y: Math.round(scene.player.y),
        elevation: iso?.elevation || 0
      };
    });
    console.log(`  Initial: pos(${initial.x}, ${initial.y}) elevation=${initial.elevation}\n`);

    // Move northeast to elevated platform
    console.log('  Moving to elevated platform (northeast corner)...');
    await page.keyboard.down('w');
    await page.keyboard.down('d');
    await new Promise(r => setTimeout(r, 3000));
    await page.keyboard.up('w');
    await page.keyboard.up('d');
    await new Promise(r => setTimeout(r, 500));

    const onPlatform = await page.evaluate(() => {
      const scene = window.game.scene.getScene('IsoGameScene');
      const iso = scene.player.getData('iso');
      return {
        x: Math.round(scene.player.x),
        y: Math.round(scene.player.y),
        elevation: iso?.elevation || 0
      };
    });
    console.log(`\n  On platform: pos(${onPlatform.x}, ${onPlatform.y}) elevation=${onPlatform.elevation}`);

    // Check result
    if (onPlatform.elevation > 0) {
      console.log('\n✅ SUCCESS: Auto-elevation is working! Elevation changed from 0 to', onPlatform.elevation);
    } else {
      console.log('\n❌ FAIL: Auto-elevation not working. Still at elevation 0');
      console.log('  Expected: elevation > 0 when on elevated platform');
    }

    // Test manual elevation
    console.log('\n  Testing manual elevation (E key)...');
    const beforeE = onPlatform.elevation;
    await page.keyboard.press('e');
    await new Promise(r => setTimeout(r, 300));

    const afterE = await page.evaluate(() => {
      const scene = window.game.scene.getScene('IsoGameScene');
      const iso = scene.player.getData('iso');
      return iso?.elevation || 0;
    });

    console.log(`  Before E: ${beforeE}, After E: ${afterE}`);
    if (afterE > beforeE) {
      console.log('  ✅ Manual elevation working');
    } else {
      console.log('  ❌ Manual elevation not working');
    }

    console.log('\n📝 Total console logs captured:', logs.length);
    const elevationLogs = logs.filter(l => l.includes('🗺️') || l.includes('🏔️') || l.includes('Elevation'));
    console.log('   Elevation-related logs:', elevationLogs.length);

    if (elevationLogs.length === 0) {
      console.log('   ⚠️  No elevation debug logs found - logging may not be enabled');
    }

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testElevation().catch(console.error);
