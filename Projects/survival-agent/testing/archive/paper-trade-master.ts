/**
 * PAPER TRADING - MASTER COORDINATOR
 *
 * Runs the EXACT same master-coordinator.ts logic but in paper trading mode
 * - Same scanner (MemeScanner)
 * - Same thresholds (score ≥60, smart money ≥35)
 * - Same position sizing (10% max)
 * - Same scan interval (30 seconds)
 *
 * Only difference: Trades are simulated, no real SOL spent
 */

import { OptimizedExecutor } from '../core/optimized-executor';
import { MemeScanner } from '../strategies/meme-scanner';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: 'meme' | 'arbitrage' | 'perp' | 'volume';
  amountIn: number;
  entryPrice?: number;
  currentPrice?: number;
  signature?: string;
  pnl?: number;
  status: 'open' | 'closed_profit' | 'closed_loss' | 'failed';
  error?: string;
  exitTimestamp?: number;
  exitReason?: string;
}

interface SystemHealth {
  balance: number;
  startingBalance: number;
  totalPnl: number;
  totalPnlPercent: number;
  runway: number;
  trades: number;
  wins: number;
  losses: number;
  winRate: number;
  avgExecutionTime: number;
  status: 'healthy' | 'warning' | 'critical' | 'paused';
}

class PaperTradeMasterCoordinator {
  private executor: OptimizedExecutor;
  private scanner: MemeScanner;
  private tracker: SmartMoneyTracker;

  private startingBalance: number;
  private currentBalance: number;
  private trades: TradeLog[] = [];
  private dailyBurnRate = 10;
  private isPaused = false;

  // EXACT SAME THRESHOLDS AS MASTER-COORDINATOR
  private readonly MAX_POSITION_SIZE = 0.12; // 12% of balance
  private readonly MIN_BALANCE = 0.05; // Emergency stop at 0.05 SOL
  private readonly MAX_DRAWDOWN = 0.25; // 25% drawdown = pause
  private readonly MIN_SCORE = 60; // Only trade opportunities with score ≥60
  private readonly MIN_SMART_MONEY_CONFIDENCE = 35; // Same as master-coordinator

  // Exit thresholds
  private readonly TAKE_PROFIT = 1.0; // 100% gain
  private readonly STOP_LOSS = -0.30; // -30% loss
  private readonly MAX_HOLD_TIME_MS = 60 * 60 * 1000; // 60 minutes

  // Scan interval
  private readonly SCAN_INTERVAL_MS = 30000; // 30 seconds

  // PAPER TRADING MODE
  private readonly PAPER_TRADE = true;

  constructor(
    rpcUrl: string,
    privateKey: string,
    jupiterApiKey: string,
    heliusApiKey: string
  ) {
    this.executor = new OptimizedExecutor(rpcUrl, privateKey, jupiterApiKey, heliusApiKey);
    this.scanner = new MemeScanner();
    this.tracker = new SmartMoneyTracker();

    this.startingBalance = 0;
    this.currentBalance = 0;

    console.log('🤖 Master Coordinator initialized');
    console.log('📄 PAPER TRADING MODE - 1:1 simulation of real trading');
  }

  async initialize(): Promise<void> {
    console.log('\n🔧 Initializing autonomous trading system...\n');

    const check = await this.executor.preFlightCheck();

    if (!check.ready) {
      throw new Error('System not ready. Check pre-flight issues.');
    }

    // PAPER TRADING: Use fixed starting balance instead of real wallet
    this.startingBalance = 0.5; // Fixed 0.5 SOL for paper trading
    this.currentBalance = 0.5;

    console.log('\n✅ System initialized and ready');
    console.log(`💰 Starting balance: ${this.startingBalance.toFixed(4)} SOL`);
    console.log('🎯 Risk parameters:');
    console.log(`   Max position: ${(this.MAX_POSITION_SIZE * 100).toFixed(0)}%`);
    console.log(`   Min score: ${this.MIN_SCORE}`);
    console.log(`   Smart money threshold: ${this.MIN_SMART_MONEY_CONFIDENCE}`);
    console.log(`   Max drawdown: ${(this.MAX_DRAWDOWN * 100).toFixed(0)}%`);
    console.log(`   Emergency stop: ${this.MIN_BALANCE} SOL`);
  }

  async run(): Promise<void> {
    console.log('\n🚀 Starting autonomous trading loop...');
    console.log(`🔄 Scanning every ${this.SCAN_INTERVAL_MS / 1000} seconds`);
    console.log('🤖 Will auto-execute on high-confidence signals');
    console.log('📄 PAPER TRADING: All trades simulated\n');
    console.log('⚠️  Press Ctrl+C to stop\n');

    let loopCount = 0;

    while (!this.isPaused) {
      loopCount++;
      const startTime = Date.now();

      console.log('============================================================');
      console.log(`Loop ${loopCount} - ${new Date().toLocaleTimeString()}`);
      console.log('============================================================\n');

      try {
        // Step 1: Scan for opportunities
        console.log('1️⃣  Scanning for opportunities...');
        const opportunities = await this.scanner.scan();
        console.log(`   Found ${opportunities.length} potential opportunities`);

        if (opportunities.length === 0) {
          console.log('   ⚠️  No opportunities found this cycle\n');
        } else {
          // Filter by minimum score
          let qualified = opportunities.filter(opp => opp.score >= this.MIN_SCORE);
          console.log(`   ${qualified.length} meet minimum score (≥${this.MIN_SCORE})\n`);

          // NEW: Exclude smart-money-only signals (v2.0 upgrade)
          const beforeSourceFilter = qualified.length;
          qualified = qualified.filter(opp => (opp as any).source !== 'dexscreener');
          const excluded = beforeSourceFilter - qualified.length;
          if (excluded > 0) {
            console.log(`   ⏭️  Excluded ${excluded} smart-money-only signal(s)`);
          }
          console.log(`   ${qualified.length} qualified after filters\n`);

          if (qualified.length > 0) {
            // Check if we already have an open position in any of the top candidates
            const alreadyHeld = qualified.filter(opp =>
              this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address)
            );

            if (alreadyHeld.length === qualified.length) {
              console.log('2️⃣  ⏭️  All qualified tokens already held - skipping\n');
            } else {
              // Take first token we don't already own
              const best = qualified.find(opp =>
                !this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address)
              );

              if (best) {
                console.log('2️⃣  Analyzing top opportunity:');
                console.log(`   Token: ${best.symbol} (${best.address.slice(0, 8)}...)`);
                console.log(`   Score: ${best.score}/100`);
                console.log(`   Age: ${best.ageMinutes} minutes`);
                console.log(`   Signals: ${best.signals.join(', ')}\n`);

                // Step 3: Check smart money
                console.log('3️⃣  Smart money analysis...');
                const analysis = await this.tracker.hasSmartMoneyInterest(best.address);
                console.log(`   Confidence: ${analysis.confidence}/100`);
                console.log(`   Reasons: ${analysis.reasons.join(', ')}\n`);

                // Step 4: Execute if both thresholds met
                if (analysis.confidence >= this.MIN_SMART_MONEY_CONFIDENCE) {
                  console.log('4️⃣  🎯 HIGH CONFIDENCE SIGNAL - EXECUTING TRADE');

                  const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
                  console.log(`   Position: ${positionSize.toFixed(4)} SOL (${(this.MAX_POSITION_SIZE * 100).toFixed(1)}%)\n`);

                  if (this.PAPER_TRADE) {
                    console.log('   📄 PAPER TRADING - SIMULATING TRADE...\n');

                    // Get real entry price from DexScreener
                    let entryPrice = 0;
                    try {
                      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${best.address}`);
                      const data = await response.json();

                      if (data.pairs && data.pairs.length > 0) {
                        const bestPair = data.pairs.sort((a: any, b: any) =>
                          (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
                        )[0];
                        entryPrice = parseFloat(bestPair.priceUsd || '0');
                      }
                    } catch (error) {
                      console.log('   ⚠️  Could not fetch entry price, skipping trade\n');
                      continue;
                    }

                    if (entryPrice === 0) {
                      console.log('   ⚠️  Invalid entry price, skipping trade\n');
                      continue;
                    }

                    console.log(`   💰 Entry price: $${entryPrice.toFixed(8)}\n`);

                    // Simulate the trade
                    this.trades.push({
                      timestamp: Date.now(),
                      tokenAddress: best.address,
                      tokenSymbol: best.symbol,
                      strategy: 'meme',
                      amountIn: positionSize,
                      entryPrice: entryPrice,
                      currentPrice: entryPrice,
                      status: 'open',
                      signature: 'PAPER_TRADE_' + Date.now()
                    });

                    // Reduce balance
                    this.currentBalance -= positionSize;

                    console.log('   ✅ TRADE SIMULATED SUCCESSFULLY\n');
                  }
                } else {
                  console.log('4️⃣  ⏭️  Skipping - smart money confidence too low\n');
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('❌ Error in trading loop:', error);
      }

      // Step 2b: Check exit conditions for open positions
      await this.checkExits();

      // Step 5: System health
      await this.checkHealth();

      // Sleep until next scan
      const elapsed = Date.now() - startTime;
      const sleepTime = Math.max(0, this.SCAN_INTERVAL_MS - elapsed);
      console.log(`⏳ Sleeping for ${(sleepTime / 1000).toFixed(1)} seconds...\n`);
      await new Promise(resolve => setTimeout(resolve, sleepTime));
    }
  }

  private async checkExits(): Promise<void> {
    const openTrades = this.trades.filter(t => t.status === 'open');

    if (openTrades.length === 0) {
      return;
    }

    console.log(`\n💼 Checking ${openTrades.length} open position(s)...\n`);

    for (const trade of openTrades) {
      const holdTime = Date.now() - trade.timestamp;
      const holdMinutes = (holdTime / 60000).toFixed(1);

      // Fetch real price from DexScreener
      let currentPrice = trade.entryPrice!;
      let priceAvailable = false;

      try {
        const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${trade.tokenAddress}`);
        const data = await response.json();

        if (data.pairs && data.pairs.length > 0) {
          // Get the pair with highest liquidity
          const bestPair = data.pairs.sort((a: any, b: any) =>
            (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
          )[0];

          currentPrice = parseFloat(bestPair.priceUsd || '0');
          priceAvailable = true;
        }
      } catch (error) {
        // Price fetch failed, token likely rugged
      }

      // If price unavailable (rugged token), mark as -100% loss
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

      console.log(`   📊 ${trade.tokenSymbol}:`);
      console.log(`      Entry: $${trade.entryPrice!.toFixed(8)} | Current: $${currentPrice.toFixed(8)}`);
      console.log(`      P&L: ${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}% (${pnlSol >= 0 ? '+' : ''}${pnlSol.toFixed(4)} SOL)`);
      console.log(`      Hold time: ${holdMinutes} min`);
      if (!priceAvailable) {
        console.log(`      ⚠️  Token rugged/delisted - no price data`);
      }

      // Check exit conditions
      let shouldExit = false;
      let exitReason = '';

      if (pnlPercent >= this.TAKE_PROFIT * 100) {
        shouldExit = true;
        exitReason = `Take profit hit (+${this.TAKE_PROFIT * 100}%)`;
      } else if (pnlPercent <= this.STOP_LOSS * 100) {
        shouldExit = true;
        exitReason = `Stop loss hit (${this.STOP_LOSS * 100}%)`;
      } else if (holdTime >= this.MAX_HOLD_TIME_MS) {
        shouldExit = true;
        exitReason = `Max hold time (${this.MAX_HOLD_TIME_MS / 60000} min)`;
      }

      if (shouldExit) {
        console.log(`      🚪 EXITING: ${exitReason}`);

        // Close position
        trade.status = pnlPercent >= 0 ? 'closed_profit' : 'closed_loss';
        trade.pnl = pnlSol;
        trade.exitTimestamp = Date.now();
        trade.exitReason = exitReason;

        // Return SOL to balance
        this.currentBalance += trade.amountIn + pnlSol;

        console.log(`      ✅ Position closed\n`);
      } else {
        console.log(`      ⏳ Holding...\n`);
      }
    }
  }

  private async checkHealth(): Promise<void> {
    console.log('5️⃣  System health:');

    // Calculate stats
    const openTrades = this.trades.filter(t => t.status === 'open');
    const closedTrades = this.trades.filter(t => t.status === 'closed_profit' || t.status === 'closed_loss');
    const wins = this.trades.filter(t => t.status === 'closed_profit').length;
    const losses = this.trades.filter(t => t.status === 'closed_loss').length;
    const winRate = closedTrades.length > 0 ? (wins / closedTrades.length) * 100 : 0;

    const totalPnl = this.currentBalance - this.startingBalance;
    const totalPnlPercent = ((totalPnl / this.startingBalance) * 100);

    const solPrice = 119; // Approximate
    const balanceUsd = this.currentBalance * solPrice;
    const runway = balanceUsd / this.dailyBurnRate;

    // Check circuit breakers
    let status: 'healthy' | 'warning' | 'critical' | 'paused' = 'healthy';

    if (this.currentBalance < this.MIN_BALANCE) {
      status = 'critical';
      console.log('   🚨 CRITICAL: Balance below emergency threshold!');
      this.isPaused = true;
    } else if (totalPnlPercent < -this.MAX_DRAWDOWN * 100) {
      status = 'critical';
      console.log('   🚨 CRITICAL: Max drawdown exceeded!');
      this.isPaused = true;
    } else if (this.currentBalance < this.startingBalance * 0.90) {
      status = 'warning';
      console.log('   ⚠️  WARNING: Balance down >10%');
    } else {
      console.log('   ✅ Status: HEALTHY');
    }

    console.log(`   💰 Balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`   📊 P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL (${totalPnlPercent >= 0 ? '+' : ''}${totalPnlPercent.toFixed(2)}%)`);
    console.log(`   ⏰ Runway: ${runway.toFixed(1)} days`);
    console.log(`   📈 Total Trades: ${this.trades.length} | Open: ${openTrades.length} | Closed: ${closedTrades.length} (${wins}W/${losses}L) - ${winRate.toFixed(0)}% win rate\n`);
  }
}

// Run the paper trading system
async function main() {
  console.log('🧪 PAPER TRADING - MASTER COORDINATOR 1:1 SIMULATION\n');

  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterApiKey = process.env.JUP_TOKEN;
  const heliusApiKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusApiKey}`;

  if (!privateKey || !jupiterApiKey || !heliusApiKey) {
    console.error('❌ Missing credentials in environment');
    console.error('Required: SOLANA_PRIVATE_KEY, JUP_TOKEN, HELIUS_API_KEY');
    process.exit(1);
  }

  console.log('✅ Credentials loaded from environment\n');

  const coordinator = new PaperTradeMasterCoordinator(
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
