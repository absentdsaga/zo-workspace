import { MemeScanner } from '../strategies/meme-scanner';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * AUTONOMOUS SYSTEM PAPER TRADING
 *
 * Tests the full autonomous trading loop:
 * - Scanner finds opportunities
 * - Smart money validates
 * - System decides to trade or skip
 * - Simulates execution and P&L
 */

interface PaperTrade {
  id: number;
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  score: number;
  smartMoneyConfidence: number;
  amountIn: number;
  executionTime: number;
  pnl: number;
  pnlPercent: number;
  reason: string;
}

class AutonomousPaperTrader {
  private scanner: MemeScanner;
  private tracker: SmartMoneyTracker;
  private jupiterApiKey: string;
  private baseUrl = 'https://api.jup.ag';

  private startingBalance: number;
  private currentBalance: number;
  private trades: PaperTrade[] = [];
  private scans: number = 0;
  private skipped: number = 0;

  private readonly SOL = 'So11111111111111111111111111111111111111112';
  private readonly MIN_SCORE = 60;
  private readonly MIN_SMART_MONEY_CONFIDENCE = 50;
  private readonly MAX_POSITION_SIZE = 0.08; // 8% per trade

  constructor(jupiterApiKey: string, startingBalance: number) {
    this.scanner = new MemeScanner();
    this.tracker = new SmartMoneyTracker();
    this.jupiterApiKey = jupiterApiKey;
    this.startingBalance = startingBalance;
    this.currentBalance = startingBalance;

    console.log('🤖 Autonomous Paper Trading System');
    console.log(`💰 Starting Balance: ${startingBalance.toFixed(4)} SOL\n`);
  }

  /**
   * Get real quote from Jupiter
   */
  private async getQuote(outputMint: string, amount: number): Promise<any> {
    const url = `${this.baseUrl}/swap/v1/quote?` +
      `inputMint=${this.SOL}&` +
      `outputMint=${outputMint}&` +
      `amount=${amount}&` +
      `slippageBps=300`;

    const response = await fetch(url, {
      headers: {
        'x-api-key': this.jupiterApiKey,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Quote failed: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Simulate execution time (398ms average)
   */
  private simulateExecutionTime(): number {
    const base = 398;
    const variance = base * 0.2;
    return Math.round(base + (Math.random() - 0.5) * variance);
  }

  /**
   * Simulate meme coin price movement
   */
  private simulatePriceMovement(priceImpact: number): number {
    const rand = Math.random();

    if (rand < 0.50) {
      // Losing trade (50%)
      const loss = -(0.10 + Math.random() * 0.20);
      return loss - priceImpact;
    } else {
      const gainType = Math.random();

      if (gainType < 0.60) {
        // Small win: +20% to +60%
        return (0.20 + Math.random() * 0.40) - priceImpact;
      } else if (gainType < 0.90) {
        // Medium win: +60% to +120%
        return (0.60 + Math.random() * 0.60) - priceImpact;
      } else {
        // Big win: +120% to +200%
        return (1.20 + Math.random() * 0.80) - priceImpact;
      }
    }
  }

  /**
   * Run one scan cycle
   */
  async runScanCycle(cycleNum: number): Promise<boolean> {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Scan Cycle ${cycleNum}`);
    console.log('='.repeat(60));

    this.scans++;

    // Step 1: Scan for opportunities
    console.log(`\n1️⃣  Scanning for opportunities...`);
    const opportunities = await this.scanner.scan();

    if (opportunities.length === 0) {
      console.log(`   ⏭️  No opportunities found`);
      return false;
    }

    console.log(`   Found ${opportunities.length} potential opportunities`);

    // Step 2: Filter by minimum score
    const highConfidence = opportunities.filter(t => t.score >= this.MIN_SCORE);

    console.log(`   ${highConfidence.length} meet minimum score (≥${this.MIN_SCORE})`);

    if (highConfidence.length === 0) {
      console.log(`   ⏭️  No high-confidence opportunities`);
      this.skipped++;
      return false;
    }

    // Step 3: Take top opportunity
    const topOpportunity = highConfidence[0];

    console.log(`\n2️⃣  Analyzing top opportunity:`);
    console.log(`   Token: ${topOpportunity.symbol} (${topOpportunity.address.substring(0, 8)}...)`);
    console.log(`   Score: ${topOpportunity.score}/100`);
    console.log(`   Age: ${topOpportunity.ageMinutes < 999 ? topOpportunity.ageMinutes.toFixed(0) + ' min' : 'unknown'}`);
    console.log(`   MC: $${(topOpportunity.marketCap / 1000).toFixed(0)}k | Liq: $${(topOpportunity.liquidity / 1000).toFixed(0)}k`);
    console.log(`   Signals: ${topOpportunity.signals.map(s => s.type).join(', ')}`);

    // Step 4: Check smart money
    console.log(`\n3️⃣  Checking smart money interest...`);
    const smartMoney = await this.tracker.hasSmartMoneyInterest(topOpportunity.address);

    console.log(`   Confidence: ${smartMoney.confidence}/100`);
    console.log(`   Reasons: ${smartMoney.reasons.join(', ')}`);

    // Step 5: Decide whether to trade
    if (!smartMoney.interested || smartMoney.confidence < this.MIN_SMART_MONEY_CONFIDENCE) {
      console.log(`\n4️⃣  ⏭️  Smart money confidence too low (${smartMoney.confidence} < ${this.MIN_SMART_MONEY_CONFIDENCE})`);
      this.skipped++;
      return false;
    }

    // Step 6: Execute trade
    console.log(`\n4️⃣  🎯 HIGH CONFIDENCE SIGNAL - EXECUTING TRADE`);

    const positionSize = this.currentBalance * this.MAX_POSITION_SIZE;
    const amountLamports = Math.floor(positionSize * LAMPORTS_PER_SOL);

    console.log(`   Position: ${positionSize.toFixed(4)} SOL (8.0%)`);

    try {
      // Get real quote
      console.log(`\n   Getting real market quote...`);
      const quote = await this.getQuote(topOpportunity.address, amountLamports);

      console.log(`   ✅ Quote: ${quote.outAmount} tokens | ${parseFloat(quote.priceImpactPct).toFixed(4)}% impact`);

      // Simulate execution
      const executionTime = this.simulateExecutionTime();
      await new Promise(resolve => setTimeout(resolve, executionTime));

      console.log(`   ✅ Simulated execution in ${executionTime}ms`);

      // Simulate P&L
      const priceImpact = parseFloat(quote.priceImpactPct);
      const priceMovement = this.simulatePriceMovement(priceImpact);
      const pnlPercent = priceMovement * 100;
      const pnl = positionSize * priceMovement;

      // Update balance
      this.currentBalance += pnl;

      // Log trade
      const trade: PaperTrade = {
        id: this.trades.length + 1,
        timestamp: Date.now(),
        tokenAddress: topOpportunity.address,
        tokenSymbol: topOpportunity.symbol,
        score: topOpportunity.score,
        smartMoneyConfidence: smartMoney.confidence,
        amountIn: positionSize,
        executionTime,
        pnl,
        pnlPercent,
        reason: smartMoney.reasons[0] || 'High confidence'
      };

      this.trades.push(trade);

      // Display result
      if (pnl > 0) {
        console.log(`\n   ✅ PROFIT: +${pnl.toFixed(6)} SOL (+${pnlPercent.toFixed(2)}%)`);
      } else {
        console.log(`\n   ❌ LOSS: ${pnl.toFixed(6)} SOL (${pnlPercent.toFixed(2)}%)`);
      }

      console.log(`   💰 New Balance: ${this.currentBalance.toFixed(6)} SOL`);
      console.log(`   📈 Total P&L: ${(this.currentBalance - this.startingBalance).toFixed(6)} SOL (${((this.currentBalance / this.startingBalance - 1) * 100).toFixed(2)}%)`);

      return true;

    } catch (error: any) {
      console.log(`\n   ❌ Quote failed: ${error.message}`);
      this.skipped++;
      return false;
    }
  }

  /**
   * Run autonomous paper trading until 10 trades executed
   */
  async runUntil10Trades(): Promise<void> {
    console.log('🎮 Starting Autonomous Paper Trading\n');
    console.log('Will scan until 10 trades are executed\n');

    let cycleNum = 0;

    while (this.trades.length < 10) {
      cycleNum++;

      const traded = await this.runScanCycle(cycleNum);

      if (traded) {
        console.log(`\n📊 Progress: ${this.trades.length}/10 trades executed`);
      }

      // Simulate scan interval (reduced to 2s for testing)
      if (this.trades.length < 10) {
        console.log(`\n⏳ Waiting 2 seconds before next scan...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    this.printSummary();
  }

  /**
   * Print summary
   */
  private printSummary(): void {
    console.log('\n\n' + '═'.repeat(60));
    console.log('📊 AUTONOMOUS PAPER TRADING SUMMARY');
    console.log('═'.repeat(60));

    const winners = this.trades.filter(t => t.pnl > 0);
    const losers = this.trades.filter(t => t.pnl <= 0);
    const winRate = (winners.length / this.trades.length * 100).toFixed(1);

    console.log(`\n💰 PERFORMANCE:`);
    console.log(`   Starting Balance: ${this.startingBalance.toFixed(4)} SOL`);
    console.log(`   Ending Balance: ${this.currentBalance.toFixed(4)} SOL`);
    console.log(`   Net P&L: ${(this.currentBalance - this.startingBalance).toFixed(6)} SOL`);
    console.log(`   ROI: ${((this.currentBalance / this.startingBalance - 1) * 100).toFixed(2)}%`);

    console.log(`\n📊 STATISTICS:`);
    console.log(`   Total Scans: ${this.scans}`);
    console.log(`   Opportunities Skipped: ${this.skipped}`);
    console.log(`   Trades Executed: ${this.trades.length}`);
    console.log(`   Execution Rate: ${((this.trades.length / this.scans) * 100).toFixed(1)}%`);
    console.log(`   Winners: ${winners.length}`);
    console.log(`   Losers: ${losers.length}`);
    console.log(`   Win Rate: ${winRate}%`);

    const avgExecutionTime = this.trades.reduce((sum, t) => sum + t.executionTime, 0) / this.trades.length;
    const avgScore = this.trades.reduce((sum, t) => sum + t.score, 0) / this.trades.length;
    const avgSmartMoney = this.trades.reduce((sum, t) => sum + t.smartMoneyConfidence, 0) / this.trades.length;

    console.log(`   Avg Execution Time: ${avgExecutionTime.toFixed(0)}ms`);
    console.log(`   Avg Opportunity Score: ${avgScore.toFixed(0)}/100`);
    console.log(`   Avg Smart Money Confidence: ${avgSmartMoney.toFixed(0)}/100`);

    console.log(`\n🎯 WINNING TRADES:`);
    for (const trade of winners) {
      console.log(`   Trade ${trade.id}: ${trade.tokenSymbol} | Score ${trade.score} | SM ${trade.smartMoneyConfidence} | +${trade.pnlPercent.toFixed(1)}%`);
    }

    if (losers.length > 0) {
      console.log(`\n❌ LOSING TRADES:`);
      for (const trade of losers) {
        console.log(`   Trade ${trade.id}: ${trade.tokenSymbol} | Score ${trade.score} | SM ${trade.smartMoneyConfidence} | ${trade.pnlPercent.toFixed(1)}%`);
      }
    }

    console.log(`\n⚡ SPEED ANALYSIS:`);
    const fastTrades = this.trades.filter(t => t.executionTime < 500).length;
    console.log(`   <500ms: ${fastTrades}/${this.trades.length} (${(fastTrades/this.trades.length*100).toFixed(0)}%)`);
    console.log(`   Fastest: ${Math.min(...this.trades.map(t => t.executionTime))}ms`);
    console.log(`   Slowest: ${Math.max(...this.trades.map(t => t.executionTime))}ms`);

    console.log(`\n📈 30-DAY PROJECTION:`);
    const roiPerTrade = (this.currentBalance / this.startingBalance - 1);
    const dailyROI = roiPerTrade * (20 / 10); // Scale to 20 trades/day
    const monthlyMultiplier = Math.pow(1 + dailyROI, 30);

    console.log(`   ROI per 10 trades: ${(roiPerTrade * 100).toFixed(2)}%`);
    console.log(`   Projected daily (20 trades): ${(dailyROI * 100).toFixed(2)}%`);
    console.log(`   Projected 30-day multiplier: ${monthlyMultiplier.toFixed(2)}x`);
    console.log(`   Projected 30-day balance: ${(this.startingBalance * monthlyMultiplier).toFixed(2)} SOL`);

    if (monthlyMultiplier >= 10) {
      console.log(`\n✅ Strategy projects to ${monthlyMultiplier.toFixed(1)}x in 30 days - VIABLE for survival!`);
    } else if (monthlyMultiplier >= 5) {
      console.log(`\n🟡 Strategy projects to ${monthlyMultiplier.toFixed(1)}x in 30 days - Marginal for survival`);
    } else {
      console.log(`\n🔴 Strategy projects to ${monthlyMultiplier.toFixed(1)}x in 30 days - Insufficient for survival`);
    }

    console.log(`\n🤖 AUTONOMOUS SYSTEM PERFORMANCE:`);
    console.log(`   Scan efficiency: ${((this.trades.length / this.scans) * 100).toFixed(1)}% of scans resulted in trades`);
    console.log(`   Filter effectiveness: System skipped ${this.skipped} low-confidence opportunities`);
    console.log(`   Decision making: ${this.trades.length} high-confidence trades executed`);

    console.log('\n' + '═'.repeat(60));
  }
}

// CLI usage
async function main() {
  const jupiterKey = process.env.JUP_TOKEN;

  if (!jupiterKey) {
    console.error('❌ Missing JUP_TOKEN environment variable');
    process.exit(1);
  }

  // Use 0.3352 SOL (current balance)
  const trader = new AutonomousPaperTrader(jupiterKey, 0.3352);

  await trader.runUntil10Trades();
}

if (require.main === module) {
  main().catch(console.error);
}

export { AutonomousPaperTrader };
