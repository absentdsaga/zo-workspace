/**
 * SUB-AGENT COORDINATOR
 *
 * Implements @legendaryy's principle #1:
 * "Heavy tasks (Twitter research, market scans) should run as sub-agents,
 * not in the main session. Your main lane stays clean and doesn't accumulate
 * 750K token context bombs"
 *
 * Uses Zo's /zo/ask API to parallelize heavy market scanning tasks.
 * Main session only receives essential results, not full API responses.
 */

interface ScanTask {
  task: string;
  limit?: number;
}

interface ScanResult {
  tokens: TokenSignal[];
  metadata: {
    scannedCount: number;
    passedFilter: number;
    executionTime: number;
  };
}

interface TokenSignal {
  address: string;
  symbol?: string;
  score: number;
  source: 'pumpfun' | 'dexscreener' | 'shocked';
  confidence: number;
  keyMetrics: {
    volume1h?: number;
    priceChange1h?: number;
    liquidity?: number;
    marketCap?: number;
  };
  reasons: string[];
}

export class SubAgentCoordinator {
  private apiKey: string;
  private baseUrl = 'https://api.zo.computer';

  constructor() {
    this.apiKey = process.env.ZO_CLIENT_IDENTITY_TOKEN || '';
    if (!this.apiKey) {
      throw new Error('ZO_CLIENT_IDENTITY_TOKEN not found in environment');
    }
  }

  /**
   * Run parallel market scans using sub-agents
   * Each scan runs in isolation, preventing context bloat
   */
  async parallelMarketScan(tasks: ScanTask[]): Promise<ScanResult[]> {
    console.log(`🔄 Launching ${tasks.length} parallel market scans...`);
    const startTime = Date.now();

    const promises = tasks.map(task => this.runScanTask(task));
    const results = await Promise.allSettled(promises);

    const successful = results
      .filter(r => r.status === 'fulfilled')
      .map(r => (r as PromiseFulfilledResult<ScanResult>).value);

    const failed = results.filter(r => r.status === 'rejected').length;

    console.log(`✅ Completed ${successful.length}/${tasks.length} scans in ${Date.now() - startTime}ms`);
    if (failed > 0) {
      console.log(`⚠️  ${failed} scans failed`);
    }

    return successful;
  }

  /**
   * Run a single scan task via /zo/ask API
   */
  private async runScanTask(task: ScanTask): Promise<ScanResult> {
    const prompt = this.buildScanPrompt(task);

    try {
      const response = await fetch(`${this.baseUrl}/zo/ask`, {
        method: 'POST',
        headers: {
          'authorization': this.apiKey,
          'content-type': 'application/json'
        },
        body: JSON.stringify({
          input: prompt,
          // We want text response with specific format, not structured output
          // Structured output is too rigid for nuanced market analysis
        })
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();
      const output = data.output as string;

      // Parse the text response into structured data
      return this.parseScanOutput(output, task);

    } catch (error: any) {
      console.error(`❌ Scan task failed: ${error.message}`);
      return {
        tokens: [],
        metadata: {
          scannedCount: 0,
          passedFilter: 0,
          executionTime: 0
        }
      };
    }
  }

  /**
   * Build a comprehensive, self-contained prompt for the sub-agent
   *
   * CRITICAL: Sub-agents have NO context from parent conversation.
   * Include ALL information needed for the task.
   */
  private buildScanPrompt(task: ScanTask): string {
    const limit = task.limit || 20;

    return `You are a Solana meme token scanner. Your task: ${task.task}

REQUIREMENTS:
1. Scan for up to ${limit} tokens
2. For each token, calculate a confidence score (0-100) based on:
   - Volume (1h and 24h)
   - Price momentum (5m, 1h changes)
   - Liquidity strength
   - Buy/sell pressure
   - Market cap sweet spot ($50k-$1M)
3. Only include tokens with confidence >= 40
4. Return results in this EXACT format:

TOKEN_START
Address: <token_address>
Symbol: <symbol>
Score: <0-100>
Source: <pumpfun|dexscreener|shocked>
Confidence: <0-100>
Volume1h: <usd_value>
PriceChange1h: <percentage>
Liquidity: <usd_value>
MarketCap: <usd_value>
Reasons: <comma,separated,reasons>
TOKEN_END

METADATA_START
ScannedCount: <number>
PassedFilter: <number>
ExecutionTime: <ms>
METADATA_END

CONSTRAINTS:
- Use DexScreener API: https://api.dexscreener.com/latest/dex/tokens/{address}
- For shocked tokens, check the watchlist at /home/workspace/Projects/survival-agent/data/paper-trade-watchlist.json
- Only return high-confidence signals (score >= 40)
- Be concise - no explanations, just data

Start scanning now.`;
  }

  /**
   * Parse the sub-agent's text response into structured data
   */
  private parseScanOutput(output: string, task: ScanTask): ScanResult {
    const tokens: TokenSignal[] = [];
    let metadata = {
      scannedCount: 0,
      passedFilter: 0,
      executionTime: 0
    };

    // Extract tokens using regex
    const tokenRegex = /TOKEN_START\s+(.*?)\s+TOKEN_END/gs;
    const tokenMatches = output.matchAll(tokenRegex);

    for (const match of tokenMatches) {
      const tokenData = match[1];
      const token = this.parseTokenData(tokenData);
      if (token) {
        tokens.push(token);
      }
    }

    // Extract metadata
    const metadataRegex = /METADATA_START\s+(.*?)\s+METADATA_END/s;
    const metadataMatch = output.match(metadataRegex);

    if (metadataMatch) {
      const metadataStr = metadataMatch[1];
      metadata = this.parseMetadata(metadataStr);
    }

    return { tokens, metadata };
  }

  /**
   * Parse individual token data from text
   */
  private parseTokenData(data: string): TokenSignal | null {
    try {
      const lines = data.split('\n').filter(l => l.trim());
      const fields: Record<string, string> = {};

      for (const line of lines) {
        const [key, ...valueParts] = line.split(':');
        if (key && valueParts.length > 0) {
          fields[key.trim()] = valueParts.join(':').trim();
        }
      }

      return {
        address: fields['Address'] || '',
        symbol: fields['Symbol'],
        score: parseFloat(fields['Score']) || 0,
        source: (fields['Source'] as any) || 'dexscreener',
        confidence: parseFloat(fields['Confidence']) || 0,
        keyMetrics: {
          volume1h: parseFloat(fields['Volume1h']) || undefined,
          priceChange1h: parseFloat(fields['PriceChange1h']) || undefined,
          liquidity: parseFloat(fields['Liquidity']) || undefined,
          marketCap: parseFloat(fields['MarketCap']) || undefined
        },
        reasons: fields['Reasons']?.split(',') || []
      };
    } catch (error) {
      console.error('Failed to parse token data:', error);
      return null;
    }
  }

  /**
   * Parse metadata from text
   */
  private parseMetadata(data: string): { scannedCount: number; passedFilter: number; executionTime: number } {
    const lines = data.split('\n').filter(l => l.trim());
    const fields: Record<string, string> = {};

    for (const line of lines) {
      const [key, value] = line.split(':');
      if (key && value) {
        fields[key.trim()] = value.trim();
      }
    }

    return {
      scannedCount: parseInt(fields['ScannedCount']) || 0,
      passedFilter: parseInt(fields['PassedFilter']) || 0,
      executionTime: parseInt(fields['ExecutionTime']) || 0
    };
  }

  /**
   * Simplified scan for quick checks
   * Returns top N tokens across all sources
   */
  async quickScan(limit: number = 10): Promise<TokenSignal[]> {
    const tasks: ScanTask[] = [
      { task: 'Scan pump.fun trending tokens', limit: Math.ceil(limit / 3) },
      { task: 'Scan DexScreener high momentum tokens', limit: Math.ceil(limit / 3) },
      { task: 'Scan shocked watchlist for high scores', limit: Math.ceil(limit / 3) }
    ];

    const results = await this.parallelMarketScan(tasks);
    const allTokens = results.flatMap(r => r.tokens);

    // Sort by score and return top N
    return allTokens
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }
}
