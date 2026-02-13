/**
 * SIMPLE PAPER TRADING BOT
 *
 * No executor, no real transactions - pure simulation with Jupiter validation
 * Combines Pump.fun WebSocket + DexScreener with real Jupiter price checking
 */

import { CombinedScannerWebSocket } from '../strategies/combined-scanner-websocket';
import { JupiterValidator } from '../core/jupiter-validator';
import { ShockedAlphaScanner } from '../strategies/shocked-alpha-scanner';

interface PaperTrade {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  amountSol: number;
  entryPrice: number;
  status: 'open' | 'closed';
  exitPrice?: number;
  exitTimestamp?: number;
  pnl?: number;
  exitReason?: string;
  isRunner?: boolean; // 20% runner after TP hit
  partialExitPrice?: number; // Price at which 80% was sold
}

class SimplePaperTrader {
  private scanner: CombinedScannerWebSocket;
  private shockedScanner: ShockedAlphaScanner;
  private validator: JupiterValidator;

  private balance: number = 0.5; // Start with 0.5 SOL
  private trades: PaperTrade[] = [];

  private readonly POSITION_SIZE = 0.04; // 0.04 SOL per trade
  private readonly MIN_SCORE = 40;
  private readonly SHOCKED_MIN_SCORE = 30; // Lower threshold for group calls
  private readonly TAKE_PROFIT = 1.0; // 100%
  private readonly STOP_LOSS = -0.30; // -30%
  private readonly MAX_HOLD_MS = 60 * 60 * 1000; // 60 min
  private readonly TRADES_FILE = '/tmp/paper-trades.json';

  constructor() {
    this.scanner = new CombinedScannerWebSocket();
    this.shockedScanner = new ShockedAlphaScanner();
    this.validator = new JupiterValidator(); // No API key needed for public endpoint
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

  async initialize() {
    console.log('🤖 Simple Paper Trader initializing...\n');
    await this.loadTrades();
    await this.scanner.initialize();
    await this.shockedScanner.initialize();

    console.log('✅ Scanner ready (Pump.fun WebSocket + DexScreener)');
    console.log(`💰 Starting balance: ${this.balance.toFixed(4)} SOL\n`);
    console.log('📊 Trading parameters:');
    console.log(`   Position size: ${this.POSITION_SIZE} SOL`);
    console.log(`   Regular min score: ${this.MIN_SCORE}`);
    console.log(`   Shocked min score: ${this.SHOCKED_MIN_SCORE} (prioritized!)`);
    console.log(`   Take profit: +${this.TAKE_PROFIT * 100}%`);
    console.log(`   Stop loss: ${this.STOP_LOSS * 100}%`);
    console.log(`   Max hold: ${this.MAX_HOLD_MS / 60000} min\n`);

    const openTrades = this.trades.filter(t => t.status === 'open').length;
    if (openTrades > 0) {
      console.log(`📂 Loaded ${openTrades} existing open positions\n`);
    }
  }

  async run() {
    console.log('🚀 Starting paper trading loop...\n');

    while (true) {
      try {
        // Check exits first
        await this.checkExits();

        // Look for new opportunities
        await this.scanAndTrade();

        // Status update
        this.printStatus();

        // Wait before next scan
        await new Promise(resolve => setTimeout(resolve, 30000)); // 30 seconds

      } catch (error: any) {
        console.error('Error in trading loop:', error.message);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  private async scanAndTrade() {
    const openTrades = this.trades.filter(t => t.status === 'open').length;

    if (openTrades >= 3) {
      return; // Max 3 open positions
    }

    if (this.balance < this.POSITION_SIZE) {
      console.log('⚠️  Insufficient balance for new trades');
      return;
    }

    // Check Shocked group calls FIRST (priority)
    const shockedOpps = await this.shockedScanner.scan();
    const validShocked = shockedOpps.filter(opp => opp.score >= this.SHOCKED_MIN_SCORE);

    if (validShocked.length > 0) {
      const best = validShocked[0];
      await this.executeTrade(best.address, best.symbol, best.score, 'SHOCKED GROUP');
      return;
    }

    // Fall back to regular scanner
    const opportunities = await this.scanner.scan();
    const sorted = opportunities
      .filter(opp => opp.score >= this.MIN_SCORE)
      .sort((a, b) => b.score - a.score);

    if (sorted.length === 0) {
      return;
    }

    const best = sorted[0];
    await this.executeTrade(best.address, best.symbol, best.score, best.source);
  }

  private async executeTrade(address: string, symbol: string, score: number, source: string) {
    // Validate with Jupiter (silently)
    const roundTrip = await this.validator.validateRoundTrip(
      address,
      this.POSITION_SIZE
    );

    if (!roundTrip.canBuy || !roundTrip.canSell) {
      return; // Skip silently
    }

    // Only log when we're actually buying
    console.log(`\n🎯 BUYING: ${symbol} (Score: ${score})`);
    console.log(`   Address: ${address}`);
    console.log(`   Source: ${source}`);

    // Execute paper trade
    const trade: PaperTrade = {
      timestamp: Date.now(),
      tokenAddress: address,
      tokenSymbol: symbol,
      amountSol: this.POSITION_SIZE,
      entryPrice: roundTrip.buyPrice!,
      status: 'open'
    };

    this.trades.push(trade);
    this.balance -= this.POSITION_SIZE;

    console.log(`   ✅ Paper trade executed!`);
    console.log(`   💰 Entry price: $${trade.entryPrice.toFixed(8)}`);
    console.log(`   📊 Slippage: ${roundTrip.slippage?.toFixed(2)}%`);
    console.log(`   💵 Balance: ${this.balance.toFixed(4)} SOL\n`);

    await this.saveTrades();
  }

  private async checkExits() {
    const openTrades = this.trades.filter(t => t.status === 'open');

    for (const trade of openTrades) {
      const holdTime = Date.now() - trade.timestamp;

      // Get current price from Jupiter
      const currentPrice = await this.validator.getRealExecutablePrice(
        trade.tokenAddress,
        'sell',
        trade.amountSol
      );

      if (!currentPrice) {
        // Token rugged - can't sell
        trade.status = 'closed';
        trade.exitTimestamp = Date.now();
        trade.exitReason = 'RUGGED - No sell route';
        trade.pnl = -trade.amountSol;

        console.log(`\n💀 ${trade.tokenSymbol} RUGGED`);
        console.log(`   Loss: -${trade.amountSol.toFixed(4)} SOL\n`);
        await this.saveTrades();
        continue;
      }

      const pnlPercent = ((currentPrice - trade.entryPrice) / trade.entryPrice);

      let shouldExit = false;
      let reason = '';

      if (pnlPercent >= this.TAKE_PROFIT) {
        shouldExit = true;
        reason = 'TAKE PROFIT';
      } else if (pnlPercent <= this.STOP_LOSS) {
        shouldExit = true;
        reason = 'STOP LOSS';
      } else if (holdTime >= this.MAX_HOLD_MS) {
        shouldExit = true;
        reason = 'MAX HOLD TIME';
      }

      if (shouldExit) {
        const pnlSol = trade.amountSol * pnlPercent;

        // TAKE PROFIT: Sell 80%, keep 20% as runner
        if (reason === 'TAKE PROFIT' && !trade.isRunner) {
          const sellAmount = trade.amountSol * 0.8;
          const runnerAmount = trade.amountSol * 0.2;
          const sellPnl = sellAmount * pnlPercent;

          // Create runner position
          const runner: PaperTrade = {
            timestamp: Date.now(),
            tokenAddress: trade.tokenAddress,
            tokenSymbol: trade.tokenSymbol,
            amountSol: runnerAmount,
            entryPrice: trade.entryPrice,
            status: 'open',
            isRunner: true,
            partialExitPrice: currentPrice
          };

          this.trades.push(runner);

          // Close original position (80% sold)
          trade.status = 'closed';
          trade.exitPrice = currentPrice;
          trade.exitTimestamp = Date.now();
          trade.exitReason = 'TAKE PROFIT (80% sold, 20% runner)';
          trade.pnl = sellPnl;

          this.balance += sellAmount + sellPnl;

          console.log(`\n✅ ${trade.tokenSymbol} - TAKE PROFIT`);
          console.log(`   Entry: $${trade.entryPrice.toFixed(8)}`);
          console.log(`   Exit: $${currentPrice.toFixed(8)}`);
          console.log(`   💰 80% Sold: +${sellPnl.toFixed(4)} SOL (+${(pnlPercent * 100).toFixed(1)}%)`);
          console.log(`   🏃 20% Runner: ${runnerAmount.toFixed(4)} SOL (letting it ride)`);
          console.log(`   Balance: ${this.balance.toFixed(4)} SOL\n`);

        } else {
          // STOP LOSS, MAX HOLD, or RUNNER exit: Close 100%
          trade.status = 'closed';
          trade.exitPrice = currentPrice;
          trade.exitTimestamp = Date.now();
          trade.exitReason = reason;
          trade.pnl = pnlSol;

          this.balance += trade.amountSol + pnlSol;

          const emoji = pnlSol >= 0 ? '✅' : '❌';
          console.log(`\n${emoji} ${trade.tokenSymbol} - ${reason}${trade.isRunner ? ' (RUNNER)' : ''}`);
          console.log(`   Entry: $${trade.entryPrice.toFixed(8)}`);
          console.log(`   Exit: $${currentPrice.toFixed(8)}`);
          console.log(`   P&L: ${pnlSol >= 0 ? '+' : ''}${pnlSol.toFixed(4)} SOL (${pnlPercent >= 0 ? '+' : ''}${(pnlPercent * 100).toFixed(1)}%)`);
          console.log(`   Balance: ${this.balance.toFixed(4)} SOL\n`);
        }

        await this.saveTrades();
      }
    }
  }

  private printStatus() {
    const openTrades = this.trades.filter(t => t.status === 'open');
    const closedTrades = this.trades.filter(t => t.status === 'closed');
    const wins = closedTrades.filter(t => (t.pnl || 0) > 0).length;
    const losses = closedTrades.filter(t => (t.pnl || 0) <= 0).length;
    const totalPnl = closedTrades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const winRate = closedTrades.length > 0 ? (wins / closedTrades.length) * 100 : 0;

    console.log('━'.repeat(60));
    console.log('📊 STATUS UPDATE');
    console.log(`💰 Balance: ${this.balance.toFixed(4)} SOL`);
    console.log(`📈 Total P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL`);
    console.log(`📊 Trades: ${this.trades.length} | Open: ${openTrades.length} | Closed: ${closedTrades.length}`);
    console.log(`🎯 Win Rate: ${winRate.toFixed(0)}% (${wins}W/${losses}L)`);
    console.log('━'.repeat(60) + '\n');
  }
}

// Run
async function main() {
  console.log('🧪 SIMPLE PAPER TRADER\n');
  console.log('✅ Pump.fun WebSocket + DexScreener');
  console.log('✅ Jupiter price validation');
  console.log('✅ No credentials required\n');

  const trader = new SimplePaperTrader();
  await trader.initialize();
  await trader.run();
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
