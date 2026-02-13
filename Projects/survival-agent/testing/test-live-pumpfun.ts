/**
 * LIVE PUMP.FUN ROUTE TESTER
 *
 * Connects to PumpPortal WebSocket and tests Jupiter routes for incoming tokens
 * Shows real-time which tokens are tradeable via Jupiter
 */

import { PumpPortalWebSocket, PumpPortalTokenCreate } from '../strategies/pumpportal-websocket';
import { JupiterValidator } from '../core/jupiter-validator';

const TEST_AMOUNT_SOL = 0.04;
const TEST_DURATION_MINUTES = 5; // Listen for 5 minutes

async function main() {
  console.log('🧪 LIVE PUMP.FUN JUPITER ROUTE TESTER\n');
  console.log(`Will listen for ${TEST_DURATION_MINUTES} minutes and test each new token\n`);

  const ws = new PumpPortalWebSocket();
  const validator = new JupiterValidator();

  let tokensReceived = 0;
  let tokensWithRoutes = 0;

  // Connect and subscribe
  await ws.connect();
  ws.subscribeNewTokens();

  console.log('🔌 Connected to PumpPortal WebSocket');
  console.log('👂 Listening for new Pump.fun token launches...\n');

  // Handle new tokens
  ws.onTokenCreate(async (token: PumpPortalTokenCreate) => {
    tokensReceived++;

    console.log(`\n📦 Token #${tokensReceived}: ${token.symbol}`);
    console.log(`   Address: ${token.mint}`);
    console.log(`   Name: ${token.name}`);
    console.log(`   Initial Buy: ${token.initialBuy} SOL`);
    console.log(`   Market Cap: $${token.marketCapSol} SOL`);

    // Wait a few seconds for potential liquidity to appear
    console.log(`   ⏳ Waiting 5 seconds for liquidity...`);
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Test Jupiter route
    console.log(`   🧪 Testing Jupiter route...`);
    const validation = await validator.validateBuyRoute(token.mint, TEST_AMOUNT_SOL);

    if (validation.valid) {
      tokensWithRoutes++;
      console.log(`   ✅ TRADEABLE via Jupiter!`);
      console.log(`   💰 Price: $${validation.priceUsd?.toFixed(8)}`);
      console.log(`   📊 Slippage: ${(validation.slippageBps! / 100).toFixed(2)}%`);
    } else {
      console.log(`   ❌ NOT tradeable - ${validation.error}`);
    }

    console.log(`\n📈 Summary: ${tokensWithRoutes}/${tokensReceived} tokens tradeable`);
  });

  // Run for specified duration
  await new Promise(resolve => setTimeout(resolve, TEST_DURATION_MINUTES * 60 * 1000));

  console.log('\n\n🏁 TEST COMPLETE');
  console.log(`   Tokens received: ${tokensReceived}`);
  console.log(`   Tradeable via Jupiter: ${tokensWithRoutes}`);
  console.log(`   Success rate: ${tokensReceived > 0 ? ((tokensWithRoutes / tokensReceived) * 100).toFixed(1) : 0}%`);

  process.exit(0);
}

main().catch(error => {
  console.error('Test failed:', error);
  process.exit(1);
});
