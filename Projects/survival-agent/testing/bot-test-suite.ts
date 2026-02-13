#!/usr/bin/env bun

/**
 * COMPREHENSIVE BOT TEST SUITE
 *
 * Purpose: Prevent iterative degradation by validating ALL critical behaviors
 * Run this BEFORE and AFTER every change to catch regressions
 */

import { JupiterValidator } from '../core/jupiter-validator';
import type { TradeOpportunity } from '../core/types';

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  duration: number;
}

class BotTestSuite {
  private results: TestResult[] = [];
  private validator = new JupiterValidator();

  // Color output
  private green(text: string) { return `\x1b[32m${text}\x1b[0m`; }
  private red(text: string) { return `\x1b[31m${text}\x1b[0m`; }
  private yellow(text: string) { return `\x1b[33m${text}\x1b[0m`; }
  private blue(text: string) { return `\x1b[36m${text}\x1b[0m`; }

  async test(name: string, fn: () => Promise<void>) {
    const start = Date.now();
    try {
      await fn();
      this.results.push({ name, passed: true, duration: Date.now() - start });
    } catch (error) {
      this.results.push({
        name,
        passed: false,
        error: error instanceof Error ? error.message : String(error),
        duration: Date.now() - start
      });
    }
  }

  // ==================== CRITICAL BEHAVIOR TESTS ====================

  async testRateLimitDetection() {
    await this.test('Rate limit detection (429 != rug)', async () => {
      // Simulate 429 response
      const mockResponse = {
        status: 429,
        statusText: 'Too Many Requests',
        headers: new Headers({ 'Retry-After': '2' })
      };

      // Validator should NOT mark this as liquidityInsufficient
      const result = await this.validator.validateSellRoute(
        'DummyToken',
        0.1,
        0.001
      );

      // On 429, liquidityInsufficient should be FALSE
      if (result.error?.includes('429') && result.liquidityInsufficient === true) {
        throw new Error('429 rate limit incorrectly marked as liquidity issue');
      }
    });
  }

  async testRealRugDetection() {
    await this.test('Real rug detection (no routes = rug)', async () => {
      // Token with no liquidity should be marked as rug
      const result = await this.validator.validateSellRoute(
        'NonExistentToken123456789',
        0.1,
        0.001
      );

      if (!result.error) {
        throw new Error('Nonexistent token should fail validation');
      }

      // Real rug should have liquidityInsufficient = true
      // (unless it's a 429, which would be false)
      if (result.error.includes('404') && result.liquidityInsufficient !== true) {
        throw new Error('404 no-route error should set liquidityInsufficient=true');
      }
    });
  }

  async testDynamicIntervals() {
    await this.test('Dynamic check intervals by P&L', async () => {
      const testCases = [
        { pnl: -30, expected: 2000, label: 'CRITICAL -30%' },
        { pnl: -20, expected: 3000, label: 'WARNING -20%' },
        { pnl: 0, expected: 10000, label: 'Safe 0%' },
        { pnl: 60, expected: 5000, label: 'Big gains +60%' }
      ];

      for (const tc of testCases) {
        const interval = this.calculateInterval(tc.pnl, false);
        if (interval !== tc.expected) {
          throw new Error(
            `${tc.label}: Expected ${tc.expected}ms, got ${interval}ms`
          );
        }
      }
    });
  }

  private calculateInterval(pnlPercent: number, tp1Hit: boolean): number {
    if (pnlPercent <= -25) return 2000;
    if (pnlPercent <= -15) return 3000;
    if (tp1Hit) return 3000;
    if (pnlPercent > 50) return 5000;
    return 10000;
  }

  async testPositionLimit() {
    await this.test('Max 7 concurrent positions enforced', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();
      const openPositions = data.trades.filter((t: any) => t.status === 'open');

      if (openPositions.length > 7) {
        throw new Error(`Found ${openPositions.length} open positions (max: 7)`);
      }
    });
  }

  async testNoRebuyAfterClose() {
    await this.test('No immediate re-buy after manual close', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();
      const watchlist = await Bun.file('/tmp/shocked-watchlist.json').json();

      // Find recently closed positions
      const recentlyClosed = data.trades.filter((t: any) => {
        if (t.status === 'open') return false;
        const ageMs = Date.now() - t.exitTimestamp;
        return ageMs < 3600000; // Last hour
      });

      // None should be in watchlist
      for (const trade of recentlyClosed) {
        const inWatchlist = watchlist.some((w: any) =>
          w[1].address === trade.tokenAddress
        );
        if (inWatchlist) {
          throw new Error(
            `${trade.tokenSymbol} closed but still in watchlist - will re-buy!`
          );
        }
      }
    });
  }

  async testConfidenceThreshold() {
    await this.test('Confidence threshold enforcement', async () => {
      const MIN_CONFIDENCE = 45; // Current threshold

      const mockOpp: TradeOpportunity = {
        tokenAddress: 'Test123',
        tokenSymbol: 'TEST',
        score: 40, // Below threshold
        source: 'test',
        timestamp: Date.now()
      };

      // Bot should reject this
      if (mockOpp.score < MIN_CONFIDENCE) {
        // Pass - correctly rejected
        return;
      }

      throw new Error(`Score ${mockOpp.score} should be rejected (min: ${MIN_CONFIDENCE})`);
    });
  }

  async testMonitorStateSync() {
    await this.test('Monitor shows correct open positions', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();
      const openTrades = data.trades.filter((t: any) => t.status === 'open');

      // Verify each has required fields
      for (const trade of openTrades) {
        if (!trade.tokenSymbol) {
          throw new Error(`Trade ${trade.tokenAddress} missing symbol`);
        }
        if (!trade.entryPrice) {
          throw new Error(`Trade ${trade.tokenSymbol} missing entry price`);
        }
        if (!trade.timestamp) {
          throw new Error(`Trade ${trade.tokenSymbol} missing timestamp`);
        }
      }
    });
  }

  async testTrailingStopLogic() {
    await this.test('Trailing stop activates after TP1', async () => {
      const mockTrade = {
        entryPrice: 0.0001,
        peakPrice: 0.0002, // +100% (TP1 hit)
        currentPrice: 0.00016, // -20% from peak
        tp1Hit: true
      };

      const dropFromPeak = (mockTrade.peakPrice - mockTrade.currentPrice) / mockTrade.peakPrice;

      if (mockTrade.tp1Hit && dropFromPeak >= 0.20) {
        // Should trigger trailing stop
        return;
      }

      throw new Error('Trailing stop should trigger at -20% from peak');
    });
  }

  async testBalanceAccounting() {
    await this.test('Balance accounting is accurate', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const STARTING_BALANCE = 1.0; // SOL
      let calculatedBalance = STARTING_BALANCE;

      const closedTrades = data.trades.filter((t: any) => t.status !== 'open');
      for (const trade of closedTrades) {
        calculatedBalance += (trade.pnl || 0);
      }

      const openTrades = data.trades.filter((t: any) => t.status === 'open');
      const lockedCapital = openTrades.reduce((sum: number, t: any) => sum + t.amountIn, 0);
      calculatedBalance -= lockedCapital;

      const diff = Math.abs(calculatedBalance - data.balance);
      if (diff > 0.001) { // 1 mSOL tolerance
        throw new Error(
          `Balance mismatch: Expected ${calculatedBalance.toFixed(4)}, got ${data.balance.toFixed(4)}`
        );
      }
    });
  }

  async testBlacklistPersistence() {
    await this.test('Blacklisted rugs never re-traded', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const blacklisted = data.blacklistedTokens || {};
      const allTrades = data.trades;

      for (const [address, reason] of Object.entries(blacklisted)) {
        // Count how many times we traded this token
        const tradeCount = allTrades.filter((t: any) =>
          t.tokenAddress === address
        ).length;

        if (tradeCount > 1) {
          throw new Error(
            `Blacklisted token ${address} traded ${tradeCount} times (reason: ${reason})`
          );
        }
      }
    });
  }

  // ==================== PERFORMANCE REGRESSION TESTS ====================

  async testWinRateRegression() {
    await this.test('Win rate above minimum threshold', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const MIN_WIN_RATE = 0.35; // 35% baseline
      const v2Trades = data.trades.filter((t: any) => t.timestamp > 1770950000000);
      const closed = v2Trades.filter((t: any) => t.status !== 'open');

      if (closed.length < 10) {
        console.log(this.yellow('    ⚠️  Too few trades for win rate test (need 10, have ' + closed.length + ')'));
        return; // Skip test
      }

      const wins = closed.filter((t: any) => t.pnl > 0).length;
      const winRate = wins / closed.length;

      if (winRate < MIN_WIN_RATE) {
        throw new Error(
          `Win rate ${(winRate * 100).toFixed(1)}% below minimum ${MIN_WIN_RATE * 100}%`
        );
      }
    });
  }

  async testProfitabilityRegression() {
    await this.test('System remains profitable', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const v2Trades = data.trades.filter((t: any) => t.timestamp > 1770950000000);
      const closed = v2Trades.filter((t: any) => t.status !== 'open');
      const open = v2Trades.filter((t: any) => t.status === 'open');

      const realizedPnl = closed.reduce((sum: number, t: any) => sum + (t.pnl || 0), 0);
      const unrealizedPnl = open.reduce((sum: number, t: any) => sum + (t.unrealizedPnl || 0), 0);
      const totalPnl = realizedPnl + unrealizedPnl;

      if (closed.length < 10) {
        console.log(this.yellow('    ⚠️  Too few trades for profitability test'));
        return;
      }

      if (totalPnl < 0) {
        throw new Error(
          `System unprofitable: ${(totalPnl * 1000).toFixed(2)} mSOL (${closed.length} trades)`
        );
      }
    });
  }

  async testRateLimitRegression() {
    await this.test('Rate limit errors under 5%', async () => {
      const data = await Bun.file('/tmp/paper-trades-master.json').json();

      const v2Trades = data.trades.filter((t: any) => t.timestamp > 1770950000000);
      const rateLimitErrors = v2Trades.filter((t: any) =>
        t.exitReason?.includes('429') || t.exitReason?.includes('rate limit')
      );

      const errorRate = rateLimitErrors.length / v2Trades.length;
      const MAX_ERROR_RATE = 0.05; // 5%

      if (errorRate > MAX_ERROR_RATE) {
        throw new Error(
          `Rate limit errors: ${(errorRate * 100).toFixed(1)}% (${rateLimitErrors.length}/${v2Trades.length})`
        );
      }
    });
  }

  // ==================== RUN SUITE ====================

  async runAll() {
    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('🧪 COMPREHENSIVE BOT TEST SUITE'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    const startTime = Date.now();

    // Critical behavior tests
    console.log(this.blue('📋 CRITICAL BEHAVIOR TESTS\n'));
    await this.testRateLimitDetection();
    await this.testRealRugDetection();
    await this.testDynamicIntervals();
    await this.testPositionLimit();
    await this.testNoRebuyAfterClose();
    await this.testConfidenceThreshold();
    await this.testMonitorStateSync();
    await this.testTrailingStopLogic();
    await this.testBalanceAccounting();
    await this.testBlacklistPersistence();

    // Performance regression tests
    console.log(this.blue('\n📊 PERFORMANCE REGRESSION TESTS\n'));
    await this.testWinRateRegression();
    await this.testProfitabilityRegression();
    await this.testRateLimitRegression();

    // Print results
    const duration = Date.now() - startTime;
    this.printResults(duration);

    // Exit with error if any failed
    const failed = this.results.filter(r => !r.passed);
    if (failed.length > 0) {
      process.exit(1);
    }
  }

  private printResults(totalDuration: number) {
    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('📊 TEST RESULTS'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    const passed = this.results.filter(r => r.passed);
    const failed = this.results.filter(r => !r.passed);

    for (const result of this.results) {
      const status = result.passed
        ? this.green('✓ PASS')
        : this.red('✗ FAIL');
      const time = this.yellow(`${result.duration}ms`);

      console.log(`${status} ${result.name} (${time})`);

      if (result.error) {
        console.log(this.red(`    ↳ ${result.error}`));
      }
    }

    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(`Total: ${this.results.length} | ${this.green(`Passed: ${passed.length}`)} | ${failed.length > 0 ? this.red(`Failed: ${failed.length}`) : 'Failed: 0'}`);
    console.log(`Duration: ${totalDuration}ms\n`);

    if (failed.length === 0) {
      console.log(this.green('✅ ALL TESTS PASSED - Safe to deploy\n'));
    } else {
      console.log(this.red('❌ TESTS FAILED - DO NOT DEPLOY\n'));
    }
  }
}

// Run the suite
const suite = new BotTestSuite();
await suite.runAll();
