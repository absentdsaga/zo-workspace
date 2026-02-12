/**
 * PAPER TRADING - MASTER COORDINATOR (ADVANCED)
 *
 * FEATURES:
 * 1. ✅ Dual-loop architecture: Scanner (15s) + Monitor (5s)
 * 2. ✅ Tiered exit strategy: Regular stop-loss before TP1, trailing stop after
 * 3. ✅ Peak price tracking with 20% trailing stop from peak after +100%
 * 4. ✅ Scanner source tracking (pumpfun/dexscreener/both)
 * 5. ✅ Up to 10 concurrent positions for better diversification
 * 6. ✅ Jupiter-validated prices and routes (entry + exit)
 * 7. ✅ Proper handling of rugged tokens (no sell route = total loss)
 */

import { OptimizedExecutor } from '../core/optimized-executor';
import { CombinedScannerWebSocket } from '../strategies/combined-scanner-websocket';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';
import { JupiterValidator } from '../core/jupiter-validator';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';
import { ShockedAlphaScanner } from '../strategies/shocked-alpha-scanner';

interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: 'meme' | 'arbitrage' | 'perp' | 'volume';
  source?: 'pumpfun' | 'dexscreener' | 'both';
  amountIn: number;
  entryPrice?: number;
  currentPrice?: number;
  peakPrice?: number; // Highest price seen since entry
  tp1Hit?: boolean; // Did we hit +100% take profit?
  signature?: string;
  pnl?: number;
  status: 'open' | 'closed_profit' | 'closed_loss' | 'failed';
  error?: string;
  exitTimestamp?: number;
  exitReason?: string;
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
  private isPaused = false;

  // Trading thresholds
  private readonly MAX_CONCURRENT_POSITIONS = 10; // Allow up to 10 tokens at once
  private readonly MAX_POSITION_SIZE = 0.08; // 8% of balance (user preference)
  private readonly MIN_BALANCE = 0.05;
  private readonly MAX_DRAWDOWN = 0.25;
  private readonly MIN_SCORE = 40;
  private readonly MIN_SMART_MONEY_CONFIDENCE = 35;

  // Exit thresholds
  private readonly TAKE_PROFIT = 1.0; // 100% gain (TP1 - activates trailing stop)
  private readonly STOP_LOSS = -0.30; // -30% loss (before TP1)
  private readonly TRAILING_STOP_PERCENT = 0.20; // 20% drop from peak (after TP1)
  private readonly MAX_HOLD_TIME_MS = 60 * 60 * 1000; // 60 minutes
  private readonly MIN_SHOCKED_SCORE = 30;

  private readonly SCAN_INTERVAL_MS = 15000; // 15 seconds (find opportunities)
  private readonly MONITOR_INTERVAL_MS = 5000; // 5 seconds (check positions)
  private readonly PAPER_TRADE = true;
  private readonly TRADES_FILE = '/tmp/paper-trades-master.json';

  constructor(
    rpcUrl: string,
    privateKey: string,
    jupiterApiKey: string,
    heliusApiKey: string
  ) {
    this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey);
    this.scanner = new CombinedScannerWebSocket();
    this.tracker = new SmartMoneyTracker();
    this.validator = new JupiterValidator(jupiterApiKey);
    this.shockedScanner = new ShockedAlphaScanner();

    this.startingBalance = 0;
    this.currentBalance = 0;

    console.log('🤖 Master Coordinator FIXED initialized');
    console.log('📄 PAPER TRADING MODE - 1:1 simulation with REAL on-chain validation');
  }

  async initialize(): Promise<void> {
    console.log('\n🔧 Initializing autonomous trading system...\n');

    await this.loadTrades();

    const check = await this.executor.preFlightCheck();

    if (!check.ready) {
      throw new Error('System not ready. Check pre-flight issues.');
    }

    await this.scanner.initialize();
    await this.shockedScanner.initialize();

    this.startingBalance = 0.5;
    this.currentBalance = 0.5;

    console.log('\n✅ System initialized and ready');
    console.log(`💰 Starting balance: ${this.startingBalance.toFixed(4)} SOL`);
    console.log('🎯 Risk parameters:');
    console.log(`   Max concurrent positions: ${this.MAX_CONCURRENT_POSITIONS}`);
    console.log(`   Max position: ${(this.MAX_POSITION_SIZE * 100).toFixed(0)}%`);
    console.log(`   TP1 (activates trailing): +${(this.TAKE_PROFIT * 100).toFixed(0)}%`);
    console.log(`   Trailing stop: ${(this.TRAILING_STOP_PERCENT * 100).toFixed(0)}% from peak (after TP1)`);
    console.log(`   Stop loss: ${(this.STOP_LOSS * 100).toFixed(0)}% (before TP1)`);
    console.log(`   Max hold: ${this.MAX_HOLD_TIME_MS / 60000} min`);
    console.log(`\n⚡ Timing:`);
    console.log(`   Scanner: Every ${this.SCAN_INTERVAL_MS / 1000}s`);
    console.log(`   Position monitor: Every ${this.MONITOR_INTERVAL_MS / 1000}s`);
  }

  async run(): Promise<void> {
    console.log('\n🚀 Starting DUAL-LOOP autonomous trading system...');
    console.log('🔍 Scanner: Every 15s | Monitor: Every 5s');
    console.log('💎 NEW: Trailing stop from peak after +100% TP1');
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

        if (validShocked.length > 0) {
          const best = validShocked[0];
          const openPositions = this.trades.filter(t => t.status === 'open').length;

          // Check if already holding this token or at max positions
          const alreadyHolding = this.trades.some(t => t.status === 'open' && t.tokenAddress === best.address);

          if (!alreadyHolding && openPositions < this.MAX_CONCURRENT_POSITIONS) {
            console.log('\n🎯 SHOCKED GROUP CALL DETECTED!');
            console.log(`   Token: ${best.symbol}`);
            console.log(`   Priority: ${best.priority.toUpperCase()}`);
            console.log(`   Score: ${best.score}/100\n`);

            const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
            const roundTrip = await this.validator.validateRoundTrip(best.address, positionSize);

            if (roundTrip.canBuy && roundTrip.canSell && roundTrip.slippage! < 15) {
              const entryPrice = roundTrip.buyPrice!;

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
                signature: 'PAPER_SHOCKED_' + Date.now()
              });

              this.currentBalance -= positionSize;
              await this.saveTrades();
              console.log('   ✅ SHOCKED CALL EXECUTED!\n');

              // Continue to next scan loop after shocked trade
              const elapsed = Date.now() - startTime;
              const sleepTime = Math.max(0, this.SCAN_INTERVAL_MS - elapsed);
              console.log(`⏳ Scanner sleeping for ${(sleepTime / 1000).toFixed(1)} seconds...\n`);
              await new Promise(resolve => setTimeout(resolve, sleepTime));
              continue;
            }
          }
        }

        // Step 1: Scan for opportunities
        console.log('1️⃣  Scanning for opportunities...');
        const opportunities = await this.scanner.scan();
        console.log(`   Found ${opportunities.length} potential opportunities`);

        if (opportunities.length === 0) {
          console.log('   ⚠️  No opportunities found this cycle\n');
        } else {
          const qualified = opportunities.filter(opp => opp.score >= this.MIN_SCORE);
          console.log(`   ${qualified.length} meet minimum score (≥${this.MIN_SCORE})\n`);

          if (qualified.length > 0) {
            // Check if we have room for more positions
            const openPositions = this.trades.filter(t => t.status === 'open').length;

            if (openPositions >= this.MAX_CONCURRENT_POSITIONS) {
              console.log(`2️⃣  ⏭️  Max concurrent positions reached (${this.MAX_CONCURRENT_POSITIONS}) - skipping\n`);
            } else {
              const best = qualified.find(opp =>
                !this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address)
              );

              if (best) {
                console.log('2️⃣  Analyzing top opportunity:');
                console.log(`   Token: ${best.symbol} (${best.address.slice(0, 8)}...)`);
                console.log(`   Score: ${best.score}/100`);
                console.log(`   Source: ${best.source || 'unknown'}`);
                console.log(`   Signals: ${best.signals.join(', ')}\n`);

                console.log('3️⃣  Smart money analysis...');
                const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
                console.log(`   Confidence: ${analysis.confidence}/100\n`);

                if (analysis.confidence >= this.MIN_SMART_MONEY_CONFIDENCE) {
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
                    signature: 'PAPER_TRADE_' + Date.now()
                  });

                  this.currentBalance -= positionSize;
                  await this.saveTrades();
                  console.log('   ✅ TRADE SIMULATED (with Jupiter-validated prices)\n');
                } else {
                  console.log('4️⃣  ⏭️  Skipping - smart money confidence too low\n');
                }
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

      // 🔥 FIX #4: Get REAL current price from Jupiter, not DexScreener
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
      } catch (error) {
        // Price fetch failed
      }

      // Update peak price
      if (priceAvailable && currentPrice > 0) {
        if (!trade.peakPrice || currentPrice > trade.peakPrice) {
          trade.peakPrice = currentPrice;
        }
      }

      // Calculate P&L
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
          console.log(`      💀 TOTAL LOSS - Token is rugged/illiquid\n`);

          trade.status = 'closed_loss';
          trade.pnl = -trade.amountIn; // Total loss
          trade.currentPrice = 0;
          trade.exitTimestamp = Date.now();
          trade.exitReason = 'No sell route - rugged';
          await this.saveTrades();
          // Don't return SOL to balance - it's lost
        } else {
          // Get final sell price
          const finalPrice = sellValidation.priceUsd!;
          const finalPnl = trade.amountIn * ((finalPrice - trade.entryPrice!) / trade.entryPrice!);

          console.log(`      ✅ SELL EXECUTED (Jupiter-validated)`);
          console.log(`      💰 Exit price: $${finalPrice.toFixed(8)}`);
          console.log(`      📊 Final P&L: ${finalPnl >= 0 ? '+' : ''}${finalPnl.toFixed(4)} SOL\n`);

          trade.status = finalPnl >= 0 ? 'closed_profit' : 'closed_loss';
          trade.pnl = finalPnl;
          trade.currentPrice = finalPrice;
          trade.exitTimestamp = Date.now();
          trade.exitReason = exitReason;

          // Return SOL to balance
          this.currentBalance += trade.amountIn + finalPnl;
          await this.saveTrades();
        }
      } else {
        console.log(`      ⏳ Holding...\n`);
      }
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

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 STATUS UPDATE');
    console.log(`💰 Balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`📈 Total P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL`);
    console.log(`📊 Trades: ${this.trades.length} | Open: ${openTrades.length} | Closed: ${closedTrades.length}`);
    console.log(`🎯 Win Rate: ${winRate.toFixed(0)}% (${wins}W/${losses}L)`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  }

  async saveTrades() {
    await Bun.write(this.TRADES_FILE, JSON.stringify(this.trades, null, 2));
  }

  async loadTrades() {
    try {
      const content = await Bun.file(this.TRADES_FILE).text();
      this.trades = JSON.parse(content);
    } catch {
      this.trades = [];
    }
  }
}

// Run
async function main() {
  console.log('🧪 PAPER TRADING - MASTER COORDINATOR **ADVANCED**\n');
  console.log('🚀 NEW FEATURES:');
  console.log('   ⚡ Dual-loop: Scanner (15s) + Monitor (5s) for fast exits');
  console.log('   💎 Trailing stop: 20% from peak after +100% TP1');
  console.log('   📊 Scanner source tracking (pumpfun/dexscreener/both)');
  console.log('   🎯 Up to 10 concurrent positions');
  console.log('✅ Jupiter-validated prices and routes');
  console.log('✅ Rugged token protection\n');

  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterApiKey = process.env.JUP_TOKEN;
  const heliusApiKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusApiKey}`;

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
