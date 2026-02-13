#!/usr/bin/env bun
/**
 * Test Recently Graduated Pump.fun Tokens
 * 
 * Finds tokens on DexScreener that:
 * 1. Are on Raydium (graduated from Pump.fun)
 * 2. Are very fresh (10-60 min old)
 * 3. Tests if they have Jupiter routes
 * 
 * This shows which graduated tokens are actually TRADEABLE
 */

import { JupiterValidator } from '../core/jupiter-validator';

const JUP_API_KEY = process.env.JUP_TOKEN;

interface GraduatedToken {
  address: string;
  symbol: string;
  name: string;
  ageMinutes: number;
  marketCapUsd: number;
  liquidityUsd: number;
  priceUsd: number;
  pairAddress: string;
}

async function findGraduatedTokens(): Promise<GraduatedToken[]> {
  console.log('🔍 Searching for recently graduated Pump.fun tokens on Raydium...\n');

  try {
    // Get fresh Raydium pairs from DexScreener
    const response = await fetch(
      'https://api.dexscreener.com/latest/dex/search/?q=SOL'
    );

    if (!response.ok) {
      throw new Error(`DexScreener API error: ${response.status}`);
    }

    const data = await response.json();
    const pairs = data.pairs || [];

    console.log(`📊 Fetched ${pairs.length} Solana pairs from DexScreener\n`);

    // Filter for fresh Raydium pairs
    const graduated: GraduatedToken[] = [];
    const now = Date.now();

    for (const pair of pairs) {
      // Must be on Raydium
      if (pair.dexId !== 'raydium') continue;

      // Calculate age
      const pairCreatedAt = new Date(pair.pairCreatedAt).getTime();
      const ageMs = now - pairCreatedAt;
      const ageMinutes = ageMs / 60000;

      // Only tokens 10-120 minutes old (likely recent Pump.fun graduates)
      if (ageMinutes < 10 || ageMinutes > 120) continue;

      // Must have decent liquidity
      const liquidityUsd = pair.liquidity?.usd || 0;
      if (liquidityUsd < 5000) continue;

      // Must have market cap data
      const marketCapUsd = pair.marketCap || 0;
      if (marketCapUsd < 10000) continue;

      graduated.push({
        address: pair.baseToken.address,
        symbol: pair.baseToken.symbol,
        name: pair.baseToken.name,
        ageMinutes,
        marketCapUsd,
        liquidityUsd,
        priceUsd: parseFloat(pair.priceUsd || '0'),
        pairAddress: pair.pairAddress
      });
    }

    // Sort by age (freshest first)
    graduated.sort((a, b) => a.ageMinutes - b.ageMinutes);

    return graduated.slice(0, 10); // Top 10 freshest

  } catch (error: any) {
    console.error(`❌ Error fetching graduated tokens: ${error.message}`);
    return [];
  }
}

async function testJupiterRoutes(tokens: GraduatedToken[]) {
  console.log(`\n🧪 Testing Jupiter routes for ${tokens.length} graduated tokens...\n`);
  console.log('='.repeat(80) + '\n');

  if (!JUP_API_KEY) {
    console.error('❌ Missing JUP_TOKEN environment variable');
    process.exit(1);
  }

  const validator = new JupiterValidator(JUP_API_KEY);
  const testAmount = 0.04; // 0.04 SOL (8% of 0.5 SOL bot balance)

  let tradeableCount = 0;
  let notTradeableCount = 0;

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    
    console.log(`[${i + 1}/${tokens.length}] ${token.symbol} (${token.address.slice(0, 8)}...)`);
    console.log(`   Age: ${token.ageMinutes.toFixed(1)} min`);
    console.log(`   MC: $${token.marketCapUsd.toLocaleString()} | Liq: $${token.liquidityUsd.toLocaleString()}`);
    console.log(`   DexScreener Price: $${token.priceUsd.toFixed(8)}`);

    try {
      const roundTrip = await validator.validateRoundTrip(token.address, testAmount);

      if (roundTrip.canBuy && roundTrip.canSell) {
        tradeableCount++;
        console.log(`   ✅ TRADEABLE - Has Jupiter routes!`);
        console.log(`      Buy price:  $${roundTrip.buyPrice?.toFixed(8)}`);
        console.log(`      Sell price: $${roundTrip.sellPrice?.toFixed(8)}`);
        console.log(`      Slippage:   ${roundTrip.slippage?.toFixed(2)}%`);
        
        // Compare to DexScreener price
        const priceDiff = roundTrip.buyPrice && token.priceUsd 
          ? ((roundTrip.buyPrice - token.priceUsd) / token.priceUsd) * 100
          : 0;
        console.log(`      Price diff: ${priceDiff >= 0 ? '+' : ''}${priceDiff.toFixed(2)}% vs DexScreener`);
        console.log(`   🎯 This token could be traded by the bot!\n`);
      } else {
        notTradeableCount++;
        console.log(`   ❌ NOT TRADEABLE`);
        if (!roundTrip.canBuy) {
          console.log(`      No buy route: ${roundTrip.error?.substring(0, 60)}`);
        }
        if (!roundTrip.canSell) {
          console.log(`      No sell route: ${roundTrip.error?.substring(0, 60)}`);
        }
        console.log();
      }

    } catch (error: any) {
      notTradeableCount++;
      console.log(`   ❌ Error: ${error.message}\n`);
    }

    // Rate limit
    if (i < tokens.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  // Summary
  console.log('='.repeat(80));
  console.log('📊 SUMMARY\n');
  console.log(`✅ Tradeable (bot can trade these): ${tradeableCount}/${tokens.length}`);
  console.log(`❌ Not tradeable: ${notTradeableCount}/${tokens.length}\n`);

  if (tradeableCount > 0) {
    console.log('🎯 CONCLUSION: Recently graduated Pump.fun tokens ARE tradeable!');
    console.log('   The bot should catch these when they appear in both sources.\n');
  } else {
    console.log('⚠️  CONCLUSION: None of these graduated tokens have Jupiter routes yet.');
    console.log('   They may need more time to establish liquidity.\n');
  }

  console.log('💡 TIP: The bot will automatically trade graduated tokens when:');
  console.log('   1. They show up on DexScreener (already happening)');
  console.log('   2. They pass the minimum score (≥40)');
  console.log('   3. Jupiter routes exist (validated before trading)');
  console.log('   4. Smart money confidence ≥35\n');
}

async function main() {
  console.log('🧪 GRADUATED PUMP.FUN TOKEN TESTER\n');
  console.log('This finds recently graduated tokens and tests if they\'re tradeable\n');
  
  const graduated = await findGraduatedTokens();

  if (graduated.length === 0) {
    console.log('❌ No recently graduated tokens found');
    console.log('   Try again in a few minutes\n');
    return;
  }

  console.log(`✅ Found ${graduated.length} recently graduated tokens (10-120 min old)`);
  
  await testJupiterRoutes(graduated);
}

main().catch(console.error);
