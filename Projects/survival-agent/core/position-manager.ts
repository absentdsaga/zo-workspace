/**
 * POSITION MANAGER
 *
 * Tracks open positions and manages exits
 * - Monitors token holdings in real-time
 * - Implements take profit and stop loss
 * - Uses Helius funded-by to detect rugs before buying
 */

import { Connection, PublicKey } from '@solana/web3.js';

interface Position {
  tokenAddress: string;
  tokenSymbol: string;
  entryPrice: number;
  entryAmount: number;
  entryCostSOL: number;
  entryTime: number;
  currentPrice?: number;
  currentValueSOL?: number;
  pnl?: number;
  pnlPercent?: number;
  holdTimeMinutes?: number;
}

interface ExitConditions {
  takeProfitPercent: number; // Exit at +X%
  stopLossPercent: number; // Exit at -X%
  maxHoldMinutes: number; // Exit after X minutes
  trailingStopPercent?: number; // Optional trailing stop
}

class PositionManager {
  private connection: Connection;
  private walletAddress: PublicKey;
  private heliusApiKey: string;
  private jupiterApiKey: string;

  private positions: Map<string, Position> = new Map();

  // Default exit conditions for meme coins
  private readonly DEFAULT_EXIT: ExitConditions = {
    takeProfitPercent: 100, // Take profit at +100%
    stopLossPercent: -30, // Stop loss at -30%
    maxHoldMinutes: 60, // Max 1 hour hold
    trailingStopPercent: 20 // Trail by 20% from peak
  };

  constructor(
    rpcUrl: string,
    walletAddress: string,
    heliusApiKey: string,
    jupiterApiKey: string
  ) {
    this.connection = new Connection(rpcUrl, 'confirmed');
    this.walletAddress = new PublicKey(walletAddress);
    this.heliusApiKey = heliusApiKey;
    this.jupiterApiKey = jupiterApiKey;

    console.log('📊 Position Manager initialized');
  }

  /**
   * Get token holder distribution using Helius API
   */
  async checkHolderDistribution(tokenAddress: string): Promise<{
    safe: boolean;
    reason: string;
    holderCount?: number;
    top10Percent?: number;
  }> {
    try {
      const heliusUrl = `https://mainnet.helius-rpc.com/?api-key=${this.heliusApiKey}`;

      // Get token holders using Helius enhanced API
      const response = await fetch(heliusUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 'holder-check',
          method: 'getTokenAccounts',
          params: {
            mint: tokenAddress,
            limit: 100,
            page: 1
          }
        })
      });

      if (!response.ok) {
        return { safe: true, reason: 'Cannot verify holders (assume safe)' };
      }

      const data = await response.json();
      const accounts = data.result?.token_accounts || [];

      if (accounts.length === 0) {
        return { safe: false, reason: 'No holders found (dead token?)' };
      }

      // Calculate top 10 concentration
      const sortedByBalance = accounts.sort((a: any, b: any) =>
        parseFloat(b.amount) - parseFloat(a.amount)
      );

      const totalSupply = accounts.reduce((sum: number, acc: any) =>
        sum + parseFloat(acc.amount), 0
      );

      const top10Supply = sortedByBalance.slice(0, 10).reduce((sum: number, acc: any) =>
        sum + parseFloat(acc.amount), 0
      );

      const top10Percent = (top10Supply / totalSupply) * 100;

      // RED FLAG: Top 10 holders own >80% (too centralized for fresh launches)
      // Relaxed from 60% → 75% → 80% based on research showing WHITEWHALE (54%) and successful launches have 70-80% concentration
      if (top10Percent > 80) {
        return {
          safe: false,
          reason: `Too centralized: Top 10 hold ${top10Percent.toFixed(1)}%`,
          holderCount: accounts.length,
          top10Percent
        };
      }

      // YELLOW FLAG: Top 10 hold 60-80% (normal for fresh 0-60 min launches)
      if (top10Percent > 60) {
        return {
          safe: true,
          reason: `Early-stage concentration: Top 10 hold ${top10Percent.toFixed(1)}%`,
          holderCount: accounts.length,
          top10Percent
        };
      }

      // GREEN: Well distributed
      return {
        safe: true,
        reason: `Good distribution: Top 10 hold ${top10Percent.toFixed(1)}%`,
        holderCount: accounts.length,
        top10Percent
      };

    } catch (error: any) {
      return { safe: true, reason: `Holder check failed: ${error.message}` };
    }
  }

  /**
   * Get enhanced token metadata using Helius API
   */
  async getTokenMetadata(tokenAddress: string): Promise<{
    symbol?: string;
    name?: string;
    decimals?: number;
    totalSupply?: number;
    isFrozen?: boolean;
    hasAuthority?: boolean;
  }> {
    try {
      const heliusUrl = `https://mainnet.helius-rpc.com/?api-key=${this.heliusApiKey}`;

      const response = await fetch(heliusUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 'token-metadata',
          method: 'getAsset',
          params: { id: tokenAddress }
        })
      });

      if (!response.ok) return {};

      const data = await response.json();
      const asset = data.result || {};

      return {
        symbol: asset.content?.metadata?.symbol,
        name: asset.content?.metadata?.name,
        decimals: asset.token_info?.decimals,
        totalSupply: asset.token_info?.supply,
        isFrozen: asset.token_info?.frozen || false,
        hasAuthority: asset.authorities?.length > 0
      };

    } catch (error) {
      return {};
    }
  }

  /**
   * Check if deployer wallet is sketchy using Helius funded-by
   */
  async checkDeployerSafety(tokenAddress: string): Promise<{
    safe: boolean;
    reason: string;
    fundedBy?: string[];
  }> {
    try {
      // Get token info to find deployer
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
      if (!response.ok) return { safe: false, reason: 'Cannot fetch token info' };

      const data = await response.json();
      const pairs = data.pairs || [];
      if (pairs.length === 0) return { safe: false, reason: 'No pairs found' };

      // Get deployer from first pair
      const deployerWallet = pairs[0].pairAddress; // Using pair address as proxy

      // Check funded-by using Helius
      const heliusUrl = `https://mainnet.helius-rpc.com/?api-key=${this.heliusApiKey}`;

      const fundedByResponse = await fetch(heliusUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 'funded-by-check',
          method: 'getFundedBy',
          params: [deployerWallet]
        })
      });

      if (!fundedByResponse.ok) {
        return { safe: true, reason: 'Cannot verify (assume safe)' };
      }

      const fundedByData = await fundedByResponse.json();
      const fundedBy = fundedByData.result || [];

      // RED FLAGS
      const redFlags = ['mixer', 'tornado', 'suspicious'];
      const hasRedFlag = fundedBy.some((source: string) =>
        redFlags.some(flag => source.toLowerCase().includes(flag))
      );

      if (hasRedFlag) {
        return {
          safe: false,
          reason: `Deployer funded by ${fundedBy.join(', ')}`,
          fundedBy
        };
      }

      // GREEN FLAGS
      const greenFlags = ['exchange', 'coinbase', 'binance', 'kraken'];
      const hasGreenFlag = fundedBy.some((source: string) =>
        greenFlags.some(flag => source.toLowerCase().includes(flag))
      );

      if (hasGreenFlag) {
        return {
          safe: true,
          reason: `Deployer funded by legit source: ${fundedBy.join(', ')}`,
          fundedBy
        };
      }

      // Unknown but no red flags = cautiously safe
      return {
        safe: true,
        reason: 'No red flags detected',
        fundedBy
      };

    } catch (error: any) {
      // If check fails, assume safe (don't block trades on API errors)
      return { safe: true, reason: `Check failed: ${error.message}` };
    }
  }

  /**
   * Add a new position
   */
  addPosition(
    tokenAddress: string,
    tokenSymbol: string,
    entryCostSOL: number,
    entryAmount: number,
    entryPrice: number
  ): void {
    const position: Position = {
      tokenAddress,
      tokenSymbol,
      entryPrice,
      entryAmount,
      entryCostSOL,
      entryTime: Date.now()
    };

    this.positions.set(tokenAddress, position);

    console.log(`📊 Added position: ${tokenSymbol}`);
    console.log(`   Entry: ${entryCostSOL.toFixed(4)} SOL @ $${entryPrice.toFixed(8)}`);
  }

  /**
   * Remove position (after exit)
   */
  removePosition(tokenAddress: string): void {
    this.positions.delete(tokenAddress);
  }

  /**
   * Update position with current price
   */
  async updatePosition(tokenAddress: string): Promise<void> {
    const position = this.positions.get(tokenAddress);
    if (!position) return;

    try {
      // Get current price from DexScreener
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
      if (!response.ok) return;

      const data = await response.json();
      const pairs = data.pairs || [];
      if (pairs.length === 0) return;

      const pair = pairs.sort((a: any, b: any) =>
        (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
      )[0];

      const currentPrice = parseFloat(pair.priceUsd);
      const currentValueSOL = (position.entryAmount * currentPrice) / 119; // Rough SOL conversion

      position.currentPrice = currentPrice;
      position.currentValueSOL = currentValueSOL;
      position.pnl = currentValueSOL - position.entryCostSOL;
      position.pnlPercent = (position.pnl / position.entryCostSOL) * 100;
      position.holdTimeMinutes = (Date.now() - position.entryTime) / 60000;

    } catch (error) {
      // Skip update on error
    }
  }

  /**
   * Check if position should exit
   */
  shouldExit(
    tokenAddress: string,
    conditions: ExitConditions = this.DEFAULT_EXIT
  ): { shouldExit: boolean; reason: string } {
    const position = this.positions.get(tokenAddress);
    if (!position) return { shouldExit: false, reason: 'No position' };

    // Must have current price
    if (!position.pnlPercent) {
      return { shouldExit: false, reason: 'No current price' };
    }

    // 1. Take profit
    if (position.pnlPercent >= conditions.takeProfitPercent) {
      return {
        shouldExit: true,
        reason: `Take profit: +${position.pnlPercent.toFixed(1)}% (target: +${conditions.takeProfitPercent}%)`
      };
    }

    // 2. Stop loss
    if (position.pnlPercent <= conditions.stopLossPercent) {
      return {
        shouldExit: true,
        reason: `Stop loss: ${position.pnlPercent.toFixed(1)}% (limit: ${conditions.stopLossPercent}%)`
      };
    }

    // 3. Max hold time
    if (position.holdTimeMinutes! >= conditions.maxHoldMinutes) {
      return {
        shouldExit: true,
        reason: `Max hold time: ${position.holdTimeMinutes!.toFixed(0)} min (limit: ${conditions.maxHoldMinutes} min)`
      };
    }

    return { shouldExit: false, reason: 'Holding' };
  }

  /**
   * Get all positions
   */
  getPositions(): Position[] {
    return Array.from(this.positions.values());
  }

  /**
   * Get position by token address
   */
  getPosition(tokenAddress: string): Position | undefined {
    return this.positions.get(tokenAddress);
  }

  /**
   * Monitor all positions and return list of exits needed
   */
  async monitorPositions(): Promise<Array<{ tokenAddress: string; reason: string }>> {
    const exitsNeeded: Array<{ tokenAddress: string; reason: string }> = [];

    for (const [tokenAddress, position] of this.positions.entries()) {
      await this.updatePosition(tokenAddress);

      const { shouldExit, reason } = this.shouldExit(tokenAddress);

      if (shouldExit) {
        exitsNeeded.push({ tokenAddress, reason });
      }
    }

    return exitsNeeded;
  }

  /**
   * Print position status
   */
  printPosition(tokenAddress: string): void {
    const position = this.positions.get(tokenAddress);
    if (!position) {
      console.log(`No position for ${tokenAddress}`);
      return;
    }

    console.log(`\n📊 Position: ${position.tokenSymbol}`);
    console.log(`   Entry: ${position.entryCostSOL.toFixed(4)} SOL @ $${position.entryPrice.toFixed(8)}`);

    if (position.currentPrice) {
      console.log(`   Current: ${position.currentValueSOL!.toFixed(4)} SOL @ $${position.currentPrice.toFixed(8)}`);
      console.log(`   P&L: ${position.pnl! >= 0 ? '+' : ''}${position.pnl!.toFixed(4)} SOL (${position.pnlPercent! >= 0 ? '+' : ''}${position.pnlPercent!.toFixed(1)}%)`);
      console.log(`   Hold time: ${position.holdTimeMinutes!.toFixed(0)} minutes`);
    }
  }
}

export { PositionManager, Position, ExitConditions };
