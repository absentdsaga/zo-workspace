#!/usr/bin/env bun

/**
 * SURVIVAL MODE DEPLOYMENT
 *
 * Deploys the upgraded trading system with:
 * - Position manager with exit tracking
 * - Helius deployer safety checks
 * - Tighter risk management
 * - Anti-pump entry filters
 *
 * Balance: 0.1941 SOL (~$23)
 * Target: 10x in 30 days
 * Runway: ~2 days before circuit breaker
 */

import { SafeMasterCoordinator } from './core/safe-master-coordinator';

async function main() {
  console.log('🚀 DEPLOYING SURVIVAL MODE TRADING SYSTEM\n');

  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterKey = process.env.JUP_TOKEN;
  const heliusKey = process.env.HELIUS_RPC_URL;

  const rpcUrl = heliusKey
    ? `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`
    : 'https://api.mainnet-beta.solana.com';

  if (!privateKey || !jupiterKey || !heliusKey) {
    console.error('❌ Missing environment variables');
    console.error('   Required: SOLANA_PRIVATE_KEY, JUP_TOKEN, HELIUS_RPC_URL');
    process.exit(1);
  }

  console.log('📋 SURVIVAL MODE UPGRADES:');
  console.log('   ✅ Position Manager integrated');
  console.log('   ✅ Helius deployer checks (funded-by API)');
  console.log('   ✅ Tighter stops: -20% (was -30%)');
  console.log('   ✅ Faster exits: 30min max (was 60min)');
  console.log('   ✅ Higher take profit: +100% (was +50%)');
  console.log('   ✅ Anti-pump filters: Skip >20% 1h pumps');
  console.log('   ✅ Age filter: 2-6 hours (avoid early/late)');
  console.log('   ✅ Exit monitoring: Every 10s background loop');
  console.log('   ✅ Reduced position size: 5% (15 trades max)');
  console.log('');

  console.log('🎯 CRITICAL SITUATION:');
  console.log('   Current balance: ~0.19 SOL (~$23)');
  console.log('   Circuit breaker: 0.1 SOL');
  console.log('   Runway: ~2 days');
  console.log('   Need: 10x in 30 days');
  console.log('');

  console.log('⚠️  EXPERT CONSENSUS STRATEGY:');
  console.log('   Path A: 15 attempts at 5% positions');
  console.log('   Need: 60% win rate at 2:1 R/R');
  console.log('   If still losing after 5-10 trades → switch to Path B');
  console.log('   Path B: 2-3 high conviction 30% positions');
  console.log('');

  const coordinator = new SafeMasterCoordinator(rpcUrl, privateKey, jupiterKey, heliusKey);

  console.log('🔧 Initializing system...\n');
  await coordinator.initialize();

  console.log('\n🚀 Starting autonomous trading loop...');
  console.log('📝 Logs: /tmp/trading-bot.log');
  console.log('🌐 Dashboard: monitoring/dashboard.html');
  console.log('');

  // Run the coordinator
  await coordinator.run();
}

if (require.main === module) {
  main().catch((error) => {
    console.error('💥 Fatal error:', error);
    process.exit(1);
  });
}
