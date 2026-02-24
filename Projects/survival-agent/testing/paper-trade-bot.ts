/**
 * PAPER TRADING - MASTER COORDINATOR v2.5
 *
 * VERSION HISTORY:
 * v2.0 - Dual-loop architecture, trailing stops, source tracking
 * v2.1 - 3-loss blacklist (auto-blacklist tokens with 3 consecutive losses)
 * v2.2 - Real executor integration, fee tracking, multiple shocked calls
 * v2.3 - MIN_LIQUIDITY raised to $10k, age filter disabled
 * v2.4 - Dynamic fast scanning (7s) for 50%+ profitable positions + rate limit tracking
 *
 * FEATURES:
 * 1. ✅ Dual-loop architecture: Scanner (15s) + Dynamic Monitor (5s/7s)
 * 2. ✅ Tiered exit strategy: Regular stop-loss before TP1, trailing stop after
 * 3. ✅ Peak price tracking with 20% trailing stop from peak after +100%
 * 4. ✅ Scanner source tracking (pumpfun/dexscreener/both)
 * 5. ✅ Up to 10 concurrent positions for better diversification
 * 6. ✅ Jupiter-validated prices and routes (entry + exit)
 * 7. ✅ Proper handling of rugged tokens (no sell route = total loss)
 * 8. ✅ 3-loss blacklist: Auto-blacklist tokens after 3 consecutive losses
 * 9. ✅ Dynamic scan intervals: 7s for 50%+ positions, 5s for others
 * 10. ✅ Rate limit tracking and monitoring
 */

import { OptimizedExecutor } from '../core/optimized-executor';
import { CombinedScannerWebSocket } from '../strategies/combined-scanner-websocket';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';
import { JupiterValidator } from '../core/jupiter-validator';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';
import { ShockedAlphaScanner } from '../strategies/shocked-alpha-scanner';
import { CONFIG } from '../config/paper.config';

interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: 'meme' | 'arbitrage' | 'perp' | 'volume';
  source?: 'pumpfun' | 'dexscreener' | 'both' | 'shocked';
  amountIn: number;
  entryPrice?: number;
  currentPrice?: number;
  peakPrice?: number; // Highest price seen since entry
  tp1Hit?: boolean; // Did we hit +100% take profit?
  signature?: string;
  unrealizedPnl?: number; // Current open P&L in SOL (updated each monitor cycle)
  pnl?: number;
  pnlGross?: number; // P&L before fees
  jitoTipPaid?: number; // Jito tip in SOL (entry + exit)
  priorityFeePaid?: number; // Priority fees in lamports (entry + exit)
  totalFeesPaid?: number; // Total fees in SOL
  status: 'open' | 'closed_profit' | 'closed_loss' | 'failed';
  error?: string;
  exitPrice?: number; // Actual price at exit (for slippage auditing)
  closedAt?: number; // Alias for exitTimestamp — ms since epoch
  exitTimestamp?: number;
  exitReason?: string;
  confidenceScore?: number; // Smart money confidence score (0-100) for backtesting
  shockedScore?: number; // Shocked scanner score for shocked calls
}

class PaperTradeMasterCoordinatorFixed {
  private executor: OptimizedExecutor;
  private scanner: CombinedScannerWebSocket;
  private tracker: SmartMoneyTracker;
  private validator: JupiterValidator;
  private shockedScanner: ShockedAlphaScanner;

  private startingBalance: number;
  private currentBalance: number;
  private trades: TradeLog[] = [];
  private dailyBurnRate = 10;
  private lastCheckTime = new Map<string, number>(); // Track last check per position
  private isPaused = false;
  private totalRefills = 0; // Track how many times we've refilled
  private ruggedTokens: Set<string> = new Set(); // Blacklist of rugged token addresses
  private blacklistedSymbols: Set<string> = new Set(); // Blacklist of symbols with 3 consecutive SL hits
  private symbolSlHits: Map<string, number> = new Map(); // Consecutive SL streak per symbol (resets on win)
  private rateLimitCount = 0; // Track 429 rate limits
  private lastRateLimitTime = 0; // Last time we hit rate limit

  // Trading thresholds - loaded from config (paper.config.ts or mainnet.config.ts)
  private readonly MAX_CONCURRENT_POSITIONS = CONFIG.MAX_CONCURRENT_POSITIONS;
  private readonly MAX_POSITION_SIZE = CONFIG.MAX_POSITION_SIZE;
  private readonly MIN_BALANCE = CONFIG.MIN_BALANCE;
  private readonly MAX_DRAWDOWN = 0.25;
  private readonly MIN_SCORE = CONFIG.MIN_SCORE;
  private readonly MIN_SMART_MONEY_CONFIDENCE = CONFIG.MIN_SMART_MONEY_CONFIDENCE;
  private readonly AUTO_REFILL_THRESHOLD = CONFIG.AUTO_REFILL_THRESHOLD;
  private readonly AUTO_REFILL_AMOUNT = CONFIG.AUTO_REFILL_AMOUNT;

  // Exit thresholds
  private readonly TAKE_PROFIT = CONFIG.TAKE_PROFIT;
  private readonly STOP_LOSS = CONFIG.STOP_LOSS;
  private readonly TRAILING_STOP_PERCENT = CONFIG.TRAILING_STOP_PERCENT;
  private readonly MAX_HOLD_TIME_MS = CONFIG.MAX_HOLD_TIME_MS;
  private readonly MIN_SHOCKED_SCORE = CONFIG.MIN_SHOCKED_SCORE;

  private readonly SCAN_INTERVAL_MS = CONFIG.SCAN_INTERVAL_MS;
  private readonly MONITOR_INTERVAL_MS = CONFIG.MONITOR_INTERVAL_MS;
  private readonly PAPER_TRADE = CONFIG.PAPER_TRADE;
  private readonly TRADES_FILE = CONFIG.TRADES_FILE;
  private readonly STATE_FILE = CONFIG.STATE_FILE;
  private readonly BLACKLIST_FILE = CONFIG.BLACKLIST_FILE;

  constructor(
    rpcUrl: string,
    privateKey: string,
    jupiterApiKey: string,
    heliusApiKey: string
  ) {
    this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey, CONFIG.PAPER_TRADE, CONFIG.USE_JITO);
    this.scanner = new CombinedScannerWebSocket();
    this.tracker = new SmartMoneyTracker();
    this.validator = new JupiterValidator(jupiterApiKey);
    this.shockedScanner = new ShockedAlphaScanner();

    this.startingBalance = 0;
    this.currentBalance = 0;

    console.log(`🤖 Master Coordinator initialized [${CONFIG.MODE_LABEL}]`);
    console.log(CONFIG.PAPER_TRADE
      ? '📄 PAPER TRADING MODE - 1:1 simulation with REAL on-chain validation'
      : '🔴 MAINNET MODE - REAL TRANSACTIONS');
  }

  async initialize(): Promise<void> {
    console.log('\n🔧 Initializing autonomous trading system...\n');

    await this.loadTrades();
    await this.loadState();
    await this.loadBlacklist();

    const check = await this.executor.preFlightCheck();

    if (!check.ready) {
      throw new Error('System not ready. Check pre-flight issues.');
    }

    // MAINNET ONLY: Verify currentBalance against real on-chain SOL.
    // If state file was wiped or stale, the bot would use CONFIG.STARTING_BALANCE
    // (e.g. 0.5 SOL) even if the wallet only has 0.05 SOL — causing massive over-sizing.
    // clamp currentBalance to on-chain free SOL if it's more than 10% higher.
    if (!CONFIG.PAPER_TRADE && check.balance !== undefined) {
      const onChainSol = check.balance;
      const openDeployed = this.trades
        .filter(t => t.status === 'open')
        .reduce((sum, t) => sum + (t.amountIn || 0), 0);
      // free SOL = on-chain - what's deployed in open positions
      const onChainFree = Math.max(0, onChainSol - openDeployed);
      if (this.currentBalance > onChainFree * 1.1) {
        console.warn(`⚠️  BALANCE MISMATCH DETECTED`);
        console.warn(`   State file says: ${this.currentBalance.toFixed(4)} SOL free`);
        console.warn(`   On-chain reality: ${onChainSol.toFixed(4)} SOL total, ~${onChainFree.toFixed(4)} SOL free`);
        console.warn(`   Clamping to on-chain value to prevent over-sizing\n`);
        this.currentBalance = onChainFree;
        this.startingBalance = Math.min(this.startingBalance, onChainSol);
        await this.saveState();
      }
    }

    await this.scanner.initialize();
    await this.shockedScanner.initialize();

    console.log('\n✅ System initialized and ready');
    console.log(`💰 Starting balance: ${this.startingBalance.toFixed(4)} SOL`);
    console.log(`💵 Current balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`🔄 Total refills: ${this.totalRefills}`);
    console.log('🎯 Risk parameters:');
    console.log(`   Max concurrent positions: ${this.MAX_CONCURRENT_POSITIONS}`);
    console.log(`   Max position: ${(this.MAX_POSITION_SIZE * 100).toFixed(0)}%`);
    console.log(`   TP1 (activates trailing): +${(this.TAKE_PROFIT * 100).toFixed(0)}%`);
    console.log(`   Trailing stop: ${(this.TRAILING_STOP_PERCENT * 100).toFixed(0)}% from peak (after TP1)`);
    console.log(`   Stop loss: ${(this.STOP_LOSS * 100).toFixed(0)}% (before TP1)`);
    console.log(`   Max hold: ${this.MAX_HOLD_TIME_MS / 60000} min`);
    console.log(`\n⚡ Timing:`);
    console.log(`   Scanner: Every ${this.SCAN_INTERVAL_MS / 1000}s`);
    console.log(`   Position monitor: Every ${this.MONITOR_INTERVAL_MS / 1000}s (all positions)`);
    if (this.ruggedTokens.size > 0 || this.blacklistedSymbols.size > 0) {
      console.log(`\n🚫 Blacklist: ${this.ruggedTokens.size} rugged address(es), ${this.blacklistedSymbols.size} symbol(s) blocked`);
    }
  }

  async run(): Promise<void> {
    console.log('\n🚀 Starting DUAL-LOOP autonomous trading system...');
    console.log('🔍 Scanner: Every 15s | Monitor: Every 5s (all positions)');
    console.log('💎 Trailing stop from peak after +100% TP1');
    console.log('⚠️  Press Ctrl+C to stop\n');

    // Start both loops concurrently
    await Promise.all([
      this.scannerLoop(),
      this.monitorLoop()
    ]);
  }

  /**
   * Scanner loop - Find new opportunities every 15s
   */
  private async scannerLoop(): Promise<void> {
    let loopCount = 0;

    while (!this.isPaused) {
      loopCount++;
      const startTime = Date.now();

      console.log('============================================================');
      console.log(`SCANNER ${loopCount} - ${new Date().toLocaleTimeString()}`);
      console.log('============================================================\n');

      try {
        // Check Shocked group calls FIRST (priority)
        const shockedOpps = await this.shockedScanner.scan();
        const validShocked = shockedOpps.filter(opp => opp.score >= this.MIN_SHOCKED_SCORE && opp.isCallActive);
        console.log(`   📡 Shocked scanner: ${shockedOpps.length} opportunities found`);
        if (shockedOpps.length > 0) {
          console.log(`   🔍 Shocked details:`);
          shockedOpps.slice(0, 5).forEach(opp => {
            console.log(`      ${opp.symbol}: score=${opp.score}, active=${opp.isCallActive}`);
          });
          console.log();
        }
        console.log(`   ✅ Valid shocked: ${validShocked.length} (score ≥${this.MIN_SHOCKED_SCORE}, active)\n`);

        // Process multiple shocked calls (up to available position slots)
        for (const best of validShocked) {
          const openPositions = this.trades.filter(t => t.status === 'open').length;

          // Stop if at max positions
          if (openPositions >= this.MAX_CONCURRENT_POSITIONS) {
            console.log(`   ⚠️  At max positions (${this.MAX_CONCURRENT_POSITIONS}), skipping remaining shocked calls\n`);
            break;
          }

          // Check blacklist (address and symbol)
          if (this.ruggedTokens.has(best.address)) {
            console.log(`   🚫 SKIPPED: ${best.symbol} address is blacklisted (previously rugged)\n`);
            continue;
          }
          if (this.blacklistedSymbols.has(best.symbol.toUpperCase())) {
            console.log(`   🚫 SKIPPED: ${best.symbol} symbol is blacklisted (3 consecutive SL hits)\n`);
            continue;
          }

          // Check if already holding this token
          const alreadyHolding = this.trades.some(t => t.status === 'open' && t.tokenAddress === best.address);

          if (!alreadyHolding) {
            console.log('\n🎯 SHOCKED GROUP CALL DETECTED!');
            console.log(`   Token: ${best.symbol}`);
            console.log(`   Priority: ${best.priority.toUpperCase()}`);
            console.log(`   Score: ${best.score}/100\n`);

            const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
            const roundTrip = await this.validator.validateRoundTrip(best.address, positionSize);

            if (roundTrip.canBuy && roundTrip.canSell && roundTrip.slippage! < 15) {
              const entryPrice = roundTrip.buyPrice!;

              console.log('   ✅ ALL VALIDATIONS PASSED - EXECUTING SHOCKED TRADE\n');
              
              // Execute trade through executor (paper mode)
              const SOL_MINT = 'So11111111111111111111111111111111111111112';
              const tradeResult = await this.executor.executeTrade({
                inputMint: SOL_MINT,
                outputMint: best.address,
                amount: Math.floor(positionSize * LAMPORTS_PER_SOL),
                slippageBps: 1500, // 15% slippage tolerance
                strategy: 'meme'
              });

              if (!tradeResult.success) {
                console.log(`   ❌ Trade execution failed: ${tradeResult.error}\n`);
                continue; // Skip this trade
              }

              console.log(`   ⚡ Execution time: ${tradeResult.executionTime}ms`);
              console.log(`   🚀 Priority fee: ${tradeResult.priorityFeeUsed} µL`);
              if (tradeResult.retryCount && tradeResult.retryCount > 0) {
                console.log(`   🔄 Retries: ${tradeResult.retryCount}`);
                console.log(`   💰 Total fees: ${tradeResult.totalFeesSpent} µL`);
              }

              this.trades.push({
                timestamp: Date.now(),
                tokenAddress: best.address,
                tokenSymbol: best.symbol,
                strategy: 'meme',
                source: 'shocked',
                amountIn: positionSize,
                entryPrice: entryPrice,
                currentPrice: entryPrice,
                peakPrice: entryPrice,
                tp1Hit: false,
                status: 'open',
                signature: tradeResult.signature!, // Use executor signature
                shockedScore: best.score,
                jitoTipPaid: tradeResult.jitoTipPaid || 0, // Track entry Jito tip
                priorityFeePaid: tradeResult.totalFeesSpent || 0, // Track entry priority fee
                totalFeesPaid: (tradeResult.jitoTipPaid || 0) + ((tradeResult.totalFeesSpent || 0) / LAMPORTS_PER_SOL)
              });

              this.currentBalance -= positionSize;
              await this.saveTrades();
              await this.saveState();
              console.log('   ✅ SHOCKED CALL EXECUTED!\n');
            }
          }
        }

        // If we executed any shocked calls, skip regular scanning
        const shockedTradesThisCycle = this.trades.filter(t =>
          t.source === 'shocked' &&
          t.timestamp > startTime
        ).length;

        if (shockedTradesThisCycle > 0) {
          console.log(`   ✅ Executed ${shockedTradesThisCycle} shocked call(s) this cycle\n`);
          const elapsed = Date.now() - startTime;
          const sleepTime = Math.max(0, this.SCAN_INTERVAL_MS - elapsed);
          console.log(`⏳ Scanner sleeping for ${(sleepTime / 1000).toFixed(1)} seconds...\n`);
          await new Promise(resolve => setTimeout(resolve, sleepTime));
          continue;
        }

        // Step 1: Scan for opportunities
        console.log('1️⃣  Scanning for opportunities...');
        const opportunities = await this.scanner.scan();
        console.log(`   Found ${opportunities.length} potential opportunities`);

        if (opportunities.length === 0) {
          console.log('   ⚠️  No opportunities found this cycle\n');
        } else {
          let qualified = opportunities.filter(opp => opp.score >= this.MIN_SCORE);
          console.log(`   ${qualified.length} meet minimum score (≥${this.MIN_SCORE})\n`);

          if (qualified.length > 0) {
            // Check if we have room for more positions
            const openPositions = this.trades.filter(t => t.status === 'open').length;

            if (openPositions >= this.MAX_CONCURRENT_POSITIONS) {
              console.log(`2️⃣  ⏭️  Max concurrent positions reached (${this.MAX_CONCURRENT_POSITIONS}) - skipping\n`);
            } else {
              // Sort by score (highest first) and filter out already held tokens
              const availableOpps = qualified
                .filter(opp => !this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address))
                .sort((a, b) => b.score - a.score);

              // Try top 5 opportunities (in case first few fail smart money check)
              let traded = false;
              for (const best of availableOpps.slice(0, 5)) {
                if (traded) break;
                // Check blacklist (address and symbol)
                if (this.ruggedTokens.has(best.address)) {
                  console.log(`   🚫 SKIPPED: ${best.symbol} address is blacklisted (previously rugged)\n`);
                  continue;
                }
                if (this.blacklistedSymbols.has(best.symbol.toUpperCase())) {
                  console.log(`   🚫 SKIPPED: ${best.symbol} symbol is blacklisted (3+ SL hits)\n`);
                  continue;
                }

                console.log('2️⃣  Analyzing top opportunity:');
                console.log(`   Token: ${best.symbol} (${best.address.slice(0, 8)}...)`);
                console.log(`   Score: ${best.score}/100`);
                console.log(`   Source: ${best.source || 'unknown'}`);
                console.log(`   Age: ${best.ageMinutes?.toFixed(1) || '?'} min`);
                console.log(`   Signals: ${best.signals.join(', ')}\n`);

                // ALL tokens go through smart money analysis (pump.fun AND dexscreener)
                console.log('3️⃣  Smart money analysis...');
                const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
                const confidence = analysis.confidence;
                console.log(`   Confidence: ${confidence}/100\n`);

                if (confidence < this.MIN_SMART_MONEY_CONFIDENCE) {
                  console.log(`   ⏭️  SKIPPED: Low confidence (${confidence} < ${this.MIN_SMART_MONEY_CONFIDENCE}) - trying next...\n`);
                  continue; // Try next opportunity
                }

                if (confidence >= this.MIN_SMART_MONEY_CONFIDENCE) {
                  console.log('4️⃣  🎯 HIGH CONFIDENCE SIGNAL - VALIDATING TRADE\n');

                  const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
                  console.log(`   Position: ${positionSize.toFixed(4)} SOL (${(this.MAX_POSITION_SIZE * 100).toFixed(1)}%)\n`);

                  // Validate round-trip BEFORE buying
                  const roundTrip = await this.validator.validateRoundTrip(best.address, positionSize);

                  if (!roundTrip.canBuy) {
                    console.log('   ❌ SKIPPED: No buy route\n');
                    continue;
                  }

                  if (!roundTrip.canSell) {
                    console.log('   ❌ SKIPPED: No sell route (would be unable to exit)\n');
                    continue;
                  }

                  // Use REAL Jupiter price, not DexScreener
                  const entryPrice = roundTrip.buyPrice!;
                  console.log(`   💰 Entry price (Jupiter): $${entryPrice.toFixed(8)}`);
                  console.log(`   📊 Round-trip slippage: ${roundTrip.slippage?.toFixed(2)}%\n`);

                  if (roundTrip.slippage! > 15) {
                    console.log('   ⚠️  SKIPPED: Slippage too high (>15%)\n');
                    continue;
                  }

                  console.log('   ✅ ALL VALIDATIONS PASSED - EXECUTING TRADE\n');

                  // Execute trade through executor (paper mode)
                  const SOL_MINT = 'So11111111111111111111111111111111111111112';
                  const tradeResult = await this.executor.executeTrade({
                    inputMint: SOL_MINT,
                    outputMint: best.address,
                    amount: Math.floor(positionSize * LAMPORTS_PER_SOL),
                    slippageBps: 1500, // 15% slippage tolerance
                    strategy: 'meme'
                  });

                  if (!tradeResult.success) {
                    console.log(`   ❌ Trade execution failed: ${tradeResult.error}\n`);
                    continue; // Skip this trade
                  }

                  console.log(`   ⚡ Execution time: ${tradeResult.executionTime}ms`);
                  console.log(`   🚀 Priority fee: ${tradeResult.priorityFeeUsed} µL`);
                  if (tradeResult.retryCount && tradeResult.retryCount > 0) {
                    console.log(`   🔄 Retries: ${tradeResult.retryCount}`);
                    console.log(`   💰 Total fees: ${tradeResult.totalFeesSpent} µL`);
                  }

                  // Simulate the trade
                  this.trades.push({
                    timestamp: Date.now(),
                    tokenAddress: best.address,
                    tokenSymbol: best.symbol,
                    strategy: 'meme',
                    source: best.source,
                    amountIn: positionSize,
                    entryPrice: entryPrice,
                    currentPrice: entryPrice,
                    peakPrice: entryPrice,
                    tp1Hit: false,
                    status: 'open',
                    signature: tradeResult.signature!, // Use executor signature
                    confidenceScore: confidence,
                    jitoTipPaid: tradeResult.jitoTipPaid || 0, // Track entry Jito tip
                    priorityFeePaid: tradeResult.totalFeesSpent || 0, // Track entry priority fee
                    totalFeesPaid: (tradeResult.jitoTipPaid || 0) + ((tradeResult.totalFeesSpent || 0) / LAMPORTS_PER_SOL)
                  });

                  this.currentBalance -= positionSize;
                  await this.saveTrades();
                  await this.saveState();
                  console.log('   ✅ TRADE SIMULATED (with Jupiter-validated prices)\n');
                  traded = true; // Mark as traded, exit loop
                }
              }

              if (!traded) {
                console.log(`   ⚠️  No trades taken - all top 5 opportunities failed validation\n`);
              }
            }
          }
        }

      } catch (error) {
        console.error('❌ Error in scanner loop:', error);
      }

      const elapsed = Date.now() - startTime;
      const sleepTime = Math.max(0, this.SCAN_INTERVAL_MS - elapsed);
      console.log(`⏳ Scanner sleeping for ${(sleepTime / 1000).toFixed(1)} seconds...\n`);
      await new Promise(resolve => setTimeout(resolve, sleepTime));
    }
  }

  /**
   * Monitor loop - Check positions every 5s for fast exits
   */
  private async monitorLoop(): Promise<void> {
    // Wait a bit for scanner to start first
    await new Promise(resolve => setTimeout(resolve, 2000));

    while (!this.isPaused) {
      try {
        const openTrades = this.trades.filter(t => t.status === 'open');

        if (openTrades.length > 0) {
          await this.checkExitsWithTrailingStop();
        }

        // Auto-refill check
        await this.checkAutoRefill();

        // System health check every 10 monitor cycles (~50 seconds)
        if (Math.random() < 0.1) {
          await this.checkHealth();
        }

      } catch (error) {
        console.error('❌ Error in monitor loop:', error);
      }

      await new Promise(resolve => setTimeout(resolve, this.MONITOR_INTERVAL_MS));
    }
  }

  /**
   * 🔥 NEW: Trailing stop from peak after TP1 (+100%)
   */
  private async checkExitsWithTrailingStop(): Promise<void> {
    const openTrades = this.trades.filter(t => t.status === 'open');

    if (openTrades.length === 0) {
      return;
    }

    console.log(`\n💼 Checking ${openTrades.length} open position(s)...\n`);

    for (const trade of openTrades) {
      const holdTime = Date.now() - trade.timestamp;
      const holdMinutes = (holdTime / 60000).toFixed(1);

      // FIXED CHECK INTERVAL - all positions monitored at 5s
      const checkInterval = this.MONITOR_INTERVAL_MS; // 5s for all positions

      // Check if we should skip this position this cycle
      const lastCheck = this.lastCheckTime.get(trade.tokenAddress) || 0;
      const timeSinceCheck = Date.now() - lastCheck;

      if (timeSinceCheck < checkInterval) {
        console.log(`   ⏭️  ${trade.tokenSymbol}: Checked ${(timeSinceCheck/1000).toFixed(1)}s ago (interval: ${(checkInterval/1000).toFixed(0)}s), skipping`);
        continue;
      }

      // Update last check time
      this.lastCheckTime.set(trade.tokenAddress, Date.now());

      // 🔥 FIX #4: Get REAL current price from Jupiter, with DexScreener fallback
      let currentPrice = trade.entryPrice!;
      let priceAvailable = false;

      try {
        const realPrice = await this.validator.getRealExecutablePrice(
          trade.tokenAddress,
          'sell',
          trade.amountIn
        );

        if (realPrice !== null) {
          currentPrice = realPrice;
          priceAvailable = true;
        }
      } catch (error: any) {
        // Track rate limits
        if (error?.message?.includes('429') || error?.message?.includes('Rate limit')) {
          this.rateLimitCount++;
          this.lastRateLimitTime = Date.now();
          console.log(`   ⚠️  Rate limited (total: ${this.rateLimitCount})`);
        }
      }

      // FALLBACK: If Jupiter failed, try DexScreener
      if (!priceAvailable) {
        try {
          const dexPrice = await this.getDexScreenerPrice(trade.tokenAddress);
          if (dexPrice !== null) {
            currentPrice = dexPrice;
            priceAvailable = true;
            console.log(`   ℹ️  Using DexScreener fallback price: $${dexPrice.toFixed(8)}`);
          }
        } catch (error) {
          // DexScreener also failed
        }
      }

      // LAST RESORT: Use last known price if both failed
      if (!priceAvailable && trade.currentPrice && trade.currentPrice > 0) {
        currentPrice = trade.currentPrice;
        priceAvailable = true;
        console.log(`   ⚠️  Using last known price: $${currentPrice.toFixed(8)}`);
      }

      // Update peak price
      if (priceAvailable && currentPrice > 0) {
        if (!trade.peakPrice || currentPrice > trade.peakPrice) {
          trade.peakPrice = currentPrice;
        }
      }

      // Recalculate P&L with fresh price
      let pnlPercent: number;
      let pnlSol: number;

      if (!priceAvailable || currentPrice === 0) {
        pnlPercent = -100;
        pnlSol = -trade.amountIn;
        currentPrice = 0;
      } else {
        trade.currentPrice = currentPrice;
        pnlPercent = ((currentPrice - trade.entryPrice!) / trade.entryPrice!) * 100;
        pnlSol = trade.amountIn * (pnlPercent / 100);
        trade.unrealizedPnl = pnlSol;
      }

      // Check if TP1 hit
      if (pnlPercent >= this.TAKE_PROFIT * 100 && !trade.tp1Hit) {
        trade.tp1Hit = true;
        console.log(`   🎯 TP1 HIT! Trailing stop activated for ${trade.tokenSymbol}`);
      }

      console.log(`   📊 ${trade.tokenSymbol} [${trade.source || 'unknown'}]:`);
      console.log(`      Entry: $${trade.entryPrice!.toFixed(8)} | Current: $${currentPrice.toFixed(8)}`);
      if (trade.peakPrice && trade.peakPrice > trade.entryPrice!) {
        const peakGain = ((trade.peakPrice - trade.entryPrice!) / trade.entryPrice!) * 100;
        console.log(`      Peak: $${trade.peakPrice.toFixed(8)} (+${peakGain.toFixed(2)}%)`);
      }
      console.log(`      P&L: ${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}% (${pnlSol >= 0 ? '+' : ''}${pnlSol.toFixed(4)} SOL)`);
      console.log(`      Hold time: ${holdMinutes} min`);
      if (trade.tp1Hit) {
        console.log(`      Status: 🔥 TRAILING STOP ACTIVE`);
      }

      if (!priceAvailable) {
        console.log(`      ⚠️  Token rugged - no sell route`);
      }

      // Check exit conditions
      let shouldExit = false;
      let exitReason = '';

      // TIERED EXIT LOGIC
      if (!trade.tp1Hit) {
        // Before TP1 - use regular stop loss
        if (pnlPercent <= this.STOP_LOSS * 100) {
          shouldExit = true;
          exitReason = `Stop loss hit (${this.STOP_LOSS * 100}%)`;
        } else if (holdTime >= this.MAX_HOLD_TIME_MS) {
          shouldExit = true;
          exitReason = `Max hold time (${this.MAX_HOLD_TIME_MS / 60000} min)`;
        }
      } else {
        // After TP1 - use trailing stop from peak
        const peakPrice = trade.peakPrice || currentPrice;
        const dropFromPeak = ((peakPrice - currentPrice) / peakPrice);

        if (dropFromPeak >= this.TRAILING_STOP_PERCENT) {
          shouldExit = true;
          exitReason = `Trailing stop: ${(dropFromPeak * 100).toFixed(1)}% drop from peak $${peakPrice.toFixed(8)}`;
        } else if (holdTime >= this.MAX_HOLD_TIME_MS) {
          shouldExit = true;
          exitReason = `Max hold time (${this.MAX_HOLD_TIME_MS / 60000} min)`;
        }
      }

      // 🔥 FIX #5: ACTUALLY EXECUTE THE SELL
      if (shouldExit) {
        console.log(`      🚪 EXITING: ${exitReason}`);

        // Validate sell route one more time before executing
        const sellValidation = await this.validator.validateSellRoute(
          trade.tokenAddress,
          trade.amountIn
        );

        if (!sellValidation.valid) {
          console.log(`      ❌ SELL FAILED: ${sellValidation.error}`);
          
          // Check if it's a REAL rug (no liquidity) vs API/rate limit issue
          if (sellValidation.liquidityInsufficient) {
            // ACTUAL RUG - No liquidity available
            console.log(`      💀 TOTAL LOSS - Token is rugged/illiquid\n`);

            trade.status = 'closed_loss';
            trade.pnlGross = -trade.amountIn; // Gross loss (principal)
            trade.pnl = -trade.amountIn - (trade.totalFeesPaid || 0); // Net loss (principal + entry fees)
            trade.currentPrice = 0;
            trade.exitPrice = 0;
            trade.exitTimestamp = Date.now();
            trade.closedAt = trade.exitTimestamp;
            trade.exitReason = 'No sell route - rugged';
            
            // Add to blacklist (address — immediate rug)
            this.ruggedTokens.add(trade.tokenAddress);
            await this.saveBlacklist();
            console.log(`      🚫 Added ${trade.tokenSymbol} address to blacklist`);

            // Track SL hits for symbol blacklist
            await this.checkAndBlacklistLosers(trade);

            await this.saveTrades();
            // Don't return SOL to balance - it's lost
          } else {
            // API error, rate limit, or network issue - NOT a rug!
            console.log(`      ⚠️  API/Network error - will retry next cycle`);
            console.log(`      Error details: ${sellValidation.error}\n`);
            
            // Don't close position - keep it open and try again next cycle
            // This allows the bot to retry when API recovers
            console.log(`      ↻ Keeping position open for retry\n`);
          }
        } else {
          // REAL MODE: Execute the actual sell swap on-chain before recording anything
          if (!CONFIG.PAPER_TRADE) {
            const SOL_MINT = 'So11111111111111111111111111111111111111112';
            // Use actual wallet token balance - avoids mismatch from price movement since buy
            const actualTokenBalance = await this.executor.getTokenBalance(trade.tokenAddress);
            if (actualTokenBalance === 0) {
              console.log(`      ⚠️  No tokens in wallet for ${trade.tokenSymbol} - marking as closed\n`);
              // Token is gone (rugged/already sold) - close the position at 0
              trade.status = 'closed_loss';
              trade.currentPrice = 0;
              trade.pnl = -trade.amountIn;
              trade.pnlGross = -trade.amountIn;
              this.currentBalance += 0;
              await this.saveTrades();
              return;
            }
            const sellResult = await this.executor.executeTrade({
              inputMint: trade.tokenAddress,
              outputMint: SOL_MINT,
              amount: actualTokenBalance,
              slippageBps: 1500,
              strategy: 'meme'
            });

            if (!sellResult.success) {
              console.log(`      ❌ SELL TX FAILED: ${sellResult.error} - will retry next cycle\n`);
              return;
            }

            console.log(`      ⚡ Sell tx confirmed: ${sellResult.signature}`);
          }

          // Get final sell price
          const finalPrice = sellValidation.priceUsd!;
          const grossPnl = trade.amountIn * ((finalPrice - trade.entryPrice!) / trade.entryPrice!);

          // Add exit fees (Jito tip + priority fee for sell transaction)
          const jitoTipInfo = this.executor.getJitoTipInfo();
          const exitJitoTip = jitoTipInfo.tipSOL;
          const exitPriorityFee = 0.000006; // ~$0.0005 typical priority fee in SOL
          const exitFees = exitJitoTip + exitPriorityFee;

          // Total fees = entry fees + exit fees
          const totalFees = (trade.totalFeesPaid || 0) + exitFees;

          // Net PNL = Gross PNL - Total Fees
          const netPnl = grossPnl - totalFees;

          console.log(`      ✅ SELL EXECUTED`);
          console.log(`      💰 Exit price: $${finalPrice.toFixed(8)}`);
          console.log(`      📊 Gross P&L: ${grossPnl >= 0 ? '+' : ''}${grossPnl.toFixed(4)} SOL`);
          console.log(`      💸 Total fees: ${totalFees.toFixed(8)} SOL (Jito: ${jitoTipInfo.level})`);
          console.log(`      📊 Net P&L: ${netPnl >= 0 ? '+' : ''}${netPnl.toFixed(4)} SOL\n`);

          trade.status = netPnl >= 0 ? 'closed_profit' : 'closed_loss';
          trade.pnlGross = grossPnl;
          trade.pnl = netPnl;
          trade.jitoTipPaid = (trade.jitoTipPaid || 0) + exitJitoTip;
          trade.priorityFeePaid = (trade.priorityFeePaid || 0) + (exitPriorityFee * LAMPORTS_PER_SOL);
          trade.totalFeesPaid = totalFees;
          trade.currentPrice = finalPrice;
          trade.exitPrice = finalPrice;
          trade.exitTimestamp = Date.now();
          trade.closedAt = trade.exitTimestamp;
          trade.exitReason = exitReason;

          // Return SOL to balance (net after fees)
          this.currentBalance += trade.amountIn + netPnl;

          // Track consecutive SL hits for symbol blacklist; reset streak on win
          if (trade.status === 'closed_loss') {
            await this.checkAndBlacklistLosers(trade);
          } else if (trade.status === 'closed_profit') {
            await this.resetSymbolStreak(trade);
          }

          await this.saveTrades();
          await this.saveState();
        }
      } else {
        console.log(`      ⏳ Holding...\n`);
      }
    }

    // Save updated prices to JSON file for status monitor
    await this.saveTrades();
  }

  /**
   * Fetch price from DexScreener as fallback when Jupiter fails
   */
  private async getDexScreenerPrice(tokenAddress: string): Promise<number | null> {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`);
      if (!response.ok) return null;

      const data = await response.json();
      if (!data.pairs || data.pairs.length === 0) return null;

      // Get the pair with highest liquidity
      const bestPair = data.pairs.sort((a: any, b: any) =>
        (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
      )[0];

      const priceUsd = parseFloat(bestPair.priceUsd);
      return isNaN(priceUsd) ? null : priceUsd;
    } catch (error) {
      return null;
    }
  }

  private async checkHealth(): Promise<void> {
    const openTrades = this.trades.filter(t => t.status === 'open');
    const closedTrades = this.trades.filter(t => t.status === 'closed_profit' || t.status === 'closed_loss');
    const wins = this.trades.filter(t => t.status === 'closed_profit').length;
    const losses = this.trades.filter(t => t.status === 'closed_loss').length;
    const winRate = closedTrades.length > 0 ? (wins / closedTrades.length) * 100 : 0;

    const totalPnl = this.currentBalance - this.startingBalance;
    const totalPnlPercent = ((totalPnl / this.startingBalance) * 100);

    // Calculate gross vs net P&L for closed trades
    const grossPnl = closedTrades.reduce((sum, t) => sum + (t.pnlGross || t.pnl || 0), 0);
    const totalFees = closedTrades.reduce((sum, t) => sum + (t.totalFeesPaid || 0), 0);
    const jitoTipInfo = this.executor.getJitoTipInfo();

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 STATUS UPDATE');
    console.log(`💰 Balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`📈 Net P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL (${totalPnlPercent >= 0 ? '+' : ''}${totalPnlPercent.toFixed(1)}%)`);
    if (closedTrades.length > 0) {
      console.log(`   ├─ Gross P&L: ${grossPnl >= 0 ? '+' : ''}${grossPnl.toFixed(4)} SOL`);
      console.log(`   └─ Total fees: -${totalFees.toFixed(6)} SOL (Jito ${jitoTipInfo.level}: $${(jitoTipInfo.tipSOL * 88).toFixed(4)}/trade)`);
    }
    console.log(`📊 Trades: ${this.trades.length} | Open: ${openTrades.length} | Closed: ${closedTrades.length}`);
    console.log(`🎯 Win Rate: ${winRate.toFixed(0)}% (${wins}W/${losses}L)`);

    // Rate limit monitoring
    if (this.rateLimitCount > 0) {
      const timeSinceLastLimit = (Date.now() - this.lastRateLimitTime) / 1000;
      console.log(`⚠️  Rate Limits: ${this.rateLimitCount} total (last: ${timeSinceLastLimit.toFixed(0)}s ago)`);
    }

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }

  async checkAutoRefill(): Promise<void> {
    if (this.currentBalance <= this.AUTO_REFILL_THRESHOLD) {
      this.currentBalance += this.AUTO_REFILL_AMOUNT;
      this.totalRefills++;

      console.log('\n💰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('💵 AUTO-REFILL TRIGGERED');
      console.log(`   Balance was: ${(this.currentBalance - this.AUTO_REFILL_AMOUNT).toFixed(4)} SOL`);
      console.log(`   Added: ${this.AUTO_REFILL_AMOUNT} SOL`);
      console.log(`   New balance: ${this.currentBalance.toFixed(4)} SOL`);
      console.log(`   Total refills: ${this.totalRefills}`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━💰\n');

      await this.saveState();
    }
  }

  async saveTrades() {
    // Calculate total P&L from closed trades only (open trades don't have realized pnl)
    const totalPnl = this.trades
      .filter(t => t.status === 'closed_profit' || t.status === 'closed_loss')
      .reduce((sum, t) => sum + (t.pnl || 0), 0);
    
    const state = {
      balance: this.currentBalance,
      totalPnl,
      totalRefills: this.totalRefills,
      trades: this.trades
    };
    
    await Bun.write(this.TRADES_FILE, JSON.stringify(state, null, 2));
    console.log('💾 Saved trades to JSON');
  }

  async loadTrades() {
    try {
      const content = await Bun.file(this.TRADES_FILE).text();
      const data = JSON.parse(content);
      // Handle both old format (array) and new format (object with trades)
      this.trades = Array.isArray(data) ? data : (data.trades || []);
    } catch {
      this.trades = [];
  }
  }

  async loadBlacklist() {
    try {
      const content = await Bun.file(this.BLACKLIST_FILE).text();
      const data = JSON.parse(content);
      this.ruggedTokens = new Set(data.ruggedTokens || []);
      this.blacklistedSymbols = new Set((data.blacklistedSymbols || []).map((s: string) => s.toUpperCase()));
      const hits: Record<string, number> = data.symbolSlHits || {};
      this.symbolSlHits = new Map(Object.entries(hits));
    } catch {
      this.ruggedTokens = new Set();
      this.blacklistedSymbols = new Set();
      this.symbolSlHits = new Map();
    }
  }

  async saveBlacklist() {
    const data = {
      ruggedTokens: Array.from(this.ruggedTokens),
      blacklistedSymbols: Array.from(this.blacklistedSymbols),
      symbolSlHits: Object.fromEntries(this.symbolSlHits),
      lastUpdated: Date.now()
    };
    await Bun.write(this.BLACKLIST_FILE, JSON.stringify(data, null, 2));
  }

  /**
   * Reset consecutive SL streak for a symbol on a win.
   */
  async resetSymbolStreak(trade: TradeLog) {
    const symbol = trade.tokenSymbol.toUpperCase();
    const prev = this.symbolSlHits.get(symbol) || 0;
    if (prev > 0) {
      this.symbolSlHits.set(symbol, 0);
      console.log(`   ✅ ${symbol} win — consecutive SL streak reset (was ${prev})`);
      await this.saveBlacklist();
    }
  }

  /**
   * Track consecutive SL hits per symbol; blacklist after 3 in a row.
   * A single win resets the streak (see resetSymbolStreak).
   * Also keeps the original address-based 3-consecutive-loss check.
   */
  async checkAndBlacklistLosers(trade: TradeLog) {
    const symbol = trade.tokenSymbol.toUpperCase();

    // Increment consecutive loss streak
    const streak = (this.symbolSlHits.get(symbol) || 0) + 1;
    this.symbolSlHits.set(symbol, streak);
    console.log(`   📉 ${symbol} consecutive SL streak: ${streak}/3`);

    if (streak >= 3 && !this.blacklistedSymbols.has(symbol)) {
      console.log(`\n🚫 BLACKLISTING SYMBOL: ${symbol}`);
      console.log(`   Reason: 3 consecutive stop-losses with no win in between`);
      console.log(`   This symbol will no longer be traded\n`);
      this.blacklistedSymbols.add(symbol);
      await this.saveBlacklist();
    }

    // Also blacklist the address after 3 consecutive losses on same address (original logic)
    const tokenTrades = this.trades
      .filter(t => t.tokenAddress === trade.tokenAddress && (t.status === 'closed_profit' || t.status === 'closed_loss'))
      .sort((a, b) => (b.exitTimestamp || b.timestamp) - (a.exitTimestamp || a.timestamp));

    if (tokenTrades.length >= 3) {
      const lastThree = tokenTrades.slice(0, 3);
      const allLosses = lastThree.every(t => t.status === 'closed_loss');

      if (allLosses && !this.ruggedTokens.has(trade.tokenAddress)) {
        const totalLoss = lastThree.reduce((sum, t) => sum + (t.pnl || 0), 0);
        console.log(`\n🚫 BLACKLISTING ADDRESS: ${symbol} (${trade.tokenAddress})`);
        console.log(`   Reason: 3 consecutive losses on same address (${totalLoss.toFixed(4)} SOL)\n`);
        this.ruggedTokens.add(trade.tokenAddress);
        await this.saveBlacklist();
      }
    }
  }

  async saveState() {
    const state = {
      startingBalance: this.startingBalance,
      currentBalance: this.currentBalance,
      totalRefills: this.totalRefills,
      lastUpdated: Date.now()
    };
    await Bun.write(this.STATE_FILE, JSON.stringify(state, null, 2));
  }

  async loadState() {
    try {
      const content = await Bun.file(this.STATE_FILE).text();
      const state = JSON.parse(content);

      this.startingBalance = state.startingBalance || CONFIG.STARTING_BALANCE;
      this.currentBalance = state.currentBalance || CONFIG.STARTING_BALANCE;
      this.totalRefills = state.totalRefills || 0;

      const closedTrades = this.trades.filter(t => t.status === 'closed_profit' || t.status === 'closed_loss').length;
      const totalPnl = this.currentBalance - this.startingBalance + (this.totalRefills * this.AUTO_REFILL_AMOUNT);

      console.log('📂 RESUMING FROM PREVIOUS SESSION');
      console.log(`   💾 Loaded ${this.trades.length} trades (${closedTrades} closed)`);
      console.log(`   💰 Balance: ${this.currentBalance.toFixed(4)} SOL`);
      console.log(`   📈 Session P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL`);
      console.log(`   🔄 Total refills: ${this.totalRefills}\n`);
    } catch {
      // First run - initialize fresh from config
      this.startingBalance = CONFIG.STARTING_BALANCE;
      this.currentBalance = CONFIG.STARTING_BALANCE;
      this.totalRefills = 0;

      console.log('🆕 First run - initializing fresh state');
      await this.saveState();
    }
  }
}

// Run
async function main() {
  const modeEmoji = CONFIG.PAPER_TRADE ? '🧪' : '🔴';
  console.log(`${modeEmoji} ${CONFIG.MODE_LABEL} - MASTER COORDINATOR v2.5\n`);
  console.log('🚀 FEATURES:');
  console.log('   ⚡ Dual-loop: Scanner (15s) + Monitor (5s) for fast exits');
  console.log('   💎 Trailing stop: 20% from peak after +100% TP1');
  console.log('   📊 Scanner source tracking (pumpfun/dexscreener/both)');
  console.log('   🎯 Up to 10 concurrent positions');
  console.log('   🚫 3-loss blacklist: Auto-block repeat losers');
  console.log('✅ Jupiter-validated prices and routes');
  console.log('✅ Rugged token protection\n');

  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterApiKey = process.env.JUP_TOKEN;
  const heliusApiKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const rpcUrl = CONFIG.RPC_URL.replace('${HELIUS_API_KEY}', heliusApiKey || '');

  if (!privateKey || !jupiterApiKey || !heliusApiKey) {
    console.error('❌ Missing credentials');
    process.exit(1);
  }

  const coordinator = new PaperTradeMasterCoordinatorFixed(
    rpcUrl,
    privateKey,
    jupiterApiKey,
    heliusApiKey
  );

  await coordinator.initialize();
  await coordinator.run();
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
