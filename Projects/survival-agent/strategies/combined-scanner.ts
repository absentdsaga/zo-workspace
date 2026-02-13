/**
 * COMBINED SCANNER
 * 
 * Scans BOTH Pump.fun AND DexScreener for maximum coverage:
 * - Pump.fun: Ultra-early catches (0-60 min, pre-DEX launches)
 * - DexScreener: Established tokens with proven liquidity
 * 
 * Combines results, deduplicates, and returns best opportunities
 */

import { PumpFunScanner, PumpFunToken } from './pumpfun-scanner';
import { MemeScanner } from './meme-scanner';

export interface CombinedOpportunity {
  address: string;
  symbol: string;
  name?: string;
  score: number;
  ageMinutes: number;
  signals: string[];
  source: 'pumpfun' | 'dexscreener' | 'both';
  
  // Metrics
  marketCapUsd?: number;
  liquidityUsd?: number;
  volume24h?: number;
  
  // Pump.fun specific
  isGraduating?: boolean;
  bondingCurveComplete?: boolean;
  buyPressure?: {
    buySellRatio: number;
    netPressure: number;
  };
  
  // DexScreener specific
  priceChange1h?: number;
  priceChange24h?: number;
  holders?: number;
}

export class CombinedScanner {
  private pumpfunScanner: PumpFunScanner;
  private dexScanner: MemeScanner;

  constructor() {
    this.pumpfunScanner = new PumpFunScanner();
    this.dexScanner = new MemeScanner();
    console.log('🔍 Combined Scanner initialized (Pump.fun + DexScreener)');
  }

  /**
   * Scan both sources and combine results
   */
  async scan(): Promise<CombinedOpportunity[]> {
    console.log('   🔍 Scanning Pump.fun + DexScreener...');

    // Scan both in parallel
    const [pumpfunResults, dexResults] = await Promise.all([
      this.scanPumpFun(),
      this.scanDexScreener()
    ]);

    console.log(`   Pump.fun: ${pumpfunResults.length} opportunities`);
    console.log(`   DexScreener: ${dexResults.length} opportunities`);

    // Combine and deduplicate
    const combined = this.combineAndDeduplicate(pumpfunResults, dexResults);

    // Sort by score
    combined.sort((a, b) => b.score - a.score);

    console.log(`   Combined: ${combined.length} unique opportunities`);

    return combined;
  }

  /**
   * Scan Pump.fun
   */
  private async scanPumpFun(): Promise<CombinedOpportunity[]> {
    try {
      const opportunities = await this.pumpfunScanner.getTopOpportunities(20);

      return opportunities.map(opp => {
        const signals: string[] = [];

        // Add signals based on Pump.fun metrics
        if (opp.token.isGraduating) {
          signals.push('Near graduation');
        }
        if (opp.token.complete) {
          signals.push('Just graduated');
        }
        if (opp.token.king_of_the_hill_timestamp) {
          signals.push('King of the hill');
        }
        if (opp.buyPressure && opp.buyPressure.buySellRatio > 2) {
          signals.push(`${opp.buyPressure.buySellRatio.toFixed(1)}x buy pressure`);
        }
        if (opp.token.ageMinutes! <= 5) {
          signals.push('Ultra fresh (<5 min)');
        }
        if (opp.token.reply_count && opp.token.reply_count > 50) {
          signals.push(`${opp.token.reply_count} replies`);
        }

        return {
          address: opp.token.mint,
          symbol: opp.token.symbol,
          name: opp.token.name,
          score: opp.score,
          ageMinutes: opp.token.ageMinutes!,
          signals,
          source: 'pumpfun' as const,
          marketCapUsd: opp.token.usd_market_cap,
          isGraduating: opp.token.isGraduating,
          bondingCurveComplete: opp.token.complete,
          buyPressure: opp.buyPressure
        };
      });

    } catch (error: any) {
      console.log(`   ⚠️  Pump.fun scan failed: ${error.message}`);
      return [];
    }
  }

  /**
   * Scan DexScreener
   */
  private async scanDexScreener(): Promise<CombinedOpportunity[]> {
    try {
      const opportunities = await this.dexScanner.scan();

      return opportunities.map(opp => ({
        address: opp.address,
        symbol: opp.symbol,
        name: opp.name,
        score: opp.score,
        ageMinutes: opp.ageMinutes,
        signals: opp.signals,
        source: 'dexscreener' as const,
        marketCapUsd: opp.marketCap,
        liquidityUsd: opp.liquidity,
        volume24h: opp.volume24h,
        priceChange1h: opp.priceChange1h,
        priceChange24h: opp.priceChange24h
      }));

    } catch (error: any) {
      console.log(`   ⚠️  DexScreener scan failed: ${error.message}`);
      return [];
    }
  }

  /**
   * Combine results and handle duplicates
   * If same token appears in both sources, merge data and boost score
   */
  private combineAndDeduplicate(
    pumpfun: CombinedOpportunity[],
    dex: CombinedOpportunity[]
  ): CombinedOpportunity[] {
    const addressMap = new Map<string, CombinedOpportunity>();

    // Add Pump.fun results
    for (const opp of pumpfun) {
      addressMap.set(opp.address, opp);
    }

    // Add or merge DexScreener results
    for (const opp of dex) {
      const existing = addressMap.get(opp.address);

      if (existing) {
        // Token found in BOTH sources - this is VERY bullish!
        // Merge data and boost score
        const merged: CombinedOpportunity = {
          ...existing,
          source: 'both',
          // Take max score and add 20 point bonus for being in both
          score: Math.min(Math.max(existing.score, opp.score) + 20, 100),
          // Merge signals
          signals: [...existing.signals, ...opp.signals, 'Found in both sources'],
          // Add DexScreener data if missing
          liquidityUsd: opp.liquidityUsd,
          volume24h: opp.volume24h,
          priceChange1h: opp.priceChange1h,
          priceChange24h: opp.priceChange24h
        };

        addressMap.set(opp.address, merged);
      } else {
        // Only in DexScreener
        addressMap.set(opp.address, opp);
      }
    }

    return Array.from(addressMap.values());
  }

  /**
   * Get source-specific stats for logging
   */
  getSourceStats(opportunities: CombinedOpportunity[]): {
    pumpfunOnly: number;
    dexOnly: number;
    both: number;
  } {
    return {
      pumpfunOnly: opportunities.filter(o => o.source === 'pumpfun').length,
      dexOnly: opportunities.filter(o => o.source === 'dexscreener').length,
      both: opportunities.filter(o => o.source === 'both').length
    };
  }
}

// CLI test
async function main() {
  console.log('🧪 Testing Combined Scanner\n');

  const scanner = new CombinedScanner();
  const opportunities = await scanner.scan();

  console.log(`\n📊 Found ${opportunities.length} total opportunities\n`);

  const stats = scanner.getSourceStats(opportunities);
  console.log('📈 Source breakdown:');
  console.log(`   Pump.fun only: ${stats.pumpfunOnly}`);
  console.log(`   DexScreener only: ${stats.dexOnly}`);
  console.log(`   Both sources: ${stats.both} ⭐ (boosted score)\n`);

  // Show top 10
  console.log('🏆 Top 10 opportunities:\n');
  for (let i = 0; i < Math.min(10, opportunities.length); i++) {
    const opp = opportunities[i];
    console.log(`${i + 1}. ${opp.symbol} (${opp.address.slice(0, 8)}...)`);
    console.log(`   Score: ${opp.score}/100`);
    console.log(`   Source: ${opp.source}`);
    console.log(`   Age: ${opp.ageMinutes.toFixed(1)} min`);
    console.log(`   MC: $${opp.marketCapUsd?.toLocaleString() || 'N/A'}`);
    console.log(`   Signals: ${opp.signals.join(', ')}\n`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export default CombinedScanner;
