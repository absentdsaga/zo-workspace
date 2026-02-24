/**
 * REFACTORED BOT EXAMPLE
 *
 * Demonstrates the new architecture principles from @legendaryy:
 * 1. Sub-agents for heavy tasks
 * 2. config.patch > config.apply
 * 3. Circuit breakers for resilience
 * 4. Clean, minimal context in main session
 */

import { SubAgentCoordinator } from '../core/sub-agent-coordinator';
import { globalCircuitBreaker } from '../core/circuit-breaker';
import { TradingBotConfigManager, TradingBotConfig } from '../core/config-manager';
import { OptimizedExecutor } from '../core/optimized-executor';
import { SmartMoneyTracker } from '../strategies/smart-money-tracker';

class RefactoredTradingBot {
  private coordinator: SubAgentCoordinator;
  private executor: OptimizedExecutor;
  private tracker: SmartMoneyTracker;
  private configManager: TradingBotConfigManager;

  constructor(
    rpcUrl: string,
    privateKey: string,
    jupiterApiKey: string,
    heliusApiKey: string
  ) {
    // Initialize with default config
    const defaultConfig: TradingBotConfig = {
      maxConcurrentPositions: 7,
      maxPositionSize: 0.12,
      minBalance: 0.05,
      takeProfit: 1.0,
      stopLoss: -0.30,
      trailingStopPercent: 0.20,
      maxDrawdown: 0.25,
      minScore: 40,
      minSmartMoneyConfidence: 45,
      minShockedScore: 30,
      autoRefillThreshold: 0.03,
      autoRefillAmount: 1.0,
      scanIntervalMs: 15000,
      monitorIntervalMs: 5000,
      maxHoldTimeMs: 3600000,
      paperMode: true,
      useJito: true
    };

    this.configManager = new TradingBotConfigManager(
      defaultConfig,
      '/tmp/trading-bot-config.json'
    );

    this.coordinator = new SubAgentCoordinator();
    this.executor = new OptimizedExecutor(
      rpcUrl,
      privateKey,
      jupiterApiKey,
      heliusApiKey,
      true  // paper mode
    );
    this.tracker = new SmartMoneyTracker();
  }

  /**
   * Main trading loop - CLEAN, minimal context
   */
  async run(): Promise<void> {
    console.log('🚀 Starting refactored trading bot...');
    console.log('📊 Config:', this.configManager.get());

    // Set up queue processor for circuit breaker
    setInterval(() => {
      globalCircuitBreaker.processQueue();
    }, 300000); // Every 5 minutes

    while (true) {
      try {
        await this.scanAndTrade();
        await this.sleep(this.configManager.getValue('scanIntervalMs'));
      } catch (error: any) {
        console.error('❌ Main loop error:', error.message);
        await this.sleep(5000);
      }
    }
  }

  /**
   * Scan for opportunities using sub-agents
   * Main session only receives essential signals
   */
  private async scanAndTrade(): Promise<void> {
    console.log('\n🔍 Scanning for opportunities...');

    // 1️⃣ BEFORE: Inline scanning (bloats context)
    // const pumpTokens = await scanner.scanPumpFun();
    // const dexTokens = await scanner.scanDexScreener();
    // const shockedTokens = await scanner.scanShocked();
    // ... hundreds of KB of API responses in context

    // 2️⃣ AFTER: Sub-agent scanning (clean context)
    const signals = await globalCircuitBreaker.execute(
      'market-scan',
      () => this.coordinator.quickScan(10),
      () => [] // Fallback: no signals
    );

    console.log(`✅ Found ${signals.length} signals`);

    for (const signal of signals) {
      // Skip if confidence too low
      if (signal.confidence < this.configManager.getValue('minSmartMoneyConfidence')) {
        continue;
      }

      // Validate with smart money tracker
      const smartMoney = await globalCircuitBreaker.execute(
        'smart-money-check',
        () => this.tracker.hasSmartMoneyInterest(signal.address),
        () => ({ interested: false, confidence: 0, reasons: ['Service unavailable'] })
      );

      if (!smartMoney.interested) {
        continue;
      }

      console.log(`💎 Strong signal for ${signal.symbol || signal.address.slice(0, 8)}`);
      console.log(`   Score: ${signal.score}, Confidence: ${signal.confidence}`);
      console.log(`   Smart Money: ${smartMoney.confidence}%`);

      // Execute trade (with circuit breaker)
      await this.executeTrade(signal);
    }
  }

  /**
   * Execute trade with circuit breaker protection
   */
  private async executeTrade(signal: any): Promise<void> {
    const config = this.configManager.get();

    // Circuit breaker protects against Jupiter API failures
    await globalCircuitBreaker.execute(
      'jupiter-trade',
      async () => {
        const result = await this.executor.executeTrade({
          inputMint: 'So11111111111111111111111111111111111111112', // SOL
          outputMint: signal.address,
          amount: config.maxPositionSize,
          strategy: 'meme'
        });

        if (result.success) {
          console.log(`✅ Trade executed: ${result.signature}`);
        } else {
          console.error(`❌ Trade failed: ${result.error}`);
        }
      },
      () => {
        console.log('⚠️  Trade queued for retry (Jupiter unavailable)');
      }
    );
  }

  /**
   * Safely update config using .patch()
   */
  updateConfig(updates: Partial<TradingBotConfig>, reason: string): void {
    // 1️⃣ BEFORE: Full overwrite (dangerous)
    // this.config = { ...updates }; // ❌ Lost all other fields!

    // 2️⃣ AFTER: Partial update (safe)
    this.configManager.patch(updates, reason);
  }

  /**
   * Example: Adjust risk based on performance
   */
  async adjustRisk(winRate: number): Promise<void> {
    if (winRate > 0.6) {
      // Increase position size on good performance
      this.updateConfig(
        { maxPositionSize: 0.15 },
        'Increased position size due to 60%+ win rate'
      );
    } else if (winRate < 0.4) {
      // Decrease position size on poor performance
      this.updateConfig(
        { maxPositionSize: 0.08 },
        'Decreased position size due to <40% win rate'
      );
    }
  }

  /**
   * Example: Rollback config on error
   */
  async handleConfigError(): Promise<void> {
    try {
      // Try risky config change
      this.updateConfig(
        { maxConcurrentPositions: 50 }, // Invalid
        'Attempted aggressive scaling'
      );
    } catch (error) {
      // Automatic rollback already happened in ConfigManager
      console.log('❌ Config update failed, automatically rolled back');
    }
  }

  /**
   * View circuit breaker stats
   */
  getCircuitStats(): void {
    const stats = globalCircuitBreaker.getStats();
    console.log('\n📊 Circuit Breaker Stats:');
    console.log(JSON.stringify(stats, null, 2));
  }

  /**
   * View config history
   */
  getConfigHistory(): void {
    const history = this.configManager.getHistory();
    console.log('\n📜 Config History:');
    history.forEach(v => {
      console.log(`  v${v.version} (${new Date(v.timestamp).toISOString()}): ${v.description}`);
    });
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Example usage
async function main() {
  const bot = new RefactoredTradingBot(
    process.env.RPC_URL!,
    process.env.PRIVATE_KEY!,
    process.env.JUPITER_API_KEY!,
    process.env.HELIUS_API_KEY!
  );

  // Show initial state
  console.log('📊 Initial config:', bot.getConfigHistory());

  // Adjust config safely
  bot.updateConfig(
    { minSmartMoneyConfidence: 50 },
    'Raised bar for entry signals'
  );

  // View circuit breaker health
  bot.getCircuitStats();

  // Run bot
  await bot.run();
}

// Uncomment to run
// main().catch(console.error);
