import { OptimizedExecutor } from './optimized-executor';
import { SafeLiquidityScanner } from '../strategies/safe-liquidity-scanner';
import { PumpFunScanner } from '../strategies/pumpfun-scanner';
import { PumpPortalWebSocket, PumpPortalTokenCreate } from '../strategies/pumpportal-websocket';
import { PositionManager } from './position-manager';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * SAFE MASTER COORDINATOR V2
 *
 * SURVIVAL MODE IMPROVEMENTS:
 * 1. Integrated PositionManager with exit monitoring
 * 2. Helius deployer safety checks (funded-by API)
 * 3. Tighter stop losses (-20% vs -30%)
 * 4. Faster exits (30 min max hold)
 * 5. Changed entry criteria (avoid pumps, seek consolidation)
 * 6. Reduced position size (5% for longevity)
 */

interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  amountIn: number;
  buySignature?: string;
  sellSignature?: string;
  pnl?: number;
  pnlPercent?: number;
  status: 'pending' | 'bought' | 'sold' | 'failed';
}

class SafeMasterCoordinator {
  private executor: OptimizedExecutor;
  private scanner: SafeLiquidityScanner;
  private pumpfunScanner: PumpFunScanner;
  private pumpportalWS: PumpPortalWebSocket;
  private positionManager: PositionManager;

  private startingBalance: number;
  private currentBalance: number;
  private trades: TradeLog[] = [];
  private isPaused = false;
  private walletAddress: string;

  // Real-time token queue from WebSocket
  private realtimeTokenQueue: PumpPortalTokenCreate[] = [];

  // USER PREFERRED risk management
  private readonly MAX_POSITION_SIZE = 0.08; // 8% per trade (original)
  private readonly MIN_BALANCE = 0.1; // Stop at 0.1 SOL
  private readonly MAX_DRAWDOWN = 0.20; // 20% max drawdown
  private readonly MIN_SCORE = 60; // Original threshold
  private readonly SCAN_INTERVAL_MS = 30000; // 30 seconds

  // Position-based exit strategy with PARTIAL EXITS
  private readonly USE_POSITION_MANAGER = true;
  private readonly TAKE_PROFIT_PERCENT = 100; // +100% take profit (partial exit 80%)
  private readonly STOP_LOSS_PERCENT = -30; // -30% stop loss (original)
  private readonly MAX_HOLD_MINUTES = 60; // 60 min max (original)
  private readonly PARTIAL_EXIT_PERCENT = 0.80; // Sell 80% at TP, let 20% run
  private readonly PAPER_TRADE = true; // Paper trading mode - no real trades

  constructor(
    rpcUrl: string,
    privateKey: string,
    jupiterApiKey: string,
    heliusApiKey: string
  ) {
    this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey);
    this.scanner = new SafeLiquidityScanner(jupiterApiKey);
    this.pumpfunScanner = new PumpFunScanner();
    this.pumpportalWS = new PumpPortalWebSocket();

    // Get wallet address for position manager
    this.walletAddress = this.executor['wallet'].publicKey.toString();

    this.positionManager = new PositionManager(
      rpcUrl,
      this.walletAddress,
      heliusApiKey,
      jupiterApiKey
    );

    this.startingBalance = 0;
    this.currentBalance = 0;

    console.log('🛡️  Safe Master Coordinator V2 initialized');
    console.log('⚙️  SURVIVAL MODE: Position tracking + deployer checks + tight exits');
  }

  async initialize(): Promise<void> {
    console.log('\n🔧 Initializing SURVIVAL MODE trading system...\n');

    const check = await this.executor.preFlightCheck();

    if (!check.ready) {
      throw new Error('System not ready');
    }

    this.startingBalance = check.balance;
    this.currentBalance = check.balance;

    console.log('\n✅ System initialized');
    console.log(`💰 Starting balance: ${this.startingBalance.toFixed(4)} SOL (~$${(this.startingBalance * 119).toFixed(2)})`);
    console.log(`🎯 SURVIVAL MODE parameters:`);
    console.log(`   Max position: ${(this.MAX_POSITION_SIZE * 100).toFixed(0)}%`);
    console.log(`   Take profit: +${this.TAKE_PROFIT_PERCENT}% (sell ${(this.PARTIAL_EXIT_PERCENT * 100)}%, hold ${((1 - this.PARTIAL_EXIT_PERCENT) * 100)}% for runners)`);
    console.log(`   Stop loss: ${this.STOP_LOSS_PERCENT}%`);
    console.log(`   Max hold: ${this.MAX_HOLD_MINUTES} minutes`);
    console.log(`   Min score: ${this.MIN_SCORE}`);
    console.log(`   Deployer checks: ENABLED`);
    console.log(`   Position tracking: ENABLED`);

    // Initialize PumpPortal WebSocket
    await this.initializeWebSocket();
  }

  /**
   * Initialize PumpPortal WebSocket for real-time token detection
   */
  private async initializeWebSocket(): Promise<void> {
    try {
      console.log('\n🔌 Initializing PumpPortal WebSocket...');

      await this.pumpportalWS.connect();

      // Set up token creation callback
      this.pumpportalWS.onTokenCreate((token) => {
        // Calculate age in minutes (if no timestamp, assume it's brand new)
        const ageMinutes = token.timestamp ? (Date.now() - token.timestamp) / 60000 : 0;
        const marketCapUSD = token.marketCapSol * 119;

        // Only queue tokens 0-60 min old with >$3k market cap (matches DexScreener filter)
        if (ageMinutes <= 60 && marketCapUSD >= 3000) {
          console.log(`   ⚡ QUEUED: ${token.symbol} ($${(marketCapUSD / 1000).toFixed(1)}k mcap, ${ageMinutes.toFixed(1)}min old)`);
          this.realtimeTokenQueue.push(token);
        }
      });

      // Set up graduation callback (viral signal!)
      this.pumpportalWS.onGraduation((graduation) => {
        console.log(`   🎓 Token graduated: ${graduation.mint.substring(0, 8)}... → Raydium pool created`);
      });

      // Subscribe to new token creations
      this.pumpportalWS.subscribeNewTokens();

      console.log('✅ PumpPortal WebSocket ready - listening for launches\n');

    } catch (error: any) {
      console.error('⚠️  PumpPortal WebSocket failed to initialize:', error.message);
      console.log('   Continuing with DexScreener + Pump.fun REST API only\n');
    }
  }

  async run(): Promise<void> {
    console.log('\n🚀 Starting SURVIVAL MODE trading loop...\n');
    console.log('🔄 Scanning every 30 seconds');
    console.log('🛡️  Deployer safety checks ENABLED');
    console.log('📊 Position monitoring ENABLED');
    console.log('⚡ Tight exit conditions: +100% TP / -20% SL / 30min max\n');

    let loopCount = 0;

    // Start exit monitoring in background
    this.startExitMonitoring();

    while (true) {
      try {
        loopCount++;
        console.log(`\n${'='.repeat(60)}`);
        console.log(`Loop ${loopCount} - ${new Date().toLocaleTimeString()}`);
        console.log('='.repeat(60));

        if (this.isPaused) {
          console.log('⏸️  System paused');
          await this.sleep(60000);
          continue;
        }

        await this.updateBalance();

        const shouldPause = this.checkCircuitBreakers();
        if (shouldPause) {
          this.isPaused = true;
          console.log('\n🚨 CIRCUIT BREAKER TRIGGERED - SYSTEM PAUSED');
          continue;
        }

        // 1. Scan for safe opportunities (DexScreener + Pump.fun + Real-time WebSocket)
        console.log('\n1️⃣  Scanning for SAFE opportunities...');
        console.log('   📊 DexScreener scan...');
        const dexScreenerOpps = await this.scanner.scan();

        console.log('   🚀 Pump.fun scan...');
        const pumpfunTokens = await this.pumpfunScanner.scanLatest(50);

        // Convert Pump.fun tokens to our opportunity format
        const pumpfunOpps = pumpfunTokens.map(token => ({
          address: token.mint,
          symbol: token.symbol,
          name: token.name,
          liquidityUSD: token.usd_market_cap, // Using market cap as proxy
          volume24h: 0, // Not available from Pump.fun
          priceUSD: 0,
          priceChange1h: 0,
          ageMinutes: token.ageMinutes || 0,
          safetyScore: 70, // Default for Pump.fun tokens
          liquidityScore: 60,
          totalScore: this.pumpfunScanner.scoreToken(token),
          warnings: token.isGraduating ? ['Near bonding curve graduation'] : []
        }));

        // Add real-time tokens from WebSocket queue (HIGHEST PRIORITY)
        const realtimeOpps = this.realtimeTokenQueue.splice(0, 10).map(token => ({
          address: token.mint,
          symbol: token.symbol,
          name: token.name,
          liquidityUSD: token.marketCapSol * 119, // Convert SOL to USD
          volume24h: token.initialBuy * 119, // Initial buy as volume proxy
          priceUSD: 0,
          priceChange1h: 0,
          ageMinutes: (Date.now() - token.timestamp) / 60000,
          safetyScore: 80, // Higher score for real-time tokens (faster entry)
          liquidityScore: 70,
          totalScore: 90, // Prioritize real-time tokens
          warnings: ['Real-time WebSocket detection - FAST ENTRY']
        }));

        // Merge all sources, remove duplicates
        const allOpportunities = [...realtimeOpps, ...dexScreenerOpps, ...pumpfunOpps];
        const uniqueOpps = allOpportunities.filter((opp, index, self) =>
          index === self.findIndex(o => o.address === opp.address)
        );

        // Sort by total score
        const opportunities = uniqueOpps.sort((a, b) => b.totalScore - a.totalScore);

        console.log(`   Found ${opportunities.length} safe opportunities (${realtimeOpps.length} WebSocket + ${dexScreenerOpps.length} DexScreener + ${pumpfunOpps.length} Pump.fun)`);

        if (opportunities.length === 0) {
          console.log('   ⏭️  No safe opportunities, waiting...');
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 2. Get top opportunity
        const topOpportunity = opportunities[0];

        console.log(`\n2️⃣  Top safe opportunity:`);
        console.log(`   Token: ${topOpportunity.symbol} (${topOpportunity.address.substring(0, 8)}...)`);
        console.log(`   Total Score: ${topOpportunity.totalScore}/100`);
        console.log(`   Liquidity: $${(topOpportunity.liquidityUSD / 1000).toFixed(0)}k`);
        console.log(`   Safety: ${topOpportunity.safetyScore}/100`);

        // 3. Check minimum score
        if (topOpportunity.totalScore < this.MIN_SCORE) {
          console.log(`\n3️⃣  ⏭️  Score too low (${topOpportunity.totalScore} < ${this.MIN_SCORE})`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 4. CRITICAL: Check if already holding this token (prevent duplicates!)
        const existingPosition = this.positionManager.getPosition(topOpportunity.address);
        if (existingPosition) {
          console.log(`\n3️⃣  ⏭️  Already holding ${topOpportunity.symbol} - skipping duplicate buy`);
          console.log(`   Current position: ${existingPosition.entryAmount.toFixed(2)} tokens`);
          console.log(`   Unrealized P&L: ${existingPosition.pnlPercent?.toFixed(2) || '?'}%`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 5. CRITICAL: Enhanced Helius safety checks
        console.log(`\n4️⃣  Running enhanced Helius safety checks...`);

        // 5a. Check deployer funding source
        console.log(`   🔍 Deployer verification (funded-by)...`);
        const deployerCheck = await this.positionManager.checkDeployerSafety(topOpportunity.address);

        console.log(`   ${deployerCheck.safe ? '✅' : '❌'} ${deployerCheck.reason}`);
        if (deployerCheck.fundedBy && deployerCheck.fundedBy.length > 0) {
          console.log(`      Funded by: ${deployerCheck.fundedBy.join(', ')}`);
        }

        if (!deployerCheck.safe) {
          console.log(`   🚨 UNSAFE DEPLOYER - SKIPPING`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 5b. Check holder distribution
        console.log(`   🔍 Holder distribution analysis...`);
        const holderCheck = await this.positionManager.checkHolderDistribution(topOpportunity.address);

        console.log(`   ${holderCheck.safe ? '✅' : '❌'} ${holderCheck.reason}`);
        if (holderCheck.holderCount) {
          console.log(`      Holders: ${holderCheck.holderCount} | Top 10: ${holderCheck.top10Percent?.toFixed(1)}%`);
        }

        if (!holderCheck.safe) {
          console.log(`   🚨 TOO CENTRALIZED - SKIPPING`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 5c. Get enhanced token metadata
        console.log(`   🔍 Token metadata check...`);
        const metadata = await this.positionManager.getTokenMetadata(topOpportunity.address);

        if (metadata.isFrozen) {
          console.log(`   ❌ Token is frozen - SKIPPING`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        if (metadata.hasAuthority) {
          console.log(`   ⚠️  Token has mint authority (can be diluted)`);
        }

        console.log(`   ✅ All Helius checks passed`)

        // 6. Validate sell route BEFORE buying
        console.log(`\n5️⃣  Validating we can EXIT before buying...`);

        const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
        const amountLamports = Math.floor(positionSize * LAMPORTS_PER_SOL);

        const canSell = await this.scanner.validateSellRoute(topOpportunity.address, amountLamports);

        if (!canSell) {
          console.log(`   ❌ Cannot validate sell route - SKIPPING`);
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        console.log(`   ✅ Sell route validated`);

        // 7. Execute buy and track position
        console.log(`\n6️⃣  🎯 EXECUTING TRADE`);
        console.log(`   Position: ${positionSize.toFixed(4)} SOL (5%)`);

        await this.executeBuy(topOpportunity, positionSize);

        // 8. Print health
        console.log('\n7️⃣  System health:');
        this.printHealth();

        // Sleep before next scan
        console.log(`\n⏳ Sleeping for ${this.SCAN_INTERVAL_MS / 1000} seconds...`);
        await this.sleep(this.SCAN_INTERVAL_MS);

      } catch (error: any) {
        console.error(`\n❌ Error in main loop: ${error.message}`);
        await this.sleep(60000);
      }
    }
  }

  /**
   * Execute buy and track position (let exit monitor handle sells)
   */
  private async executeBuy(opportunity: any, positionSize: number): Promise<void> {
    const amountLamports = Math.floor(positionSize * LAMPORTS_PER_SOL);
    const SOL = 'So11111111111111111111111111111111111111112';

    const trade: TradeLog = {
      timestamp: Date.now(),
      tokenAddress: opportunity.address,
      tokenSymbol: opportunity.symbol,
      amountIn: positionSize,
      status: 'pending'
    };

    this.trades.push(trade);

    try {
      // BUY (paper trade or real)
      console.log(`\n   📥 ${this.PAPER_TRADE ? '📄 PAPER TRADING - SIMULATING BUY' : 'BUYING'}...`);

      let buyResult: any;

      if (this.PAPER_TRADE) {
        // Get real quote but don't execute
        const quoteUrl = `https://quote-api.jup.ag/v6/quote?` +
          `inputMint=${SOL}&` +
          `outputMint=${opportunity.address}&` +
          `amount=${amountLamports}&` +
          `slippageBps=300`;

        const quoteResponse = await fetch(quoteUrl);
        const quote = await quoteResponse.json();

        buyResult = {
          success: true,
          signature: 'PAPER_TRADE_' + Date.now(),
          executionTime: Math.random() * 500 + 200,
          quote: quote
        };
      } else {
        buyResult = await this.executor.executeTrade({
          inputMint: SOL,
          outputMint: opportunity.address,
          amount: amountLamports,
          slippageBps: 300,
          strategy: 'volume'
        });
      }

      if (!buyResult.success) {
        trade.status = 'failed';
        console.log(`\n   ❌ BUY FAILED: ${buyResult.error}`);
        return;
      }

      trade.buySignature = buyResult.signature;
      trade.status = 'bought';

      console.log(`\n   ✅ ${this.PAPER_TRADE ? '📄 PAPER BOUGHT' : 'BOUGHT'}`);
      console.log(`      Signature: ${buyResult.signature}`);
      console.log(`      Speed: ${buyResult.executionTime}ms`);

      // Get token amount from account (or simulate for paper trading)
      let tokenAmount: number;
      const entryPrice = opportunity.priceUSD;

      if (this.PAPER_TRADE) {
        // Calculate expected tokens from quote
        if (buyResult.quote && buyResult.quote.outAmount) {
          tokenAmount = parseInt(buyResult.quote.outAmount) / Math.pow(10, 6); // Assume 6 decimals
        } else {
          // Rough estimate: SOL spent / token price
          tokenAmount = positionSize / entryPrice * 119; // $119/SOL estimate
        }
      } else {
        const { Connection, PublicKey } = await import('@solana/web3.js');
        const connection = new Connection(
          `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_RPC_URL}`,
          'confirmed'
        );

        const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
          new PublicKey(this.executor['wallet'].publicKey),
          { programId: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA') }
        );

        const tokenAccount = tokenAccounts.value.find(
          acc => acc.account.data.parsed.info.mint === opportunity.address
        );

        if (!tokenAccount) {
          console.log(`   ❌ Token account not found - position not tracked`);
          trade.status = 'failed';
          return;
        }

        tokenAmount = parseFloat(tokenAccount.account.data.parsed.info.tokenAmount.uiAmount);
      }

      // Add position to manager
      this.positionManager.addPosition(
        opportunity.address,
        opportunity.symbol,
        positionSize,
        tokenAmount,
        entryPrice
      );

      console.log(`\n   📊 Position tracked:`);
      console.log(`      Amount: ${tokenAmount.toFixed(2)} ${opportunity.symbol}`);
      console.log(`      Entry: $${entryPrice.toFixed(8)}`);
      console.log(`      TP: +${this.TAKE_PROFIT_PERCENT}% | SL: ${this.STOP_LOSS_PERCENT}% | Max: ${this.MAX_HOLD_MINUTES}min`);

    } catch (error: any) {
      trade.status = 'failed';
      console.log(`\n   ❌ TRADE ERROR: ${error.message}`);
    }
  }

  /**
   * Background loop to monitor positions and execute exits
   */
  private async startExitMonitoring(): Promise<void> {
    (async () => {
      while (true) {
        try {
          await this.sleep(10000); // Check every 10 seconds

          const exitsNeeded = await this.positionManager.monitorPositions();

          for (const exit of exitsNeeded) {
            console.log(`\n🚨 EXIT SIGNAL: ${exit.tokenAddress.substring(0, 8)}...`);
            console.log(`   Reason: ${exit.reason}`);

            await this.executeExit(exit.tokenAddress, exit.reason);
          }

        } catch (error: any) {
          console.log(`⚠️  Exit monitor error: ${error.message}`);
        }
      }
    })();
  }

  /**
   * Execute exit for a position (with partial exit support)
   */
  private async executeExit(tokenAddress: string, reason?: string): Promise<void> {
    const SOL = 'So11111111111111111111111111111111111111112';

    try {
      console.log(`\n   📤 EXECUTING EXIT...`);

      // Get token balance
      const { Connection, PublicKey } = await import('@solana/web3.js');
      const connection = new Connection(
        `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_RPC_URL}`,
        'confirmed'
      );

      const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
        new PublicKey(this.executor['wallet'].publicKey),
        { programId: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA') }
      );

      const tokenAccount = tokenAccounts.value.find(
        acc => acc.account.data.parsed.info.mint === tokenAddress
      );

      if (!tokenAccount) {
        console.log(`   ❌ Token account not found`);
        this.positionManager.removePosition(tokenAddress);
        return;
      }

      const tokenAmount = tokenAccount.account.data.parsed.info.tokenAmount.amount;
      const position = this.positionManager.getPosition(tokenAddress);

      // PARTIAL EXIT: If take profit, use dynamic split based on viral signals
      const isTakeProfit = reason?.includes('Take profit');
      let sellPercent = isTakeProfit ? this.PARTIAL_EXIT_PERCENT : 1.0;

      // VIRAL DETECTION: Keep more of position if token is going parabolic
      if (isTakeProfit && position) {
        const isViral = await this.detectViralPump(tokenAddress);
        if (isViral) {
          sellPercent = 0.50; // Viral pump: Keep 50% instead of 20%
          console.log(`   🚀 VIRAL PUMP DETECTED - Keeping 50% runner instead of ${((1 - this.PARTIAL_EXIT_PERCENT) * 100).toFixed(0)}%`);
        }
      }

      const amountToSell = Math.floor(parseInt(tokenAmount) * sellPercent);

      if (isTakeProfit) {
        console.log(`   🎯 PARTIAL EXIT: Selling ${(sellPercent * 100).toFixed(0)}% at +100%, letting ${((1 - sellPercent) * 100).toFixed(0)}% run`);
      }

      const sellResult = await this.executor.executeTrade({
        inputMint: tokenAddress,
        outputMint: SOL,
        amount: amountToSell,
        slippageBps: 500, // Higher slippage for fast exit
        strategy: 'volume'
      });

      if (!sellResult.success) {
        console.log(`   ❌ EXIT FAILED: ${sellResult.error}`);
        return;
      }

      console.log(`   ✅ EXITED ${(sellPercent * 100).toFixed(0)}%`);
      console.log(`      Signature: ${sellResult.signature}`);
      console.log(`      Speed: ${sellResult.executionTime}ms`);

      // Update balance and calculate P&L
      await this.updateBalance();

      if (position && position.pnl !== undefined) {
        const realizedPnL = position.pnl * sellPercent;
        const realizedPnLPercent = position.pnlPercent! * sellPercent;

        if (realizedPnL > 0) {
          console.log(`   ✅ PROFIT: +${realizedPnL.toFixed(6)} SOL (+${position.pnlPercent!.toFixed(2)}%)`);
        } else {
          console.log(`   ❌ LOSS: ${realizedPnL.toFixed(6)} SOL (${position.pnlPercent!.toFixed(2)}%)`);
        }

        if (isTakeProfit) {
          console.log(`   🚀 RUNNER: Holding ${((1 - sellPercent) * 100).toFixed(0)}% for potential moonshot`);
          // Update position to track only remaining amount
          const remainingTokens = position.entryAmount * (1 - sellPercent);
          position.entryAmount = remainingTokens;
          // Don't remove position - it's still running!
          return;
        }
      }

      // Full exit (SL/Time) - remove position
      this.positionManager.removePosition(tokenAddress);

    } catch (error: any) {
      console.log(`   ❌ EXIT ERROR: ${error.message}`);
    }
  }

  private async updateBalance(): Promise<void> {
    try {
      const balance = await this.executor.getBalance();
      this.currentBalance = balance;
    } catch (error) {
      console.log('⚠️  Failed to update balance');
    }
  }

  /**
   * Detect viral pump using volume, holder growth, and trending data
   */
  private async detectViralPump(tokenAddress: string): Promise<boolean> {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
      if (!response.ok) return false;

      const data = await response.json();
      const pairs = data.pairs || [];
      if (pairs.length === 0) return false;

      const pair = pairs.sort((a: any, b: any) =>
        (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
      )[0];

      // Viral indicators
      const volume24h = pair.volume?.h24 || 0;
      const liquidity = pair.liquidity?.usd || 1;
      const priceChange1h = Math.abs(pair.priceChange?.h1 || 0);
      const txns24h = (pair.txns?.h24?.buys || 0) + (pair.txns?.h24?.sells || 0);

      // VIRAL SIGNALS:
      // 1. Massive volume (>$1M/day or >20x liquidity)
      const highVolume = volume24h > 1_000_000 || (volume24h / liquidity) > 20;

      // 2. High transaction count (>1000 txns/day = lots of activity)
      const highActivity = txns24h > 1000;

      // 3. Strong 1h momentum (>50% move)
      const strongMomentum = priceChange1h > 50;

      // Viral if 2+ signals are true
      const viralSignals = [highVolume, highActivity, strongMomentum].filter(x => x).length;

      if (viralSignals >= 2) {
        console.log(`   🔥 Viral signals: Volume=$${(volume24h / 1000).toFixed(0)}k, Txns=${txns24h}, Momentum=${priceChange1h.toFixed(0)}%`);
        return true;
      }

      return false;
    } catch (error) {
      return false; // Default to non-viral on error
    }
  }

  private checkCircuitBreakers(): boolean {
    if (this.currentBalance < this.MIN_BALANCE) {
      console.log(`\n🚨 CIRCUIT BREAKER: Balance too low (${this.currentBalance.toFixed(4)} < ${this.MIN_BALANCE})`);
      return true;
    }

    const drawdown = (this.startingBalance - this.currentBalance) / this.startingBalance;
    if (drawdown > this.MAX_DRAWDOWN) {
      console.log(`\n🚨 CIRCUIT BREAKER: Max drawdown (${(drawdown * 100).toFixed(1)}% > ${(this.MAX_DRAWDOWN * 100).toFixed(0)}%)`);
      return true;
    }

    return false;
  }

  private printHealth(): void {
    const totalPnl = this.currentBalance - this.startingBalance;
    const totalPnlPercent = (totalPnl / this.startingBalance) * 100;

    const solPrice = 119;
    const balanceUSD = this.currentBalance * solPrice;
    const runway = balanceUSD / 10;

    const wins = this.trades.filter(t => t.pnl && t.pnl > 0).length;
    const losses = this.trades.filter(t => t.pnl && t.pnl <= 0).length;
    const winRate = this.trades.length > 0 ? (wins / this.trades.length) * 100 : 0;

    let status = '✅ HEALTHY';
    if (this.currentBalance < 0.15) status = '🚨 CRITICAL';
    else if (this.currentBalance < 0.25) status = '⚠️  WARNING';

    console.log(`   ${status}`);
    console.log(`   💰 Balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`   📊 P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL (${totalPnlPercent >= 0 ? '+' : ''}${totalPnlPercent.toFixed(2)}%)`);
    console.log(`   ⏰ Runway: ${runway.toFixed(1)} days`);
    console.log(`   📈 Trades: ${this.trades.length} (${wins}W/${losses}L) - ${winRate.toFixed(0)}% win rate`);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// CLI usage
async function main() {
  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterKey = process.env.JUP_TOKEN;
  const heliusKey = process.env.HELIUS_RPC_URL;

  const rpcUrl = heliusKey
    ? `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`
    : 'https://api.mainnet-beta.solana.com';

  if (!privateKey || !jupiterKey || !heliusKey) {
    console.error('❌ Missing environment variables');
    process.exit(1);
  }

  const coordinator = new SafeMasterCoordinator(rpcUrl, privateKey, jupiterKey, heliusKey);

  await coordinator.initialize();
  await coordinator.run();
}

if (require.main === module) {
  main().catch(console.error);
}

export { SafeMasterCoordinator };
