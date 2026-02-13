/**
 * TEST JUPITER API CONNECTIVITY
 *
 * Tests with known tradeable tokens to verify API is working
 */

import { JupiterValidator } from '../core/jupiter-validator';

const TEST_AMOUNT = 0.04; // 0.04 SOL

// Well-known tokens that should have Jupiter routes
const KNOWN_TOKENS = [
  { symbol: 'USDC', address: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v' },
  { symbol: 'BONK', address: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263' },
  { symbol: 'WIF', address: 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm' },
];

async function main() {
  console.log('🧪 JUPITER API CONNECTIVITY TEST\n');

  const validator = new JupiterValidator();

  for (const token of KNOWN_TOKENS) {
    console.log(`\n📦 Testing ${token.symbol}`);
    console.log(`   Address: ${token.address}`);

    try {
      const validation = await validator.validateBuyRoute(token.address, TEST_AMOUNT);

      if (validation.valid) {
        console.log(`   ✅ Route found!`);
        console.log(`   💰 Price: $${validation.priceUsd?.toFixed(6)}`);
        console.log(`   📊 Slippage: ${(validation.slippageBps! / 100).toFixed(2)}%`);
      } else {
        console.log(`   ❌ Route failed: ${validation.error}`);
      }
    } catch (error: any) {
      console.log(`   💥 Error: ${error.message}`);
    }
  }

  console.log('\n\n🏁 TEST COMPLETE');
}

main().catch(error => {
  console.error('Test failed:', error);
  process.exit(1);
});
