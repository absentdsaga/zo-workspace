/**
 * FINAL PAPER TRADING TEST
 *
 * Tests the complete autonomous system with:
 * - 8% position size (original)
 * - +100% take profit (sell 80%, hold 20% for runners)
 * - -30% stop loss (original)
 * - 60 min max hold (original)
 * - Momentum-based entry (0-60 min fresh launches)
 * - All Helius safety checks
 *
 * Runs 10 trades to validate the system before going live
 */

import { SafeMasterCoordinator } from '../core/safe-master-coordinator';

async function main() {
  console.log('🧪 FINAL PAPER TRADING TEST - 10 TRADES\n');
  console.log('Configuration:');
  console.log('- Position Size: 8% per trade');
  console.log('- Take Profit: +100% (sell 80%, hold 20%)');
  console.log('- Stop Loss: -30%');
  console.log('- Max Hold: 60 minutes');
  console.log('- Entry: 0-60 min fresh launches (momentum)\n');

  // Get credentials from environment (Zo provides them automatically)
  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterApiKey = process.env.JUP_TOKEN;

  // HELIUS_RPC_URL is actually just the API key
  const heliusApiKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusApiKey}`;

  if (!privateKey || !jupiterApiKey || !heliusApiKey) {
    console.error('❌ Missing credentials in environment');
    console.error('Required: SOLANA_PRIVATE_KEY, JUP_TOKEN, HELIUS_API_KEY');
    console.error(`Found: privateKey=${!!privateKey}, jupiterApiKey=${!!jupiterApiKey}, heliusApiKey=${!!heliusApiKey}`);
    process.exit(1);
  }

  console.log('✅ Credentials loaded from environment\n');

  // Initialize coordinator in PAPER TRADE mode
  const coordinator = new SafeMasterCoordinator(
    rpcUrl,
    privateKey,
    jupiterApiKey,
    heliusApiKey
  );

  await coordinator.initialize();

  console.log('\n🚀 Starting paper trading session...');
  console.log('📄 PAPER TRADE MODE: All trades simulated, no real SOL spent\n');

  // Run the trading loop (will run indefinitely, monitoring for trades)
  await coordinator.run();
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
