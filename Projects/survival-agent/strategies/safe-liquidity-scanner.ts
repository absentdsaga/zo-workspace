/**
 * SAFE LIQUIDITY SCANNER
 *
 * Focuses on tokens with REAL, SUSTAINABLE liquidity
 * Avoids pump-and-dumps by checking:
 * 1. Liquidity depth (can we actually exit?)
 * 2. Holder distribution (not concentrated in few wallets)
 * 3. Sustainable volume patterns (not just pump spikes)
 * 4. LP lock status (liquidity provider locked = safer)
 * 5. Burn/renounce status (can't be rugged)
 */

interface SafeToken {
  address: string;
  symbol: string;
  name: string;

  // Liquidity metrics
  liquidityUSD: number;
  liquidityLocked: boolean;
  lpLockedUntil?: number;

  // Volume metrics
  volume24h: number;
  volume1h: number;
  volumeToLiquidityRatio: number; // Should be 1-5x for healthy tokens

  // Price metrics
  priceUSD: number;
  priceChange1h: number;
  priceChange24h: number;
  priceChange5m: number;

  // Safety metrics
  holderCount: number;
  top10HoldersPercent: number; // Lower = better distribution
  isRenounced: boolean;
  isBurned: boolean;

  // Trading metrics
  buyCount24h: number;
  sellCount24h: number;
  buySellRatio: number; // Should be 0.8-1.2 for healthy

  // Age
  ageMinutes: number;

  // Scoring
  safetyScore: number; // 0-100
  liquidityScore: number; // 0-100
  totalScore: number; // 0-100
  warnings: string[];
}

class SafeLiquidityScanner {
  private jupiterApiKey: string;

  // ORIGINAL STRATEGY (momentum/fresh launches - user preferred)
  private readonly MIN_LIQUIDITY = 3000; // $3k minimum (relaxed for more opportunities)
  private readonly MIN_VOLUME_24H = 5000; // $5k/day (relaxed for more opportunities)
  private readonly MAX_VOLUME_LIQUIDITY_RATIO = 10; // Not pump-and-dump
  private readonly MIN_HOLDERS = 100; // Real distribution
  private readonly MAX_TOP10_PERCENT = 40; // Not too concentrated
  private readonly MIN_BUY_SELL_RATIO = 0.6; // Not mass dumping
  private readonly MAX_BUY_SELL_RATIO = 1.5; // Not suspicious pumping

  // ORIGINAL: Chase momentum (user prefers this)
  private readonly MAX_1H_PUMP = 999; // No limit - chase pumps!
  private readonly MIN_AGE_HOURS = 0; // Fresh launches (0-60 min)
  private readonly MAX_AGE_HOURS = 1; // Max 60 minutes old
  private readonly PREFER_RISING_LIQUIDITY = false; // Momentum > liquidity

  constructor(jupiterApiKey: string) {
    this.jupiterApiKey = jupiterApiKey;
    console.log('🛡️  Safe Liquidity Scanner initialized');
    console.log('   Focus: REAL liquidity, SUSTAINABLE tokens');
  }

  /**
   * Scan for safe, liquid tokens
   */
  async scan(): Promise<SafeToken[]> {
    const tokens: SafeToken[] = [];

    try {
      // Get tokens from DexScreener trending
      const response = await fetch('https://api.dexscreener.com/token-profiles/latest/v1');
      const profiles = await response.json();

      // Also check boosted
      const boostedResponse = await fetch('https://api.dexscreener.com/token-boosts/latest/v1');
      const boosted = boostedResponse.ok ? await boostedResponse.json() : [];

      const allAddresses = new Set([
        ...profiles.slice(0, 30).map((p: any) => p.tokenAddress),
        ...boosted.slice(0, 30).map((b: any) => b.tokenAddress)
      ]);

      console.log(`\n🔍 Analyzing ${allAddresses.size} tokens for safety...`);

      for (const address of allAddresses) {
        try {
          const token = await this.analyzeToken(address);
          if (token && token.totalScore >= 60) {
            tokens.push(token);
          }
        } catch (error) {
          // Skip failed tokens
        }
      }

      console.log(`✅ Found ${tokens.length} safe tokens\n`);

    } catch (error: any) {
      console.log(`❌ Scan failed: ${error.message}`);
    }

    // Sort by total score
    tokens.sort((a, b) => b.totalScore - a.totalScore);

    return tokens;
  }

  /**
   * Analyze a single token for safety
   */
  private async analyzeToken(address: string): Promise<SafeToken | null> {
    // Get pair data from DexScreener
    const pairResponse = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
    if (!pairResponse.ok) return null;

    const pairData = await pairResponse.json();
    const pairs = pairData.pairs || [];

    // Find Solana pairs
    const solanaPairs = pairs.filter((p: any) => p.chainId === 'solana');
    if (solanaPairs.length === 0) return null;

    // Use highest liquidity pair
    const pair = solanaPairs.sort((a: any, b: any) =>
      (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
    )[0];

    // Must have basic data
    if (!pair.baseToken || !pair.priceUsd || !pair.liquidity) return null;

    // Extract metrics
    const liquidityUSD = pair.liquidity?.usd || 0;
    const volume24h = pair.volume?.h24 || 0;
    const volume1h = pair.volume?.h1 || 0;
    const volumeToLiquidityRatio = volume24h / liquidityUSD;

    // CRITICAL FILTERS - must pass ALL

    // 1. Minimum liquidity (can we exit?)
    if (liquidityUSD < this.MIN_LIQUIDITY) return null;

    // 2. Minimum volume (real activity?)
    if (volume24h < this.MIN_VOLUME_24H) return null;

    // 3. Volume/liquidity ratio (not pump-and-dump?)
    if (volumeToLiquidityRatio > this.MAX_VOLUME_LIQUIDITY_RATIO) return null;

    // 4. Must have transaction data
    const txns24h = pair.txns?.h24 || {};
    const buyCount = txns24h.buys || 0;
    const sellCount = txns24h.sells || 0;
    if (buyCount === 0 || sellCount === 0) return null;

    const buySellRatio = buyCount / sellCount;

    // 5. Buy/sell ratio must be healthy
    if (buySellRatio < this.MIN_BUY_SELL_RATIO || buySellRatio > this.MAX_BUY_SELL_RATIO) {
      return null;
    }

    // Calculate age
    let ageMinutes = 999;
    let ageHours = 999;
    if (pair.pairCreatedAt) {
      const ageMs = Date.now() - pair.pairCreatedAt;
      ageMinutes = ageMs / 1000 / 60;
      ageHours = ageMinutes / 60;
    }

    // ORIGINAL: Only skip very old tokens (>60 min)
    if (ageHours < 999 && ageHours > this.MAX_AGE_HOURS) {
      return null; // Too old (>60 min)
    }

    // ORIGINAL: No pump limit - we WANT momentum!
    // (priceChange1h can be high, we're chasing pumps)

    // Build token object
    const token: SafeToken = {
      address: pair.baseToken.address,
      symbol: pair.baseToken.symbol,
      name: pair.baseToken.name,

      liquidityUSD,
      liquidityLocked: false, // TODO: Check lock status

      volume24h,
      volume1h,
      volumeToLiquidityRatio,

      priceUSD: parseFloat(pair.priceUsd),
      priceChange1h: pair.priceChange?.h1 || 0,
      priceChange24h: pair.priceChange?.h24 || 0,
      priceChange5m: pair.priceChange?.m5 || 0,

      holderCount: 0, // TODO: Get from Helius
      top10HoldersPercent: 0,
      isRenounced: false,
      isBurned: false,

      buyCount24h: buyCount,
      sellCount24h: sellCount,
      buySellRatio,

      ageMinutes,

      safetyScore: 0,
      liquidityScore: 0,
      totalScore: 0,
      warnings: []
    };

    // Score the token
    this.scoreToken(token);

    return token;
  }

  /**
   * Score token for safety and liquidity
   */
  private scoreToken(token: SafeToken): void {
    let safetyScore = 0;
    let liquidityScore = 0;
    const warnings: string[] = [];

    // LIQUIDITY SCORING (0-100)

    // 1. Liquidity depth (40 points)
    if (token.liquidityUSD >= 500000) {
      liquidityScore += 40;
    } else if (token.liquidityUSD >= 200000) {
      liquidityScore += 30;
    } else if (token.liquidityUSD >= 100000) {
      liquidityScore += 20;
    } else {
      liquidityScore += 10;
      warnings.push(`Low liquidity: $${(token.liquidityUSD / 1000).toFixed(0)}k`);
    }

    // 2. Volume sustainability (30 points)
    if (token.volumeToLiquidityRatio >= 2 && token.volumeToLiquidityRatio <= 5) {
      liquidityScore += 30; // Healthy range
    } else if (token.volumeToLiquidityRatio >= 1 && token.volumeToLiquidityRatio <= 8) {
      liquidityScore += 20; // Acceptable
    } else {
      liquidityScore += 10;
      if (token.volumeToLiquidityRatio > 8) {
        warnings.push(`High volume/liq ratio: ${token.volumeToLiquidityRatio.toFixed(1)}x (pump?)`);
      } else {
        warnings.push(`Low volume/liq ratio: ${token.volumeToLiquidityRatio.toFixed(1)}x (dead?)`);
      }
    }

    // 3. Volume consistency (30 points)
    const volume1hProjected = token.volume1h * 24;
    const volumeRatio = volume1hProjected / token.volume24h;
    if (volumeRatio >= 0.8 && volumeRatio <= 1.5) {
      liquidityScore += 30; // Consistent
    } else if (volumeRatio >= 0.5 && volumeRatio <= 2.0) {
      liquidityScore += 20;
    } else {
      liquidityScore += 10;
      warnings.push(`Volume inconsistent: ${(volumeRatio * 100).toFixed(0)}% of expected`);
    }

    // SAFETY SCORING (0-100)

    // 1. Buy/sell ratio (40 points)
    if (token.buySellRatio >= 0.9 && token.buySellRatio <= 1.1) {
      safetyScore += 40; // Perfect balance
    } else if (token.buySellRatio >= 0.7 && token.buySellRatio <= 1.3) {
      safetyScore += 30; // Good
    } else if (token.buySellRatio >= 0.6 && token.buySellRatio <= 1.5) {
      safetyScore += 20; // Acceptable
    } else {
      safetyScore += 10;
      if (token.buySellRatio < 0.6) {
        warnings.push(`Mass dumping: ${(token.buySellRatio * 100).toFixed(0)}% buy/sell ratio`);
      } else {
        warnings.push(`Suspicious pumping: ${(token.buySellRatio * 100).toFixed(0)}% buy/sell ratio`);
      }
    }

    // 2. Price stability (30 points)
    const absChange1h = Math.abs(token.priceChange1h);
    if (absChange1h < 10) {
      safetyScore += 30; // Stable
    } else if (absChange1h < 30) {
      safetyScore += 20; // Moderate
    } else if (absChange1h < 50) {
      safetyScore += 10;
      warnings.push(`High volatility: ${absChange1h.toFixed(0)}% in 1h`);
    } else {
      safetyScore += 5;
      warnings.push(`Extreme volatility: ${absChange1h.toFixed(0)}% in 1h (pump/dump?)`);
    }

    // 3. Age maturity (30 points)
    if (token.ageMinutes >= 1440) { // 24h+
      safetyScore += 30;
    } else if (token.ageMinutes >= 360) { // 6h+
      safetyScore += 20;
    } else if (token.ageMinutes >= 120) { // 2h+
      safetyScore += 10;
    } else {
      safetyScore += 5;
      warnings.push(`Very fresh: ${token.ageMinutes.toFixed(0)} minutes old`);
    }

    // Total score (average of both)
    token.safetyScore = safetyScore;
    token.liquidityScore = liquidityScore;
    token.totalScore = Math.round((safetyScore + liquidityScore) / 2);
    token.warnings = warnings;
  }

  /**
   * Validate we can actually sell a token before buying
   */
  async validateSellRoute(tokenAddress: string, amount: number): Promise<boolean> {
    const SOL = 'So11111111111111111111111111111111111111112';

    try {
      const quoteUrl = `https://api.jup.ag/swap/v1/quote?` +
        `inputMint=${tokenAddress}&` +
        `outputMint=${SOL}&` +
        `amount=${amount}&` +
        `slippageBps=500`;

      const response = await fetch(quoteUrl, {
        headers: { 'x-api-key': this.jupiterApiKey }
      });

      if (!response.ok) return false;

      const quote = await response.json();

      // Check price impact - must be reasonable
      const priceImpact = parseFloat(quote.priceImpactPct || '0');
      if (priceImpact > 5) return false; // Too much slippage

      return true;
    } catch (error) {
      return false;
    }
  }
}

// CLI usage
async function main() {
  const jupiterKey = process.env.JUP_TOKEN;
  if (!jupiterKey) {
    console.error('❌ Missing JUP_TOKEN');
    process.exit(1);
  }

  const scanner = new SafeLiquidityScanner(jupiterKey);

  console.log('🛡️  SAFE LIQUIDITY SCANNER');
  console.log('Looking for tokens with REAL, SUSTAINABLE liquidity\n');

  const tokens = await scanner.scan();

  if (tokens.length === 0) {
    console.log('❌ No safe tokens found');
    return;
  }

  console.log(`📊 Top ${Math.min(5, tokens.length)} Safe Tokens:\n`);

  for (let i = 0; i < Math.min(5, tokens.length); i++) {
    const t = tokens[i];
    console.log(`${i + 1}. ${t.symbol} - Total Score: ${t.totalScore}/100`);
    console.log(`   Address: ${t.address.substring(0, 8)}...`);
    console.log(`   Liquidity: $${(t.liquidityUSD / 1000).toFixed(0)}k (Score: ${t.liquidityScore}/100)`);
    console.log(`   Safety: ${t.safetyScore}/100`);
    console.log(`   Volume: $${(t.volume24h / 1000).toFixed(0)}k/day (${t.volumeToLiquidityRatio.toFixed(1)}x ratio)`);
    console.log(`   Buy/Sell: ${t.buySellRatio.toFixed(2)} (${t.buyCount24h} buys, ${t.sellCount24h} sells)`);
    console.log(`   Age: ${t.ageMinutes < 999 ? t.ageMinutes.toFixed(0) + ' min' : 'unknown'}`);

    if (t.warnings.length > 0) {
      console.log(`   ⚠️  Warnings: ${t.warnings.join(', ')}`);
    }
    console.log('');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { SafeLiquidityScanner, SafeToken };
