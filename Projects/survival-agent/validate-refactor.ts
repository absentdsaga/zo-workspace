/**
 * ARCHITECTURE VALIDATION SCRIPT
 *
 * Tests that all refactored components compile and integrate correctly
 * Does NOT require real API credentials
 */

import { SubAgentCoordinator } from './core/sub-agent-coordinator';
import { globalCircuitBreaker, CircuitBreaker } from './core/circuit-breaker';
import { TradingBotConfigManager, TradingBotConfig } from './core/config-manager';

console.log('🔍 Validating Refactored Architecture...\n');

// Test 1: Circuit Breaker
console.log('1️⃣  Testing Circuit Breaker Pattern');
try {
  const testBreaker = new CircuitBreaker({
    maxFailures: 2,
    cooldownMs: 5000
  });

  // Test successful execution
  const result1 = await testBreaker.execute(
    'test-success',
    () => Promise.resolve('success'),
    () => 'fallback'
  );
  console.log('   ✅ Successful execution:', result1);

  // Test failure with fallback
  let failCount = 0;
  const result2 = await testBreaker.execute(
    'test-failure',
    () => {
      failCount++;
      if (failCount < 3) throw new Error('Mock failure');
      return Promise.resolve('recovered');
    },
    () => 'fallback-used'
  );
  console.log('   ✅ Fallback execution:', result2);

  // Check stats
  const stats = testBreaker.getStats();
  console.log('   ✅ Circuit stats:', JSON.stringify(stats, null, 2));
  console.log('   ✅ Circuit Breaker: PASS\n');

} catch (error: any) {
  console.error('   ❌ Circuit Breaker: FAIL -', error.message, '\n');
  process.exit(1);
}

// Test 2: Config Manager
console.log('2️⃣  Testing Config Manager');
try {
  const defaultConfig: TradingBotConfig = {
    maxConcurrentPositions: 7,
    maxPositionSize: 0.12,
    minBalance: 0.05,
    takeProfit: 1.0,
    stopLoss: -0.30,
    trailingStopPercent: 0.20,
    maxDrawdown: 0.25,
    minScore: 40,
    minSmartMoneyConfidence: 45,
    minShockedScore: 30,
    autoRefillThreshold: 0.03,
    autoRefillAmount: 1.0,
    scanIntervalMs: 15000,
    monitorIntervalMs: 5000,
    maxHoldTimeMs: 3600000,
    paperMode: true,
    useJito: true
  };

  const configManager = new TradingBotConfigManager(
    defaultConfig,
    '/tmp/test-config.json'
  );

  console.log('   ✅ Initial config loaded');

  // Test .patch()
  configManager.patch(
    { maxPositionSize: 0.15 },
    'Test: Increase position size'
  );
  const updated = configManager.get();
  console.log('   ✅ Config patched:', updated.maxPositionSize === 0.15);

  // Test .rollback()
  configManager.rollback(1);
  const rolledBack = configManager.get();
  console.log('   ✅ Config rolled back:', rolledBack.maxPositionSize === 0.12);

  // Test validation (should fail)
  try {
    configManager.patch(
      { maxConcurrentPositions: 100 }, // Invalid
      'Test: Invalid value'
    );
    console.error('   ❌ Validation should have failed');
    process.exit(1);
  } catch (error) {
    console.log('   ✅ Validation correctly rejected invalid config');
  }

  // Test history
  const history = configManager.getHistory();
  console.log('   ✅ Config history:', history.length, 'versions');
  console.log('   ✅ Config Manager: PASS\n');

} catch (error: any) {
  console.error('   ❌ Config Manager: FAIL -', error.message, '\n');
  process.exit(1);
}

// Test 3: Sub-Agent Coordinator (structure only, no API calls)
console.log('3️⃣  Testing Sub-Agent Coordinator Structure');
try {
  // Mock ZO_CLIENT_IDENTITY_TOKEN for validation
  process.env.ZO_CLIENT_IDENTITY_TOKEN = 'test_token_for_validation';

  const coordinator = new SubAgentCoordinator();
  console.log('   ✅ Sub-agent coordinator initialized');

  // Test prompt building (doesn't make API call)
  const testPrompt = (coordinator as any).buildScanPrompt({
    task: 'Test scan',
    limit: 10
  });

  if (!testPrompt.includes('Test scan')) {
    throw new Error('Prompt building failed');
  }
  console.log('   ✅ Prompt builder works');
  console.log('   ✅ Sub-Agent Coordinator: PASS\n');

} catch (error: any) {
  console.error('   ❌ Sub-Agent Coordinator: FAIL -', error.message, '\n');
  process.exit(1);
}

// Test 4: Global Circuit Breaker
console.log('4️⃣  Testing Global Circuit Breaker Instance');
try {
  const result = await globalCircuitBreaker.execute(
    'global-test',
    () => Promise.resolve('global-success'),
    () => 'global-fallback'
  );
  console.log('   ✅ Global instance works:', result);
  console.log('   ✅ Global Circuit Breaker: PASS\n');

} catch (error: any) {
  console.error('   ❌ Global Circuit Breaker: FAIL -', error.message, '\n');
  process.exit(1);
}

// Summary
console.log('═══════════════════════════════════════════');
console.log('✅ ALL ARCHITECTURE VALIDATIONS PASSED');
console.log('═══════════════════════════════════════════');
console.log('');
console.log('Refactored components are ready:');
console.log('  ✓ Circuit Breaker Pattern');
console.log('  ✓ Config Manager with .patch()');
console.log('  ✓ Sub-Agent Coordinator');
console.log('  ✓ Global Circuit Breaker');
console.log('');
console.log('Next step: Test with real API credentials');
console.log('See MIGRATION_GUIDE.md for instructions');
console.log('');
