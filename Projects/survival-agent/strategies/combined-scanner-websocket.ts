/**
 * COMBINED SCANNER WITH WEBSOCKET
 * 
 * Scans BOTH Pump.fun (via WebSocket) AND DexScreener (via REST API):
 * - Pump.fun: Real-time WebSocket feed from PumpPortal (bypasses Cloudflare)
 * - DexScreener: Established tokens with proven liquidity
 * 
 * Combines results, deduplicates, and returns best opportunities
 */

import { PumpPortalWebSocket, PumpPortalTokenCreate } from './pumpportal-websocket';
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
  initialBuy?: number; // SOL
  bondingCurveKey?: string;
  
  // DexScreener specific
  priceChange1h?: number;
  priceChange24h?: number;
  holders?: number;
}

export class CombinedScannerWebSocket {
  private pumpPortalWs: PumpPortalWebSocket;
  private dexScanner: MemeScanner;
  
  // Cache recent Pump.fun tokens (in-memory)
  private pumpfunTokens: Map<string, {
    token: PumpPortalTokenCreate;
    timestamp: number;
  }> = new Map();
  
  private readonly CACHE_DURATION_MS = 3600000; // 1 hour
  private wsConnected = false;

  constructor() {
    this.pumpPortalWs = new PumpPortalWebSocket();
    this.dexScanner = new MemeScanner();
    console.log('🔍 Combined Scanner (WebSocket) initialized');
  }

  /**
   * Initialize WebSocket connection
   */
  async initialize(): Promise<void> {
    try {
      console.log('🔌 Connecting to PumpPortal WebSocket...');
      
      await this.pumpPortalWs.connect();
      
      // Subscribe to new token creations
      this.pumpPortalWs.subscribeNewTokens();
      
      // Set up event handler to cache tokens
      this.pumpPortalWs.onTokenCreate((token) => {
        this.cacheToken(token);
      });
      
      this.wsConnected = true;
      console.log('✅ WebSocket connected and listening for new tokens\n');
      
    } catch (error: any) {
      console.log(`⚠️  WebSocket connection failed: ${error.message}`);
      console.log('   Will use DexScreener only until WebSocket connects\n');
      this.wsConnected = false;
    }
  }

  /**
   * Cache Pump.fun token
   */
  private cacheToken(token: PumpPortalTokenCreate): void {
    this.pumpfunTokens.set(token.mint, {
      token,
      timestamp: Date.now()
    });

    // Clean old tokens from cache
    this.cleanCache();
  }

  /**
   * Remove tokens older than cache duration
   */
  private cleanCache(): void {
    const now = Date.now();
    for (const [mint, data] of this.pumpfunTokens.entries()) {
      if (now - data.timestamp > this.CACHE_DURATION_MS) {
        this.pumpfunTokens.delete(mint);
      }
    }
  }

  /**
   * Scan both sources and combine results
   */
  async scan(): Promise<CombinedOpportunity[]> {
    // Scan both in parallel (silently)
    const [pumpfunResults, dexResults] = await Promise.all([
      this.scanPumpFunCache(),
      this.scanDexScreener()
    ]);

    // Combine and deduplicate
    const combined = this.combineAndDeduplicate(pumpfunResults, dexResults);

    // Sort by score
    combined.sort((a, b) => b.score - a.score);

    return combined;
  }

  /**
   * Scan Pump.fun cached tokens
   */
  private async scanPumpFunCache(): Promise<CombinedOpportunity[]> {
    this.cleanCache();
    
    const now = Date.now();
    const opportunities: CombinedOpportunity[] = [];

    for (const [mint, data] of this.pumpfunTokens.entries()) {
      const token = data.token;
      const ageMs = now - token.timestamp;
      const ageMinutes = ageMs / 60000;
      
      // Only include tokens 0-60 minutes old
      if (ageMinutes > 60) continue;
      
      // Score the token
      const score = this.scorePumpFunToken(token, ageMinutes);
      
      // Only include if score >= 30
      if (score < 30) continue;
      
      const signals: string[] = [];
      
      if (ageMinutes <= 5) signals.push('Ultra fresh (<5 min)');
      if (token.initialBuy >= 5) signals.push(`${token.initialBuy.toFixed(1)} SOL initial buy`);
      if (token.marketCapSol >= 50) signals.push(`${token.marketCapSol.toFixed(0)} SOL mcap`);
      
      opportunities.push({
        address: mint,
        symbol: token.symbol,
        name: token.name,
        score,
        ageMinutes,
        signals,
        source: 'pumpfun',
        marketCapUsd: token.marketCapSol * 119, // Approximate
        initialBuy: token.initialBuy,
        bondingCurveKey: token.bondingCurveKey
      });
    }

    return opportunities;
  }

  /**
   * Score Pump.fun token
   */
  private scorePumpFunToken(token: PumpPortalTokenCreate, ageMinutes: number): number {
    let score = 0;

    // Age (30 points)
    if (ageMinutes <= 5) score += 30;
    else if (ageMinutes <= 15) score += 25;
    else if (ageMinutes <= 30) score += 20;
    else if (ageMinutes <= 60) score += 15;

    // Initial buy size (30 points)
    if (token.initialBuy >= 10) score += 30;
    else if (token.initialBuy >= 5) score += 25;
    else if (token.initialBuy >= 2) score += 20;
    else if (token.initialBuy >= 1) score += 15;
    else if (token.initialBuy >= 0.5) score += 10;

    // Market cap (20 points)
    if (token.marketCapSol >= 50 && token.marketCapSol <= 500) score += 20;
    else if (token.marketCapSol >= 20 && token.marketCapSol <= 50) score += 15;
    else if (token.marketCapSol >= 500) score += 10;

    // Virtual reserves (20 points - indicates liquidity)
    const reserveRatio = token.vSolInBondingCurve / Math.max(token.vTokensInBondingCurve, 1);
    if (reserveRatio > 0.01) score += 20;
    else if (reserveRatio > 0.005) score += 15;
    else if (reserveRatio > 0.001) score += 10;

    return Math.min(score, 100);
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
        // Token found in BOTH sources - VERY bullish!
        const merged: CombinedOpportunity = {
          ...existing,
          source: 'both',
          score: Math.min(Math.max(existing.score, opp.score) + 20, 100),
          signals: [...existing.signals, ...opp.signals, '⭐ Found in both sources'],
          liquidityUsd: opp.liquidityUsd,
          volume24h: opp.volume24h,
          priceChange1h: opp.priceChange1h,
          priceChange24h: opp.priceChange24h
        };

        addressMap.set(opp.address, merged);
      } else {
        addressMap.set(opp.address, opp);
      }
    }

    return Array.from(addressMap.values());
  }

  /**
   * Get stats
   */
  getStats(): {
    wsConnected: boolean;
    cachedTokens: number;
    oldestTokenAge: number;
  } {
    let oldestAge = 0;
    const now = Date.now();
    
    for (const data of this.pumpfunTokens.values()) {
      const age = (now - data.timestamp) / 60000;
      if (age > oldestAge) oldestAge = age;
    }

    return {
      wsConnected: this.wsConnected,
      cachedTokens: this.pumpfunTokens.size,
      oldestTokenAge: oldestAge
    };
  }

  /**
   * Disconnect
   */
  disconnect(): void {
    this.pumpPortalWs.disconnect();
    this.wsConnected = false;
  }
}

export default CombinedScannerWebSocket;
