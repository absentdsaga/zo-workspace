/**
 * MAINNET BOT ENTRY POINT v1.0
 *
 * Runs the same trading coordinator as paper-trade-bot.ts but with
 * mainnet settings (real transactions, tighter risk, separate data files).
 *
 * USAGE:
 *   bash start-mainnet.sh
 *
 * HOW TO TEST CHANGES:
 *   1. Make change in paper-trade-bot.ts (paper.config.ts)
 *   2. Run paper bot 48h+ - confirm win rate ≥30% and net P&L positive
 *   3. Apply same change to mainnet-bot.ts (mainnet.config.ts)
 *   Never skip paper validation before applying changes here.
 *
 * MONITOR:
 *   bash monitoring/dashboard.sh          # paper dashboard
 *   bash monitoring/mainnet-dashboard.sh  # mainnet dashboard
 */

import { CONFIG } from './config/mainnet.config';
import { OptimizedExecutor } from './core/optimized-executor';
import { CombinedScannerWebSocket } from './strategies/combined-scanner-websocket';
import { SmartMoneyTracker } from './strategies/smart-money-tracker';
import { JupiterValidator } from './core/jupiter-validator';
import { ShockedAlphaScanner } from './strategies/shocked-alpha-scanner';

// Import the coordinator class and TradeLog interface from paper-trade-bot
// The coordinator reads CONFIG at class-definition time from its own import,
// so for mainnet we pass config values explicitly via constructor overrides.
// Until the coordinator is extracted to core/, we use a lightweight approach:
// patch the module-level CONFIG before the class reads it.
//
// IMPLEMENTATION NOTE:
// The coordinator in paper-trade-bot.ts imports CONFIG from paper.config.ts
// at module load time. To run mainnet, we need to either:
//   A) Extract coordinator to core/trading-coordinator.ts (future refactor)
//   B) Run paper-trade-bot.ts with the import line swapped to mainnet.config
//
// For now: use approach B. This file serves as documentation + startup wrapper.
// The start-mainnet.sh script handles the config swap automatically.

async function main() {
  console.log(`🔴 MAINNET BOT v1.0\n`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('⚠️  REAL MONEY - LIVE TRANSACTIONS ON SOLANA MAINNET');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  console.log('Settings vs Paper:');
  console.log(`  Max positions:  ${CONFIG.MAX_CONCURRENT_POSITIONS}  (paper: 7)`);
  console.log(`  Position size:  ${(CONFIG.MAX_POSITION_SIZE * 100).toFixed(0)}%  (paper: 12%)`);
  console.log(`  Stop loss:      ${(CONFIG.STOP_LOSS * 100).toFixed(0)}%  (paper: -30%)`);
  console.log(`  Starting bal:   ${CONFIG.STARTING_BALANCE} SOL`);
  console.log(`  Data files:     /home/workspace/Projects/survival-agent/data/mainnet-trades-*.json\n`);

  const privateKey = process.env.MAINNET_PRIVATE_KEY || process.env.SOLANA_PRIVATE_KEY;
  const jupiterApiKey = process.env.JUP_TOKEN;
  const heliusApiKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;

  if (!privateKey || !jupiterApiKey || !heliusApiKey) {
    console.error('❌ Missing env vars. Need: MAINNET_PRIVATE_KEY, JUP_TOKEN, HELIUS_API_KEY');
    process.exit(1);
  }

  if (!process.env.MAINNET_PRIVATE_KEY) {
    console.warn('⚠️  Using SOLANA_PRIVATE_KEY - consider setting MAINNET_PRIVATE_KEY separately');
  }

  const rpcUrl = `https://beta.helius-rpc.com/?api-key=${heliusApiKey}`;

  console.log('⚡ Starting in 5 seconds... Ctrl+C to abort\n');
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Validate we can connect and get a quote before committing
  console.log('🔍 Pre-flight: verifying RPC + Jupiter connectivity...');
  const executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey, false);
  const check = await executor.preFlightCheck();

  if (!check.ready) {
    console.error('❌ Pre-flight failed:', check.error);
    process.exit(1);
  }

  console.log(`✅ Pre-flight passed. Wallet: ${check.walletAddress}`);
  console.log(`   Balance: ${check.balance?.toFixed(4)} SOL\n`);

  if ((check.balance || 0) < CONFIG.STARTING_BALANCE) {
    console.error(`❌ Wallet balance ${check.balance?.toFixed(4)} SOL is less than starting balance ${CONFIG.STARTING_BALANCE} SOL`);
    process.exit(1);
  }

  // Run the full coordinator using paper-trade-bot's class
  // but with mainnet config values injected via CONFIG import above.
  // This works because paper-trade-bot.ts reads CONFIG from paper.config,
  // while this file reads from mainnet.config - they run as separate processes.
  const { default: runBot } = await import('./testing/paper-trade-bot');
  // paper-trade-bot exports nothing - it self-executes via main()
  // So we run it as a subprocess via start-mainnet.sh instead.
  // See start-mainnet.sh for the actual execution approach.

  console.log('ℹ️  Use start-mainnet.sh to launch (handles config swap automatically)');
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
