#!/usr/bin/env bun
/**
 * Test Pump.fun Cached Tokens for Jupiter Routes
 * 
 * Checks which cached Pump.fun tokens actually have Jupiter routes available
 * This will show us if any have graduated to Raydium and are tradeable
 */

import { JupiterValidator } from '../core/jupiter-validator';

const JUP_API_KEY = process.env.JUP_TOKEN;
const SOL_MINT = 'So11111111111111111111111111111111111111112';

interface TestResult {
  mint: string;
  symbol: string;
  ageMinutes: number;
  marketCapSol: number;
  hasJupiterRoute: boolean;
  buyPrice?: number;
  sellPrice?: number;
  slippage?: number;
  error?: string;
}

async function testPumpfunTokens() {
  console.log('🧪 Testing Pump.fun Cached Tokens for Jupiter Routes\n');
  console.log('This will show which tokens are actually TRADEABLE\n');
  console.log('='.repeat(70) + '\n');

  if (!JUP_API_KEY) {
    console.error('❌ Missing JUP_TOKEN environment variable');
    process.exit(1);
  }

  const validator = new JupiterValidator(JUP_API_KEY);

  // Get a list of recent Pump.fun tokens from the bot's log
  // For now, we'll test with some example addresses
  // In production, this would read from the scanner's cache
  
  const testTokens = await getRecentPumpfunTokens();

  if (testTokens.length === 0) {
    console.log('❌ No cached Pump.fun tokens found');
    console.log('   The bot needs to run for a few minutes to cache tokens\n');
    console.log('💡 Tip: Look for "🚀 Cached:" messages in the bot log\n');
    return;
  }

  console.log(`📊 Testing ${testTokens.length} cached Pump.fun tokens...\n`);

  const results: TestResult[] = [];

  for (let i = 0; i < testTokens.length; i++) {
    const token = testTokens[i];
    console.log(`[${i + 1}/${testTokens.length}] Testing ${token.symbol} (${token.mint.slice(0, 8)}...)`);
    console.log(`   Age: ${token.ageMinutes.toFixed(1)} min | MC: ${token.marketCapSol.toFixed(0)} SOL`);

    try {
      // Test with a small amount (0.01 SOL)
      const testAmount = 0.01;
      const roundTrip = await validator.validateRoundTrip(token.mint, testAmount);

      if (roundTrip.canBuy && roundTrip.canSell) {
        console.log(`   ✅ HAS JUPITER ROUTES - TRADEABLE!`);
        console.log(`      Buy: $${roundTrip.buyPrice?.toFixed(8)} | Sell: $${roundTrip.sellPrice?.toFixed(8)}`);
        console.log(`      Slippage: ${roundTrip.slippage?.toFixed(2)}%\n`);

        results.push({
          mint: token.mint,
          symbol: token.symbol,
          ageMinutes: token.ageMinutes,
          marketCapSol: token.marketCapSol,
          hasJupiterRoute: true,
          buyPrice: roundTrip.buyPrice,
          sellPrice: roundTrip.sellPrice,
          slippage: roundTrip.slippage
        });
      } else {
        console.log(`   ❌ No Jupiter routes yet`);
        console.log(`      ${roundTrip.error}\n`);

        results.push({
          mint: token.mint,
          symbol: token.symbol,
          ageMinutes: token.ageMinutes,
          marketCapSol: token.marketCapSol,
          hasJupiterRoute: false,
          error: roundTrip.error
        });
      }

    } catch (error: any) {
      console.log(`   ❌ Error: ${error.message}\n`);

      results.push({
        mint: token.mint,
        symbol: token.symbol,
        ageMinutes: token.ageMinutes,
        marketCapSol: token.marketCapSol,
        hasJupiterRoute: false,
        error: error.message
      });
    }

    // Rate limit
    if (i < testTokens.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  // Summary
  console.log('='.repeat(70));
  console.log('📊 SUMMARY\n');

  const tradeable = results.filter(r => r.hasJupiterRoute);
  const notTradeable = results.filter(r => !r.hasJupiterRoute);

  console.log(`✅ Tradeable (have Jupiter routes): ${tradeable.length}/${results.length}`);
  console.log(`❌ Not tradeable yet: ${notTradeable.length}/${results.length}\n`);

  if (tradeable.length > 0) {
    console.log('🎯 TRADEABLE TOKENS:\n');
    for (const token of tradeable) {
      console.log(`   ${token.symbol} (${token.mint.slice(0, 8)}...)`);
      console.log(`      Age: ${token.ageMinutes.toFixed(1)} min | MC: ${token.marketCapSol.toFixed(0)} SOL`);
      console.log(`      Price: $${token.buyPrice?.toFixed(8)} | Slippage: ${token.slippage?.toFixed(2)}%\n`);
    }
  }

  if (notTradeable.length > 0) {
    console.log('⏳ NOT TRADEABLE YET (too fresh / not graduated):\n');
    for (const token of notTradeable) {
      console.log(`   ${token.symbol} - Age: ${token.ageMinutes.toFixed(1)} min`);
    }
    console.log('\n💡 These tokens will become tradeable when they graduate to Raydium\n');
  }

  console.log('='.repeat(70) + '\n');
}

/**
 * Get recent Pump.fun tokens from bot log
 */
async function getRecentPumpfunTokens(): Promise<Array<{
  mint: string;
  symbol: string;
  ageMinutes: number;
  marketCapSol: number;
}>> {
  try {
    // Read the bot log and extract cached token info
    const logPath = '/tmp/paper-trade-fixed.log';
    const logContent = await Bun.file(logPath).text();
    const lines = logContent.split('\n');

    const tokens: Array<{
      mint: string;
      symbol: string;
      ageMinutes: number;
      marketCapSol: number;
    }> = [];

    const tokenMap = new Map<string, any>();

    // Parse "🚀 Cached:" lines
    // Format: 🚀 Cached: SYMBOL (MINT...) - XX.XX SOL initial
    for (const line of lines) {
      const cachedMatch = line.match(/🚀 Cached: (.+?) \(([A-Za-z0-9]+)\.\.\.\)/);
      if (cachedMatch) {
        const symbol = cachedMatch[1];
        const mintPrefix = cachedMatch[2];
        
        // Extract market cap if available
        const mcMatch = line.match(/Market cap: ([\d.]+) SOL/);
        const marketCapSol = mcMatch ? parseFloat(mcMatch[1]) : 30;

        // Estimate age (tokens in log are recent)
        const ageMinutes = 5; // Assume 5 min average

        // Store by prefix (we only have prefix from log)
        if (!tokenMap.has(mintPrefix)) {
          tokenMap.set(mintPrefix, {
            mint: mintPrefix, // Note: This is just prefix, full address needed
            symbol,
            ageMinutes,
            marketCapSol
          });
        }
      }
    }

    // If we found tokens in log, use them
    if (tokenMap.size > 0) {
      console.log(`⚠️  Found ${tokenMap.size} token prefixes in log`);
      console.log(`   Note: Need full addresses to test Jupiter routes\n`);
      console.log(`   Alternative: Testing with known recent Pump.fun graduates...\n`);
    }

    // For now, return empty - user should provide actual addresses
    // OR we could fetch from DexScreener recent Raydium listings
    return [];

  } catch (error) {
    console.log('⚠️  Could not read bot log, using fallback test tokens\n');
    return [];
  }
}

// Run
testPumpfunTokens().catch(console.error);
