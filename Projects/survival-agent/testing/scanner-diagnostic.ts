/**
 * SCANNER DIAGNOSTIC
 *
 * Shows why tokens are passing or failing the scanner filters
 * Helps understand what's blocking opportunities
 */

import { SafeLiquidityScanner } from '../strategies/safe-liquidity-scanner';

async function main() {
  console.log('🔍 SCANNER DIAGNOSTIC\n');

  const jupiterApiKey = process.env.JUP_TOKEN;
  if (!jupiterApiKey) {
    console.error('Missing JUP_TOKEN');
    process.exit(1);
  }

  const scanner = new SafeLiquidityScanner(jupiterApiKey);

  // Get trending tokens from DexScreener
  console.log('Fetching latest tokens from DexScreener...\n');

  const profilesResp = await fetch('https://api.dexscreener.com/token-profiles/latest/v1');
  const profiles = await profilesResp.json();

  const boostedResp = await fetch('https://api.dexscreener.com/token-boosts/latest/v1');
  const boosted = boostedResp.ok ? await boostedResp.json() : [];

  const allAddresses = [
    ...profiles.slice(0, 10).map((p: any) => p.tokenAddress),
    ...boosted.slice(0, 10).map((b: any) => b.tokenAddress)
  ];

  console.log(`Analyzing ${allAddresses.length} tokens...\n`);
  console.log('='.repeat(80));

  for (const address of allAddresses.slice(0, 10)) {
    try {
      // Get pair data
      const pairResponse = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
      if (!pairResponse.ok) {
        console.log(`\n❌ ${address.substring(0, 8)}... - API error`);
        continue;
      }

      const data = await pairResponse.json();
      const pairs = data.pairs || [];
      if (pairs.length === 0) {
        console.log(`\n❌ ${address.substring(0, 8)}... - No pairs`);
        continue;
      }

      const pair = pairs.sort((a: any, b: any) =>
        (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
      )[0];

      const symbol = pair.baseToken?.symbol || 'UNKNOWN';
      const liquidityUSD = pair.liquidity?.usd || 0;
      const volume24h = pair.volume?.h24 || 0;
      const priceChange1h = pair.priceChange?.h1 || 0;
      const createdAt = pair.pairCreatedAt || 0;
      const ageMinutes = createdAt > 0 ? (Date.now() - createdAt) / 60000 : 999;

      console.log(`\n📊 ${symbol} (${address.substring(0, 8)}...)`);
      console.log(`   Liquidity: $${(liquidityUSD / 1000).toFixed(1)}k ${liquidityUSD >= 5000 ? '✅' : '❌ FAIL (min $5k)'}`);
      console.log(`   Volume 24h: $${(volume24h / 1000).toFixed(1)}k ${volume24h >= 10000 ? '✅' : '❌ FAIL (min $10k)'}`);
      console.log(`   Age: ${ageMinutes.toFixed(0)} min ${ageMinutes >= 0 && ageMinutes <= 60 ? '✅' : '❌ FAIL (need 0-60 min)'}`);
      console.log(`   1h Change: ${priceChange1h >= 0 ? '+' : ''}${priceChange1h.toFixed(1)}%`);

      // Check if would pass
      const passes =
        liquidityUSD >= 5000 &&
        volume24h >= 10000 &&
        ageMinutes >= 0 &&
        ageMinutes <= 60;

      if (passes) {
        console.log(`   ✅ WOULD PASS scanner (before Helius checks)`);
      } else {
        console.log(`   ❌ FAILS scanner filters`);
      }

    } catch (error: any) {
      console.log(`\n❌ ${address.substring(0, 8)}... - Error: ${error.message}`);
    }
  }

  console.log('\n' + '='.repeat(80));
  console.log('\n💡 Summary:');
  console.log('   - Most tokens fail due to: Low liquidity, Low volume, or Wrong age');
  console.log('   - 0-60 min age requirement is VERY strict (eliminates most tokens)');
  console.log('   - Even if they pass scanner, Helius holder check (75%) can still block');
  console.log('   - This is WORKING AS DESIGNED - being selective protects capital\n');
}

main().catch(console.error);
