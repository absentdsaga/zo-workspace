/**
 * JUPITER ROUTE VALIDATOR (ROBUST)
 * 
 * Validates buy/sell routes with actual Jupiter quotes
 * Includes retry logic, timeouts, and proper error handling
 */

const SOL_MINT = 'So11111111111111111111111111111111111111112';
const JUPITER_API = 'https://public.jupiterapi.com';

export interface RouteValidation {
  valid: boolean;
  quote?: any;
  priceUsd?: number;
  slippageBps?: number;
  error?: string;
  liquidityInsufficient?: boolean;
}

/**
 * Fetch with timeout and retry logic
 */
async function fetchWithRetry(
  url: string,
  options: any = {},
  maxRetries: number = 3,
  timeoutMs: number = 10000
): Promise<Response> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), timeoutMs);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; TradingBot/1.0)',
          ...options.headers
        }
      });

      clearTimeout(timeout);
      return response;

    } catch (error: any) {
      if (attempt === maxRetries) {
        throw new Error(`Failed after ${maxRetries} attempts: ${error.message}`);
      }

      // Exponential backoff
      const backoffMs = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
      await new Promise(resolve => setTimeout(resolve, backoffMs));
    }
  }

  throw new Error('Fetch failed after all retries');
}

export class JupiterValidator {
  private jupiterApiKey?: string;
  private solPriceUsd: number = 119;

  constructor(jupiterApiKey?: string) {
    this.jupiterApiKey = jupiterApiKey;
  }

  /**
   * Validate BUY route: SOL → Token
   */
  async validateBuyRoute(
    tokenAddress: string,
    solAmount: number
  ): Promise<RouteValidation> {
    try {
      const amountInLamports = Math.floor(solAmount * 1e9);

      const url = `${JUPITER_API}/quote?` +
        `inputMint=${SOL_MINT}&` +
        `outputMint=${tokenAddress}&` +
        `amount=${amountInLamports}&` +
        `slippageBps=300`;

      const headers: Record<string, string> = {};
      if (this.jupiterApiKey) {
        headers['x-api-key'] = this.jupiterApiKey;
      }

      const response = await fetchWithRetry(url, {
        headers,
        method: 'GET'
      }, 2, 8000); // 2 retries, 8 second timeout

      if (!response.ok) {
        const text = await response.text();
        
        // Check if it's a liquidity/routing issue vs API error
        const isLiquidityIssue = response.status === 404 || 
                                text.includes('No routes') || 
                                text.includes('No route found');

        return {
          valid: false,
          error: `Jupiter API ${response.status}: ${text.substring(0, 100)}`,
          liquidityInsufficient: isLiquidityIssue
        };
      }

      const quote = await response.json();

      if (!quote.outAmount) {
        return {
          valid: false,
          error: 'No output amount in quote',
          liquidityInsufficient: true
        };
      }

      // Calculate price
      const spentUsd = solAmount * this.solPriceUsd;
      const tokensReceived = parseInt(quote.outAmount);
      
      // Assume 6 decimals (most tokens)
      const decimals = 6;
      const tokensReceivedScaled = tokensReceived / Math.pow(10, decimals);
      
      const pricePerTokenUsd = spentUsd / tokensReceivedScaled;

      return {
        valid: true,
        quote,
        priceUsd: pricePerTokenUsd,
        slippageBps: parseInt(quote.slippageBps || '0')
      };

    } catch (error: any) {
      // Check if it's a network error vs routing error
      const isNetworkError = error.message.includes('Failed after') || 
                            error.message.includes('AbortError') ||
                            error.message.includes('ECONNREFUSED');

      return {
        valid: false,
        error: isNetworkError ? `Network error: ${error.message}` : error.message,
        liquidityInsufficient: !isNetworkError
      };
    }
  }

  /**
   * Validate SELL route: Token → SOL
   */
  async validateSellRoute(
    tokenAddress: string,
    solAmountInvested: number
  ): Promise<RouteValidation> {
    try {
      // First get buy quote to estimate tokens
      const buyValidation = await this.validateBuyRoute(tokenAddress, solAmountInvested);
      
      if (!buyValidation.valid || !buyValidation.quote) {
        return {
          valid: false,
          error: 'Cannot validate sell - buy route failed',
          liquidityInsufficient: true
        };
      }

      const tokensToSell = buyValidation.quote.outAmount;

      // Now get sell quote
      const url = `${JUPITER_API}/quote?` +
        `inputMint=${tokenAddress}&` +
        `outputMint=${SOL_MINT}&` +
        `amount=${tokensToSell}&` +
        `slippageBps=300`;

      const headers: Record<string, string> = {};
      if (this.jupiterApiKey) {
        headers['x-api-key'] = this.jupiterApiKey;
      }

      const response = await fetchWithRetry(url, {
        headers,
        method: 'GET'
      }, 2, 8000);

      if (!response.ok) {
        const text = await response.text();
        const isLiquidityIssue = response.status === 404 || 
                                text.includes('No routes') || 
                                text.includes('No route found');

        return {
          valid: false,
          error: `Sell route ${response.status}: ${text.substring(0, 100)}`,
          liquidityInsufficient: isLiquidityIssue
        };
      }

      const quote = await response.json();

      if (!quote.outAmount) {
        return {
          valid: false,
          error: 'No sell route available',
          liquidityInsufficient: true
        };
      }

      // Calculate sell price
      const solReceived = parseInt(quote.outAmount) / 1e9;
      const tokensToSellScaled = parseInt(tokensToSell) / Math.pow(10, 6);
      
      const solReceivedUsd = solReceived * this.solPriceUsd;
      const pricePerTokenUsd = solReceivedUsd / tokensToSellScaled;

      return {
        valid: true,
        quote,
        priceUsd: pricePerTokenUsd,
        slippageBps: parseInt(quote.slippageBps || '0')
      };

    } catch (error: any) {
      const isNetworkError = error.message.includes('Failed after') || 
                            error.message.includes('AbortError') ||
                            error.message.includes('ECONNREFUSED');

      return {
        valid: false,
        error: isNetworkError ? `Network error: ${error.message}` : error.message,
        liquidityInsufficient: !isNetworkError
      };
    }
  }

  /**
   * Validate BOTH buy and sell routes before entering position
   */
  async validateRoundTrip(
    tokenAddress: string,
    solAmount: number
  ): Promise<{
    canBuy: boolean;
    canSell: boolean;
    buyPrice?: number;
    sellPrice?: number;
    slippage?: number;
    error?: string;
  }> {
    const buyValidation = await this.validateBuyRoute(tokenAddress, solAmount);

    if (!buyValidation.valid) {
      const errorMsg = buyValidation.error || 'Unknown error';
      return {
        canBuy: false,
        canSell: false,
        error: errorMsg
      };
    }

    const sellValidation = await this.validateSellRoute(tokenAddress, solAmount);

    if (!sellValidation.valid) {
      const errorMsg = sellValidation.error || 'Unknown error';
      return {
        canBuy: true,
        canSell: false,
        buyPrice: buyValidation.priceUsd,
        error: errorMsg
      };
    }

    // Calculate round-trip slippage
    const slippage = buyValidation.priceUsd && sellValidation.priceUsd
      ? ((buyValidation.priceUsd - sellValidation.priceUsd) / buyValidation.priceUsd) * 100
      : 0;

    return {
      canBuy: true,
      canSell: true,
      buyPrice: buyValidation.priceUsd,
      sellPrice: sellValidation.priceUsd,
      slippage
    };
  }

  /**
   * Get REAL executable price (not stale API data)
   */
  async getRealExecutablePrice(
    tokenAddress: string,
    direction: 'buy' | 'sell',
    solAmount: number
  ): Promise<number | null> {
    const validation = direction === 'buy'
      ? await this.validateBuyRoute(tokenAddress, solAmount)
      : await this.validateSellRoute(tokenAddress, solAmount);

    return validation.valid ? (validation.priceUsd || null) : null;
  }
}
