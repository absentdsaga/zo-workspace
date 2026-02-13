/**
 * MEME SCANNER
 *
 * Scans DexScreener and Pump.fun for fresh meme coin opportunities
 * Focuses on 0-60 minute old launches with high momentum
 * Scores based on multiple signals
 */

interface Signal {
  type: 'volume_spike' | 'price_momentum' | 'liquidity_add' | 'social_buzz' | 'smart_money' | 'pumpfun_graduate';
  strength: number; // 0-100
  description: string;
}

interface MemeToken {
  address: string;
  symbol: string;
  name: string;
  marketCap: number;
  volume24h: number;
  priceUSD: number;
  priceChange1h: number;
  priceChange24h: number;
  liquidity: number;
  ageMinutes: number;
  pumpfunGraduated: boolean;
  signals: Signal[];
  score: number; // 0-100 opportunity score
  source: 'dexscreener' | 'pumpfun';
}

class MemeScanner {
  private readonly MIN_AGE_MINUTES = 0;
  private readonly MAX_AGE_MINUTES = 1440; // 24 hours
  private readonly MIN_LIQUIDITY = 2000; // $2k minimum (more realistic)
  private readonly MIN_VOLUME_24H = 1000; // $1k minimum volume in 24h

  constructor() {
    console.log('🔍 Meme Scanner initialized');
  }

  /**
   * Scan for opportunities
   */
  async scan(): Promise<MemeToken[]> {
    const opportunities: MemeToken[] = [];

    try {
      // Scan DexScreener for trending Solana tokens
      const dexScreenerTokens = await this.scanDexScreener();
      opportunities.push(...dexScreenerTokens);

    } catch (error: any) {
      // Silently fail
    }

    // Sort by score (highest first)
    opportunities.sort((a, b) => b.score - a.score);

    return opportunities;
  }

  /**
   * Scan DexScreener for trending tokens
   */
  private async scanDexScreener(): Promise<MemeToken[]> {
    // Get trending tokens on Solana chain directly
    const response = await fetch('https://api.dexscreener.com/token-profiles/latest/v1');

    if (!response.ok) {
      throw new Error(`DexScreener API error: ${response.status}`);
    }

    const profiles = await response.json();
    const tokens: MemeToken[] = [];

    // Also get boosted tokens
    const boostedResponse = await fetch('https://api.dexscreener.com/token-boosts/latest/v1');
    const boosted = boostedResponse.ok ? await boostedResponse.json() : [];

    // Combine both sources
    const allTokenAddresses = new Set([
      ...profiles.slice(0, 20).map((p: any) => p.tokenAddress),
      ...boosted.slice(0, 20).map((b: any) => b.tokenAddress)
    ]);

    // Fetch pair data for each token
    for (const tokenAddress of allTokenAddresses) {
      try {
        const pairResponse = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
        if (!pairResponse.ok) continue;

        const pairData = await pairResponse.json();
        const pairs = pairData.pairs || [];

        // Find Solana pairs only
        const solanaPairs = pairs.filter((p: any) => p.chainId === 'solana');
        if (solanaPairs.length === 0) continue;

        // Use highest liquidity pair
        const pair = solanaPairs.sort((a: any, b: any) =>
          (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
        )[0];

        // Filter: Must have basic data
        if (!pair.baseToken || !pair.priceUsd || !pair.liquidity) continue;

        // Calculate age (if pairCreatedAt exists)
        let ageMinutes = 999; // Unknown age
        if (pair.pairCreatedAt) {
          const ageMs = Date.now() - pair.pairCreatedAt;
          ageMinutes = ageMs / 1000 / 60;
        }

        // Filter: Skip very old tokens (>24h) if age is known
        if (ageMinutes < 999 && ageMinutes > 1440) {
          continue;
        }

        // Filter: Minimum liquidity (lower threshold)
        const liquidityUSD = pair.liquidity?.usd || 0;
        if (liquidityUSD < 2000) continue; // $2k minimum (was $5k)

        // Get volume data
        const volume24h = pair.volume?.h24 || 0;
        const volume1h = pair.volume?.h1 || 0;

        // Filter: Minimum volume (much more lenient)
        if (volume24h < 1000) continue; // $1k/day minimum

        // Build token object
        const token: MemeToken = {
          address: pair.baseToken.address,
          symbol: pair.baseToken.symbol,
          name: pair.baseToken.name,
          marketCap: pair.marketCap || 0,
          volume24h,
          priceUSD: parseFloat(pair.priceUsd),
          priceChange1h: pair.priceChange?.h1 || 0,
          priceChange24h: pair.priceChange?.h24 || 0,
          liquidity: liquidityUSD,
          ageMinutes,
          pumpfunGraduated: false,
          signals: [],
          score: 0,
          source: 'dexscreener'
        };

        // Generate signals and score
        this.analyzeToken(token);

        // Only include if score is decent
        if (token.score >= 40) {
          tokens.push(token);
        }
      } catch (error) {
        // Skip tokens that fail to fetch
        continue;
      }
    }

    return tokens;
  }

  /**
   * Analyze token and generate signals
   */
  private analyzeToken(token: MemeToken): void {
    const signals: Signal[] = [];
    let score = 0;

    // Signal 1: Volume spike (25 points) - INCREASED WEIGHT
    const volumeRatio = token.volume24h / token.liquidity;
    if (volumeRatio > 1.0) { // LOWERED THRESHOLD
      const strength = Math.min(100, volumeRatio * 25);
      signals.push({
        type: 'volume_spike',
        strength,
        description: `${volumeRatio.toFixed(1)}x volume/liquidity ratio`
      });
      score += 25;
    }

    // Signal 2: Price momentum (30 points) - INCREASED WEIGHT
    if (token.priceChange1h > 10) { // LOWERED THRESHOLD from 20
      const strength = Math.min(100, token.priceChange1h * 2);
      signals.push({
        type: 'price_momentum',
        strength,
        description: `+${token.priceChange1h.toFixed(1)}% in 1h`
      });
      score += 30;
    }

    // Signal 3: Strong liquidity (10 points) - DECREASED (less important)
    if (token.liquidity > 10000) { // LOWERED from 50k
      const strength = Math.min(100, (token.liquidity / 10000) * 50);
      signals.push({
        type: 'liquidity_add',
        strength,
        description: `$${(token.liquidity / 1000).toFixed(0)}k liquidity`
      });
      score += 10;
    }

    // Signal 4: Fresh launch bonus (25 points if <15 min) - INCREASED
    if (token.ageMinutes < 15) { // EXTENDED window
      const strength = 100 - (token.ageMinutes * 6.67);
      signals.push({
        type: 'social_buzz',
        strength,
        description: `Fresh launch (${token.ageMinutes.toFixed(0)} min old)`
      });
      score += 25;
    }

    // Signal 5: Market cap sweet spot (10 points for $20k-$1M) - MORE LENIENT
    if (token.marketCap >= 20000 && token.marketCap <= 1000000) {
      const strength = 70;
      signals.push({
        type: 'smart_money',
        strength,
        description: `Sweet spot MC: $${(token.marketCap / 1000).toFixed(0)}k`
      });
      score += 10;
    }

    token.signals = signals;
    token.score = Math.min(100, score);
  }

  /**
   * Get token details by address
   */
  async getTokenDetails(address: string): Promise<MemeToken | null> {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      const pairs = data.pairs || [];

      if (pairs.length === 0) {
        return null;
      }

      // Use first pair (usually highest liquidity)
      const pair = pairs[0];

      const token: MemeToken = {
        address: pair.baseToken.address,
        symbol: pair.baseToken.symbol,
        name: pair.baseToken.name,
        marketCap: pair.marketCap || 0,
        volume24h: pair.volume?.h24 || 0,
        priceUSD: parseFloat(pair.priceUsd),
        priceChange1h: pair.priceChange?.h1 || 0,
        priceChange24h: pair.priceChange?.h24 || 0,
        liquidity: pair.liquidity?.usd || 0,
        ageMinutes: 999,
        pumpfunGraduated: false,
        signals: [],
        score: 0,
        source: 'dexscreener'
      };

      this.analyzeToken(token);

      return token;

    } catch (error) {
      return null;
    }
  }
}

// CLI usage
async function main() {
  const scanner = new MemeScanner();

  console.log('🔍 Scanning for meme coin opportunities...\n');

  const opportunities = await scanner.scan();

  console.log(`\n📊 Found ${opportunities.length} opportunities:\n`);

  for (let i = 0; i < Math.min(5, opportunities.length); i++) {
    const token = opportunities[i];
    console.log(`${i + 1}. ${token.symbol} - Score: ${token.score}/100`);
    console.log(`   Address: ${token.address}`);
    console.log(`   Age: ${token.ageMinutes < 999 ? token.ageMinutes.toFixed(0) + ' min' : 'unknown'}`);
    console.log(`   MC: $${(token.marketCap / 1000).toFixed(0)}k | Liq: $${(token.liquidity / 1000).toFixed(0)}k`);
    console.log(`   Price: $${token.priceUSD.toFixed(8)} | 1h: ${token.priceChange1h >= 0 ? '+' : ''}${token.priceChange1h.toFixed(1)}%`);
    console.log(`   Signals: ${token.signals.map(s => s.type).join(', ')}`);
    console.log('');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { MemeScanner, MemeToken, Signal };
