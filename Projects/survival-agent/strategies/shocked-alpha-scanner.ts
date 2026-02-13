/**
 * SHOCKED ALPHA SCANNER
 *
 * Monitors tokens called in the Shocked trading group
 * Custom scoring and entry logic for group alpha
 */

import { JupiterValidator } from '../core/jupiter-validator';

export interface ShockedCall {
  address: string;
  symbol?: string;
  addedAt: number;
  source: string; // Who called it or context
  notes?: string; // Any specific instructions
  priority: 'high' | 'medium' | 'low';
}

export interface ShockedOpportunity {
  address: string;
  symbol: string;
  source: string;
  score: number;
  momentum: {
    priceChange5m: number;
    priceChange1h: number;
    volume1h: number;
    buyPressure: number;
  };
  isCallActive: boolean; // Within 24h of call
  priority: 'high' | 'medium' | 'low';
}

export class ShockedAlphaScanner {
  private validator: JupiterValidator;
  private watchlist: Map<string, ShockedCall> = new Map();
  private readonly WATCHLIST_FILE = '/tmp/shocked-watchlist.json';

  constructor() {
    this.validator = new JupiterValidator();
  }

  async initialize() {
    await this.loadWatchlist();
    console.log(`📡 Shocked Alpha Scanner initialized`);
    console.log(`👀 Watching ${this.watchlist.size} group calls`);
  }

  /**
   * Add a token call from the group
   */
  async addCall(
    address: string,
    options: {
      symbol?: string;
      source?: string;
      notes?: string;
      priority?: 'high' | 'medium' | 'low';
    } = {}
  ) {
    const call: ShockedCall = {
      address,
      symbol: options.symbol,
      addedAt: Date.now(),
      source: options.source || 'shocked-group',
      notes: options.notes,
      priority: options.priority || 'medium'
    };

    this.watchlist.set(address, call);
    await this.saveWatchlist();

    console.log(`✅ Added to Shocked watchlist: ${options.symbol || address.slice(0, 8)}`);
    console.log(`   Priority: ${call.priority} | Source: ${call.source}`);
  }

  /**
   * Remove old calls (older than 7 days)
   */
  async cleanupOldCalls() {
    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    let removed = 0;

    for (const [address, call] of this.watchlist) {
      if (call.addedAt < sevenDaysAgo) {
        this.watchlist.delete(address);
        removed++;
      }
    }

    if (removed > 0) {
      await this.saveWatchlist();
      console.log(`🧹 Cleaned up ${removed} old calls`);
    }
  }

  /**
   * Scan for opportunities from the watchlist
   */
  async scan(): Promise<ShockedOpportunity[]> {
    const opportunities: ShockedOpportunity[] = [];

    for (const [address, call] of this.watchlist) {
      try {
        const opp = await this.evaluateCall(address, call);
        if (opp) {
          opportunities.push(opp);
        }
      } catch (error) {
        // Silent fail on individual tokens
      }
    }

    return opportunities.sort((a, b) => b.score - a.score);
  }

  /**
   * Evaluate a specific call for entry
   */
  private async evaluateCall(
    address: string,
    call: ShockedCall
  ): Promise<ShockedOpportunity | null> {
    // Check if token is still tradeable
    const price = await this.validator.getRealExecutablePrice(address, 'buy', 0.04);
    if (!price) return null;

    // Fetch basic momentum data
    const momentum = await this.getMomentum(address);
    if (!momentum) return null;

    // Score the opportunity
    const score = this.calculateScore(call, momentum);

    // Check if call is still fresh (within 24 hours)
    const isCallActive = (Date.now() - call.addedAt) < (24 * 60 * 60 * 1000);

    return {
      address,
      symbol: call.symbol || 'UNKNOWN',
      source: call.source,
      score,
      momentum,
      isCallActive,
      priority: call.priority
    };
  }

  /**
   * Calculate momentum metrics
   */
  private async getMomentum(address: string): Promise<{
    priceChange5m: number;
    priceChange1h: number;
    volume1h: number;
    buyPressure: number;
  } | null> {
    try {
      // Fetch from DexScreener (simplified - expand with actual API)
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
      const data = await response.json();

      if (!data.pairs || data.pairs.length === 0) return null;

      const pair = data.pairs[0];

      return {
        priceChange5m: parseFloat(pair.priceChange?.m5 || '0'),
        priceChange1h: parseFloat(pair.priceChange?.h1 || '0'),
        volume1h: parseFloat(pair.volume?.h1 || '0'),
        buyPressure: this.estimateBuyPressure(pair)
      };
    } catch {
      return null;
    }
  }

  /**
   * Estimate buy pressure from pair data
   */
  private estimateBuyPressure(pair: any): number {
    // Simple heuristic: positive price change + high volume = higher buy pressure
    const priceChange = parseFloat(pair.priceChange?.m5 || '0');
    const volume = parseFloat(pair.volume?.m5 || '0');

    let pressure = 0;
    if (priceChange > 0) pressure += Math.min(priceChange, 50);
    if (volume > 10000) pressure += 20;
    if (volume > 50000) pressure += 30;

    return Math.min(pressure, 100);
  }

  /**
   * Calculate opportunity score
   */
  private calculateScore(call: ShockedCall, momentum: any): number {
    let score = 0;

    // Priority bonus (high priority calls get boost)
    if (call.priority === 'high') score += 30;
    if (call.priority === 'medium') score += 15;

    // Freshness bonus (time since added to watchlist)
    const ageHours = (Date.now() - call.addedAt) / (1000 * 60 * 60);
    if (ageHours < 2) score += 25;
    else if (ageHours < 6) score += 15;
    else if (ageHours < 24) score += 5;

    // Momentum bonus - prioritize recent price action (5m > 1h for freshness)
    // Use 5m momentum for calls added within last hour (likely caught mid-pump)
    const priceChange = ageHours < 1
      ? parseFloat(momentum.priceChange5m || momentum.priceChange1h || 0)
      : parseFloat(momentum.priceChange1h || 0);

    if (priceChange > 0) {
      score += Math.min(priceChange / 2, 30); // Up to +30 for strong momentum
    }

    // Volume bonus (active trading)
    if (momentum.volume1h > 50000) score += 15;
    if (momentum.volume1h > 200000) score += 10; // Extra for very high volume

    // Buy pressure bonus (bullish sentiment)
    if (momentum.buyPressure > 60) score += 20;
    if (momentum.buyPressure > 80) score += 10; // Extra for very strong buying

    return Math.round(score);
  }

  /**
   * Get current watchlist
   */
  getWatchlist(): ShockedCall[] {
    return Array.from(this.watchlist.values());
  }

  /**
   * Save watchlist to disk
   */
  private async saveWatchlist() {
    const data = Array.from(this.watchlist.entries());
    await Bun.write(this.WATCHLIST_FILE, JSON.stringify(data, null, 2));
  }

  /**
   * Load watchlist from disk
   */
  private async loadWatchlist() {
    try {
      const content = await Bun.file(this.WATCHLIST_FILE).text();
      const data = JSON.parse(content);
      this.watchlist = new Map(data);
    } catch {
      this.watchlist = new Map();
    }
  }
}
