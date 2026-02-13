import { OptimizedExecutor } from './optimized-executor';
import { MemeScanner } from '../strategies/meme-scanner';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';
import { LAMPORTS_PER_SOL } from '@solana/web3.js';

/**
 * MASTER COORDINATOR - AUTONOMOUS TRADING SYSTEM
 *
 * Ties together all components for fully automated trading:
 * - Continuous scanning for opportunities
 * - Automated execution on high-confidence signals
 * - Risk management and circuit breakers
 * - Health monitoring and P&L tracking
 *
 * NO MANUAL INTERVENTION REQUIRED
 */

interface TradeLog {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: 'meme' | 'arbitrage' | 'perp' | 'volume';
  amountIn: number;
  signature?: string;
  pnl?: number;
  status: 'pending' | 'success' | 'failed';
  error?: string;
}

interface SystemHealth {
  balance: number;
  startingBalance: number;
  totalPnl: number;
  totalPnlPercent: number;
  runway: number; // days
  trades: number;
  wins: number;
  losses: number;
  winRate: number;
  avgExecutionTime: number;
  status: 'healthy' | 'warning' | 'critical' | 'paused';
}

class MasterCoordinator {
  private executor: OptimizedExecutor;
  private scanner: MemeScanner;
  private tracker: SmartMoneyTracker;

  private startingBalance: number;
  private currentBalance: number;
  private trades: TradeLog[] = [];
  private dailyBurnRate = 10; // $10/day in SOL
  private isPaused = false;

  // Risk management thresholds
  private readonly MAX_POSITION_SIZE = 0.10; // 10% of balance
  private readonly MIN_BALANCE = 0.05; // Emergency stop at 0.05 SOL
  private readonly MAX_DRAWDOWN = 0.25; // 25% drawdown = pause
  private readonly MIN_SCORE = 60; // Only trade opportunities with score ≥60
  private readonly MIN_SMART_MONEY_CONFIDENCE = 35; // LOWERED: For meme coins, we need to be early

  // Scan interval
  private readonly SCAN_INTERVAL_MS = 30000; // 30 seconds

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
    console.log('⚙️  Autonomous trading mode');
  }

  /**
   * Initialize system and verify readiness
   */
  async initialize(): Promise<void> {
    console.log('\n🔧 Initializing autonomous trading system...\n');

    // Pre-flight check
    const check = await this.executor.preFlightCheck();

    if (!check.ready) {
      throw new Error('System not ready. Check pre-flight issues.');
    }

    // Set starting balance
    this.startingBalance = check.balance;
    this.currentBalance = check.balance;

    console.log('\n✅ System initialized and ready');
    console.log(`💰 Starting balance: ${this.startingBalance.toFixed(4)} SOL`);
    console.log(`🎯 Risk parameters:`);
    console.log(`   Max position: ${(this.MAX_POSITION_SIZE * 100).toFixed(0)}%`);
    console.log(`   Min score: ${this.MIN_SCORE}`);
    console.log(`   Max drawdown: ${(this.MAX_DRAWDOWN * 100).toFixed(0)}%`);
    console.log(`   Emergency stop: ${this.MIN_BALANCE} SOL`);
  }

  /**
   * Main autonomous trading loop
   */
  async run(): Promise<void> {
    console.log('\n🚀 Starting autonomous trading loop...\n');
    console.log('🔄 Scanning every 30 seconds');
    console.log('🤖 Will auto-execute on high-confidence signals');
    console.log('⚠️  Press Ctrl+C to stop\n');

    let loopCount = 0;

    while (true) {
      try {
        loopCount++;
        console.log(`\n${'='.repeat(60)}`);
        console.log(`Loop ${loopCount} - ${new Date().toLocaleTimeString()}`);
        console.log('='.repeat(60));

        // Check if system should pause
        if (this.isPaused) {
          console.log('⏸️  System paused - waiting for manual intervention');
          await this.sleep(60000); // Check every minute
          continue;
        }

        // Update current balance
        await this.updateBalance();

        // Check circuit breakers
        const shouldPause = this.checkCircuitBreakers();
        if (shouldPause) {
          this.isPaused = true;
          console.log('\n🚨 CIRCUIT BREAKER TRIGGERED - SYSTEM PAUSED');
          await this.sendHealthAlert('critical');
          continue;
        }

        // 1. Scan for opportunities
        console.log('\n1️⃣  Scanning for opportunities...');
        const opportunities = await this.scanner.scan();

        console.log(`   Found ${opportunities.length} potential opportunities`);

        // 2. Filter by score
        const highConfidence = opportunities.filter(t => t.score >= this.MIN_SCORE);

        console.log(`   ${highConfidence.length} meet minimum score (≥${this.MIN_SCORE})`);

        if (highConfidence.length === 0) {
          console.log('   ⏭️  No high-confidence opportunities, waiting...');
          await this.sleep(this.SCAN_INTERVAL_MS);
          continue;
        }

        // 3. Check smart money interest for top opportunity
        const topOpportunity = highConfidence[0]; // Already sorted by score

        console.log(`\n2️⃣  Analyzing top opportunity:`);
        console.log(`   Token: ${topOpportunity.symbol} (${topOpportunity.address.substring(0, 8)}...)`);
        console.log(`   Score: ${topOpportunity.score}/100`);
        console.log(`   Age: ${topOpportunity.ageMinutes} minutes`);
        console.log(`   Signals: ${topOpportunity.signals.map(s => s.type).join(', ')}`);

        const smartMoney = await this.tracker.hasSmartMoneyInterest(topOpportunity.address);

        console.log(`\n3️⃣  Smart money analysis:`);
        console.log(`   Confidence: ${smartMoney.confidence}/100`);
        console.log(`   Reasons: ${smartMoney.reasons.join(', ')}`);

        // 4. Execute if smart money is interested
        if (smartMoney.interested && smartMoney.confidence >= this.MIN_SMART_MONEY_CONFIDENCE) {
          console.log(`\n4️⃣  🎯 HIGH CONFIDENCE SIGNAL - EXECUTING TRADE`);

          await this.executeTrade(topOpportunity);
        } else {
          console.log(`\n4️⃣  ⏭️  Smart money confidence too low (${smartMoney.confidence} < ${this.MIN_SMART_MONEY_CONFIDENCE})`);
        }

        // 5. Print health status
        console.log('\n5️⃣  System health:');
        const health = this.getHealth();
        this.printHealth(health);

        // 6. Sleep before next scan
        console.log(`\n⏳ Sleeping for ${this.SCAN_INTERVAL_MS / 1000} seconds...`);
        await this.sleep(this.SCAN_INTERVAL_MS);

      } catch (error: any) {
        console.error(`\n❌ Error in main loop: ${error.message}`);
        console.log('   Continuing in 60 seconds...');
        await this.sleep(60000);
      }
    }
  }

  /**
   * Execute a trade
   */
  private async executeTrade(opportunity: any): Promise<void> {
    // Calculate position size
    const positionSize = Math.min(
      this.currentBalance * this.MAX_POSITION_SIZE,
      this.currentBalance * 0.08 // Start conservative with 8%
    );

    const amountLamports = Math.floor(positionSize * LAMPORTS_PER_SOL);

    console.log(`   Position: ${positionSize.toFixed(4)} SOL (${((positionSize / this.currentBalance) * 100).toFixed(1)}%)`);

    // Log trade
    const tradeLog: TradeLog = {
      timestamp: Date.now(),
      tokenAddress: opportunity.address,
      tokenSymbol: opportunity.symbol,
      strategy: 'meme',
      amountIn: positionSize,
      status: 'pending'
    };

    this.trades.push(tradeLog);

    try {
      // Execute with optimized executor
      const result = await this.executor.executeTrade({
        inputMint: 'So11111111111111111111111111111111111111112', // SOL
        outputMint: opportunity.address,
        amount: amountLamports,
        slippageBps: 300, // 3% slippage for meme coins
        strategy: 'meme'
      });

      if (result.success) {
        tradeLog.status = 'success';
        tradeLog.signature = result.signature;

        console.log(`\n✅ TRADE EXECUTED SUCCESSFULLY`);
        console.log(`   Signature: ${result.signature}`);
        console.log(`   Speed: ${result.executionTime}ms`);
        console.log(`   View: https://solscan.io/tx/${result.signature}`);

        // TODO: Monitor for exit signal
        // For now, we'll implement exit monitoring in a separate component

      } else {
        tradeLog.status = 'failed';
        tradeLog.error = result.error;

        console.log(`\n❌ TRADE FAILED`);
        console.log(`   Error: ${result.error}`);
      }

    } catch (error: any) {
      tradeLog.status = 'failed';
      tradeLog.error = error.message;

      console.log(`\n❌ TRADE EXECUTION ERROR`);
      console.log(`   Error: ${error.message}`);
    }
  }

  /**
   * Update current balance
   */
  private async updateBalance(): Promise<void> {
    try {
      const balance = await this.executor.getBalance();
      this.currentBalance = balance;
    } catch (error) {
      console.log('⚠️  Failed to update balance');
    }
  }

  /**
   * Check circuit breakers
   */
  private checkCircuitBreakers(): boolean {
    // 1. Emergency stop - balance too low
    if (this.currentBalance < this.MIN_BALANCE) {
      console.log(`\n🚨 CIRCUIT BREAKER: Balance below minimum (${this.currentBalance.toFixed(4)} < ${this.MIN_BALANCE} SOL)`);
      return true;
    }

    // 2. Max drawdown exceeded
    const drawdown = (this.startingBalance - this.currentBalance) / this.startingBalance;
    if (drawdown > this.MAX_DRAWDOWN) {
      console.log(`\n🚨 CIRCUIT BREAKER: Max drawdown exceeded (${(drawdown * 100).toFixed(1)}% > ${(this.MAX_DRAWDOWN * 100).toFixed(0)}%)`);
      return true;
    }

    // 3. Five consecutive losses
    const recentTrades = this.trades.slice(-5);
    if (recentTrades.length === 5 && recentTrades.every(t => t.status === 'failed')) {
      console.log(`\n🚨 CIRCUIT BREAKER: 5 consecutive failed trades`);
      return true;
    }

    return false;
  }

  /**
   * Get system health
   */
  private getHealth(): SystemHealth {
    const totalPnl = this.currentBalance - this.startingBalance;
    const totalPnlPercent = (totalPnl / this.startingBalance) * 100;

    const wins = this.trades.filter(t => t.status === 'success').length;
    const losses = this.trades.filter(t => t.status === 'failed').length;
    const winRate = this.trades.length > 0 ? (wins / this.trades.length) * 100 : 0;

    // Calculate runway (in days)
    const solPrice = 119; // Approximate SOL price in USD
    const balanceUSD = this.currentBalance * solPrice;
    const runway = balanceUSD / this.dailyBurnRate;

    // Determine status
    let status: 'healthy' | 'warning' | 'critical' | 'paused' = 'healthy';

    if (this.isPaused) {
      status = 'paused';
    } else if (this.currentBalance < 0.1 || runway < 5) {
      status = 'critical';
    } else if (this.currentBalance < 0.2 || runway < 10) {
      status = 'warning';
    }

    return {
      balance: this.currentBalance,
      startingBalance: this.startingBalance,
      totalPnl,
      totalPnlPercent,
      runway,
      trades: this.trades.length,
      wins,
      losses,
      winRate,
      avgExecutionTime: 0, // TODO: Calculate from executor
      status
    };
  }

  /**
   * Print health status
   */
  private printHealth(health: SystemHealth): void {
    const statusIcon = {
      healthy: '✅',
      warning: '⚠️',
      critical: '🚨',
      paused: '⏸️'
    }[health.status];

    console.log(`   ${statusIcon} Status: ${health.status.toUpperCase()}`);
    console.log(`   💰 Balance: ${health.balance.toFixed(4)} SOL`);
    console.log(`   📊 P&L: ${health.totalPnl >= 0 ? '+' : ''}${health.totalPnl.toFixed(4)} SOL (${health.totalPnlPercent >= 0 ? '+' : ''}${health.totalPnlPercent.toFixed(2)}%)`);
    console.log(`   ⏰ Runway: ${health.runway.toFixed(1)} days`);
    console.log(`   📈 Trades: ${health.trades} (${health.wins}W/${health.losses}L) - ${health.winRate.toFixed(0)}% win rate`);
  }

  /**
   * Send health alert (placeholder for future notification system)
   */
  private async sendHealthAlert(level: 'warning' | 'critical'): Promise<void> {
    const health = this.getHealth();

    console.log(`\n🚨 HEALTH ALERT (${level.toUpperCase()}):`);
    this.printHealth(health);

    // TODO: Implement actual notification (email, SMS, Discord, etc.)
  }

  /**
   * Sleep utility
   */
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
    console.error('❌ Missing required environment variables');
    console.error('   SOLANA_PRIVATE_KEY:', !!privateKey);
    console.error('   JUP_TOKEN:', !!jupiterKey);
    console.error('   HELIUS_RPC_URL:', !!heliusKey);
    process.exit(1);
  }

  const coordinator = new MasterCoordinator(rpcUrl, privateKey, jupiterKey, heliusKey);

  // Initialize
  await coordinator.initialize();

  // Start autonomous trading
  await coordinator.run();
}

if (require.main === module) {
  main().catch(console.error);
}

export { MasterCoordinator };
