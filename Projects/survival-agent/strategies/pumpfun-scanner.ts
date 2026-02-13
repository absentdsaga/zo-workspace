/**
 * PUMP.FUN SCANNER
 *
 * Scans Pump.fun (THE #1 Solana meme coin launchpad)
 * - 80% of meme coins launch here first
 * - Tracks bonding curve completion (graduation signal)
 * - Catches tokens BEFORE DexScreener indexes them
 * - Real-time fresh launch detection
 */

export interface PumpFunToken {
  // Basic info
  mint: string;
  name: string;
  symbol: string;
  description: string;
  image_uri: string;

  // Trading metrics
  usd_market_cap: number;
  market_cap: number; // In SOL
  virtual_sol_reserves: number;
  virtual_token_reserves: number;

  // Bonding curve status
  bonding_curve: string;
  associated_bonding_curve: string;
  complete: boolean; // Graduated to Raydium?

  // Age and activity
  created_timestamp: number;
  raydium_pool?: string; // Set when graduated

  // Social/viral signals
  king_of_the_hill_timestamp?: number; // Viral indicator
  is_currently_live?: boolean;

  // Replies (engagement metric)
  reply_count?: number;

  // Calculated fields
  ageMinutes?: number;
  ageSeconds?: number;
  isGraduating?: boolean; // Near 100% bonding curve
}

export interface PumpFunTrade {
  signature: string;
  mint: string;
  sol_amount: number;
  token_amount: number;
  is_buy: boolean;
  user: string;
  timestamp: number;
  virtual_sol_reserves: number;
  virtual_token_reserves: number;
}

class PumpFunScanner {
  private readonly BASE_URL = 'https://frontend-api.pump.fun';

  // Filters for fresh momentum plays
  private readonly MIN_AGE_SECONDS = 0;
  private readonly MAX_AGE_MINUTES = 60; // 0-60 min (fresh launches)
  private readonly MIN_MARKET_CAP_USD = 5000; // $5k minimum
  private readonly MIN_REPLIES = 0; // Any engagement

  constructor() {
    console.log('🚀 Pump.fun Scanner initialized');
    console.log('   Focus: Fresh launches, bonding curve graduation');
  }

  /**
   * Scan for latest launches on Pump.fun
   */
  async scanLatest(limit: number = 50): Promise<PumpFunToken[]> {
    try {
      const url = `${this.BASE_URL}/coins?limit=${limit}&offset=0&sort=created_timestamp&order=DESC&includeNsfw=false`;

      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Origin': 'https://pump.fun',
          'Referer': 'https://pump.fun/'
        }
      });

      if (!response.ok) {
        throw new Error(`Pump.fun API error: ${response.status}`);
      }

      const coins: PumpFunToken[] = await response.json();

      // Calculate age and filter
      const now = Date.now();
      const filtered = coins
        .map(coin => {
          const ageMs = now - coin.created_timestamp;
          coin.ageMinutes = ageMs / 60000;
          coin.ageSeconds = ageMs / 1000;

          // Check if near graduation (>80% bonding curve)
          // Bonding curve completes at certain market cap threshold
          coin.isGraduating = coin.usd_market_cap > 60000 && !coin.complete;

          return coin;
        })
        .filter(coin => {
          // Age filter (0-60 min)
          if (coin.ageMinutes! > this.MAX_AGE_MINUTES) return false;

          // Market cap filter
          if (coin.usd_market_cap < this.MIN_MARKET_CAP_USD) return false;

          // Must not be completed yet (we want to catch before graduation)
          // OR just graduated in last 10 min (catching the pump)
          if (coin.complete && coin.ageMinutes! > 10) return false;

          return true;
        });

      console.log(`   Pump.fun: ${filtered.length}/${coins.length} tokens passed filters`);

      return filtered;

    } catch (error: any) {
      console.log(`   ⚠️  Pump.fun scan failed: ${error.message}`);
      return [];
    }
  }

  /**
   * Get single token details
   */
  async getToken(mint: string): Promise<PumpFunToken | null> {
    try {
      const url = `${this.BASE_URL}/coins/${mint}`;

      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Origin': 'https://pump.fun',
          'Referer': 'https://pump.fun/'
        }
      });

      if (!response.ok) return null;

      const coin: PumpFunToken = await response.json();

      // Calculate age
      const ageMs = Date.now() - coin.created_timestamp;
      coin.ageMinutes = ageMs / 60000;
      coin.ageSeconds = ageMs / 1000;
      coin.isGraduating = coin.usd_market_cap > 60000 && !coin.complete;

      return coin;

    } catch (error) {
      return null;
    }
  }

  /**
   * Get recent trades for a token
   */
  async getTrades(mint: string, limit: number = 100): Promise<PumpFunTrade[]> {
    try {
      const url = `${this.BASE_URL}/trades/latest/${mint}?limit=${limit}`;

      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Origin': 'https://pump.fun',
          'Referer': 'https://pump.fun/'
        }
      });

      if (!response.ok) return [];

      const trades: PumpFunTrade[] = await response.json();
      return trades;

    } catch (error) {
      return [];
    }
  }

  /**
   * Calculate buy pressure from recent trades
   */
  async getBuyPressure(mint: string): Promise<{
    buyCount: number;
    sellCount: number;
    buySellRatio: number;
    buyVolume: number;
    sellVolume: number;
    netPressure: number;
  }> {
    const trades = await this.getTrades(mint, 50);

    if (trades.length === 0) {
      return {
        buyCount: 0,
        sellCount: 0,
        buySellRatio: 0,
        buyVolume: 0,
        sellVolume: 0,
        netPressure: 0
      };
    }

    const buyTrades = trades.filter(t => t.is_buy);
    const sellTrades = trades.filter(t => !t.is_buy);

    const buyVolume = buyTrades.reduce((sum, t) => sum + t.sol_amount, 0);
    const sellVolume = sellTrades.reduce((sum, t) => sum + t.sol_amount, 0);

    return {
      buyCount: buyTrades.length,
      sellCount: sellTrades.length,
      buySellRatio: sellTrades.length > 0 ? buyTrades.length / sellTrades.length : 999,
      buyVolume,
      sellVolume,
      netPressure: buyVolume - sellVolume
    };
  }

  /**
   * Check if token is about to graduate (viral signal)
   */
  async isAboutToGraduate(mint: string): Promise<boolean> {
    const token = await this.getToken(mint);
    if (!token) return false;

    // Graduation happens around $69k market cap
    // Check if close to graduation (>$60k but not graduated yet)
    return token.usd_market_cap > 60000 && !token.complete;
  }

  /**
   * Score a Pump.fun token for trading opportunity
   */
  scoreToken(token: PumpFunToken, buyPressure?: {
    buySellRatio: number;
    netPressure: number;
  }): number {
    let score = 0;

    // 1. Fresh age (30 points)
    if (token.ageMinutes! <= 5) {
      score += 30; // Super fresh
    } else if (token.ageMinutes! <= 15) {
      score += 25;
    } else if (token.ageMinutes! <= 30) {
      score += 20;
    } else if (token.ageMinutes! <= 60) {
      score += 15;
    }

    // 2. Market cap sweet spot (25 points)
    if (token.usd_market_cap >= 10000 && token.usd_market_cap <= 50000) {
      score += 25; // Perfect range for early entry
    } else if (token.usd_market_cap >= 5000 && token.usd_market_cap <= 10000) {
      score += 20; // Very early
    } else if (token.usd_market_cap >= 50000 && token.usd_market_cap <= 69000) {
      score += 15; // Near graduation
    }

    // 3. Bonding curve status (20 points)
    if (token.isGraduating) {
      score += 20; // About to graduate (viral signal!)
    } else if (token.complete && token.ageMinutes! <= 10) {
      score += 25; // Just graduated (momentum play!)
    } else if (!token.complete) {
      score += 10; // Still on bonding curve
    }

    // 4. Viral signals (15 points)
    if (token.king_of_the_hill_timestamp) {
      score += 15; // Was king of the hill
    }

    // 5. Engagement (10 points)
    if (token.reply_count && token.reply_count > 50) {
      score += 10;
    } else if (token.reply_count && token.reply_count > 20) {
      score += 7;
    } else if (token.reply_count && token.reply_count > 5) {
      score += 5;
    }

    // 6. Buy pressure (if provided) (10 points)
    if (buyPressure) {
      if (buyPressure.buySellRatio > 2) {
        score += 10; // Strong buying
      } else if (buyPressure.buySellRatio > 1.5) {
        score += 7;
      } else if (buyPressure.buySellRatio > 1) {
        score += 5;
      }
    }

    return Math.min(score, 100);
  }

  /**
   * Get top opportunities (scored and sorted)
   */
  async getTopOpportunities(limit: number = 10): Promise<Array<{
    token: PumpFunToken;
    score: number;
    buyPressure?: {
      buySellRatio: number;
      netPressure: number;
    };
  }>> {
    const tokens = await this.scanLatest(50);

    const scored = await Promise.all(
      tokens.map(async (token) => {
        // Get buy pressure for scoring
        const buyPressure = await this.getBuyPressure(token.mint);
        const score = this.scoreToken(token, buyPressure);

        return {
          token,
          score,
          buyPressure
        };
      })
    );

    // Sort by score (highest first)
    scored.sort((a, b) => b.score - a.score);

    return scored.slice(0, limit);
  }
}

export { PumpFunScanner };
