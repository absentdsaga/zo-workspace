/**
 * SMART MONEY TRACKER
 *
 * Tracks whale wallet activity and institutional interest
 * Provides confidence scoring for trade decisions
 */

interface SmartMoneySignal {
  interested: boolean;
  confidence: number; // 0-100
  reasons: string[];
}

class SmartMoneyTracker {
  constructor() {
    console.log('💰 Smart Money Tracker initialized');
  }

  /**
   * Check if smart money is interested in a token
   * Uses DexScreener data as proxy for whale activity
   */
  async hasSmartMoneyInterest(tokenAddress: string): Promise<SmartMoneySignal> {
    try {
      // Get token data from DexScreener
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);

      if (!response.ok) {
        return {
          interested: false,
          confidence: 0,
          reasons: ['Unable to fetch token data']
        };
      }

      const data = await response.json();
      const pairs = data.pairs || [];

      if (pairs.length === 0) {
        return {
          interested: false,
          confidence: 0,
          reasons: ['No trading pairs found']
        };
      }

      // Use highest liquidity pair
      const pair = pairs[0];

      const reasons: string[] = [];
      let confidence = 0;

      // Signal 1: High volume (25 points)
      const volume24h = pair.volume?.h24 || 0;
      const volume1h = pair.volume?.h1 || 0;

      if (volume1h > 100000) {
        reasons.push(`High 1h volume: $${(volume1h / 1000).toFixed(0)}k`);
        confidence += 25;
      } else if (volume1h > 50000) {
        reasons.push(`Good 1h volume: $${(volume1h / 1000).toFixed(0)}k`);
        confidence += 15;
      }

      // Signal 2: Buy pressure (20 points)
      const txns24h = pair.txns?.h24 || {};
      const buys = txns24h.buys || 0;
      const sells = txns24h.sells || 0;
      const buyRatio = buys / (buys + sells || 1);

      if (buyRatio > 0.6 && buys > 50) {
        reasons.push(`Strong buy pressure: ${(buyRatio * 100).toFixed(0)}% buys`);
        confidence += 20;
      } else if (buyRatio > 0.5 && buys > 20) {
        reasons.push(`Moderate buy pressure: ${(buyRatio * 100).toFixed(0)}% buys`);
        confidence += 10;
      }

      // Signal 3: Price momentum (25 points)
      const priceChange1h = pair.priceChange?.h1 || 0;
      const priceChange5m = pair.priceChange?.m5 || 0;

      if (priceChange1h > 50) {
        reasons.push(`Explosive momentum: +${priceChange1h.toFixed(0)}% in 1h`);
        confidence += 25;
      } else if (priceChange1h > 20) {
        reasons.push(`Good momentum: +${priceChange1h.toFixed(0)}% in 1h`);
        confidence += 15;
      }

      // Signal 4: Liquidity strength (20 points)
      const liquidity = pair.liquidity?.usd || 0;

      if (liquidity > 100000) {
        reasons.push(`Strong liquidity: $${(liquidity / 1000).toFixed(0)}k`);
        confidence += 20;
      } else if (liquidity > 50000) {
        reasons.push(`Good liquidity: $${(liquidity / 1000).toFixed(0)}k`);
        confidence += 10;
      }

      // Signal 5: Market cap sweet spot (10 points)
      const marketCap = pair.marketCap || 0;

      if (marketCap >= 50000 && marketCap <= 1000000) {
        reasons.push(`Ideal MC: $${(marketCap / 1000).toFixed(0)}k`);
        confidence += 10;
      }

      // Determine if interested (confidence >= 50)
      const interested = confidence >= 50;

      if (!interested && reasons.length === 0) {
        reasons.push('No strong smart money signals detected');
      }

      return {
        interested,
        confidence: Math.min(100, confidence),
        reasons
      };

    } catch (error: any) {
      return {
        interested: false,
        confidence: 0,
        reasons: [`Error analyzing token: ${error.message}`]
      };
    }
  }

  /**
   * Get detailed metrics for a token
   */
  async getMetrics(tokenAddress: string): Promise<any> {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      const pairs = data.pairs || [];

      if (pairs.length === 0) {
        return null;
      }

      const pair = pairs[0];

      return {
        address: tokenAddress,
        symbol: pair.baseToken?.symbol || 'UNKNOWN',
        priceUSD: parseFloat(pair.priceUsd || '0'),
        marketCap: pair.marketCap || 0,
        liquidity: pair.liquidity?.usd || 0,
        volume24h: pair.volume?.h24 || 0,
        volume1h: pair.volume?.h1 || 0,
        priceChange1h: pair.priceChange?.h1 || 0,
        priceChange24h: pair.priceChange?.h24 || 0,
        txns24h: pair.txns?.h24 || {},
        pairAddress: pair.pairAddress,
        dexId: pair.dexId
      };

    } catch (error) {
      return null;
    }
  }
}

// CLI usage
async function main() {
  const tracker = new SmartMoneyTracker();

  // Example: Check a known token (BONK)
  const tokenAddress = 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263';

  console.log('💰 Checking smart money interest...\n');

  const signal = await tracker.hasSmartMoneyInterest(tokenAddress);

  console.log(`Token: ${tokenAddress.substring(0, 8)}...`);
  console.log(`Interested: ${signal.interested ? '✅ YES' : '❌ NO'}`);
  console.log(`Confidence: ${signal.confidence}/100`);
  console.log(`\nReasons:`);
  for (const reason of signal.reasons) {
    console.log(`  • ${reason}`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { SmartMoneyTracker, SmartMoneySignal };
