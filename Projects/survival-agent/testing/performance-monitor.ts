#!/usr/bin/env bun

/**
 * PERFORMANCE REGRESSION DETECTOR
 *
 * Purpose: Automatically detect when bot performance degrades
 * Tracks key metrics over time and alerts when things get worse
 */

import { existsSync } from 'fs';

interface PerformanceSnapshot {
  timestamp: number;
  date: string;
  metrics: {
    winRate: number;
    avgWin: number;
    avgLoss: number;
    totalPnl: number;
    tradeCount: number;
    rateLimitErrors: number;
    expectancy: number; // Expected profit per trade
  };
  version: string; // e.g., "v1", "v2-rate-limit-fix", etc.
}

class PerformanceMonitor {
  private historyFile = '/tmp/performance-history.json';
  private history: PerformanceSnapshot[] = [];

  private green(text: string) { return `\x1b[32m${text}\x1b[0m`; }
  private red(text: string) { return `\x1b[31m${text}\x1b[0m`; }
  private yellow(text: string) { return `\x1b[33m${text}\x1b[0m`; }
  private blue(text: string) { return `\x1b[36m${text}\x1b[0m`; }

  constructor() {
    this.loadHistory();
  }

  private loadHistory() {
    if (existsSync(this.historyFile)) {
      this.history = JSON.parse(Bun.file(this.historyFile).toString());
    }
  }

  private async saveHistory() {
    await Bun.write(this.historyFile, JSON.stringify(this.history, null, 2));
  }

  async captureSnapshot(version: string) {
    console.log(this.blue('\n📸 Capturing performance snapshot...\n'));

    const data = await Bun.file('/tmp/paper-trades-master.json').json();

    // Use V2 trades only (post-rate-limit-fix)
    const v2Cutoff = 1770950000000;
    const trades = data.trades.filter((t: any) => t.timestamp >= v2Cutoff);
    const closed = trades.filter((t: any) => t.status !== 'open');
    const open = trades.filter((t: any) => t.status === 'open');

    if (closed.length === 0) {
      console.log(this.yellow('⚠️  No closed trades yet - skipping snapshot\n'));
      return;
    }

    const wins = closed.filter((t: any) => t.pnl > 0);
    const losses = closed.filter((t: any) => t.pnl <= 0);

    const winRate = wins.length / closed.length;
    const avgWin = wins.reduce((sum: number, t: any) => sum + t.pnl, 0) / (wins.length || 1);
    const avgLoss = losses.reduce((sum: number, t: any) => sum + t.pnl, 0) / (losses.length || 1);
    const totalPnl = closed.reduce((sum: number, t: any) => sum + (t.pnl || 0), 0);
    const expectancy = (avgWin * winRate) + (avgLoss * (1 - winRate));

    const rateLimitErrors = closed.filter((t: any) =>
      t.exitReason?.includes('429') || t.exitReason?.includes('rate limit')
    ).length;

    const snapshot: PerformanceSnapshot = {
      timestamp: Date.now(),
      date: new Date().toISOString(),
      version,
      metrics: {
        winRate,
        avgWin,
        avgLoss,
        totalPnl,
        tradeCount: closed.length,
        rateLimitErrors,
        expectancy
      }
    };

    this.history.push(snapshot);
    await this.saveHistory();

    console.log(this.green('✅ Snapshot captured\n'));
    this.printSnapshot(snapshot);
  }

  private printSnapshot(snap: PerformanceSnapshot) {
    console.log(`Version: ${snap.version}`);
    console.log(`Date: ${snap.date}`);
    console.log(`Win Rate: ${(snap.metrics.winRate * 100).toFixed(1)}%`);
    console.log(`Avg Win: ${(snap.metrics.avgWin * 1000).toFixed(2)} mSOL`);
    console.log(`Avg Loss: ${(snap.metrics.avgLoss * 1000).toFixed(2)} mSOL`);
    console.log(`Total P&L: ${(snap.metrics.totalPnl * 1000).toFixed(2)} mSOL`);
    console.log(`Trades: ${snap.metrics.tradeCount}`);
    console.log(`Rate Limit Errors: ${snap.metrics.rateLimitErrors}`);
    console.log(`Expectancy: ${(snap.metrics.expectancy * 1000).toFixed(2)} mSOL/trade\n`);
  }

  async detectRegression() {
    if (this.history.length < 2) {
      console.log(this.yellow('\n⚠️  Need at least 2 snapshots to detect regression\n'));
      return;
    }

    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('📉 PERFORMANCE REGRESSION ANALYSIS'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    // Compare latest vs previous
    const latest = this.history[this.history.length - 1];
    const previous = this.history[this.history.length - 2];

    console.log(`Comparing: ${previous.version} → ${latest.version}\n`);

    const regressions: string[] = [];
    const improvements: string[] = [];

    // Win rate regression
    const wrDiff = latest.metrics.winRate - previous.metrics.winRate;
    if (wrDiff < -0.10) { // -10% or more
      regressions.push(`❌ Win rate degraded: ${(wrDiff * 100).toFixed(1)}%`);
    } else if (wrDiff > 0.10) {
      improvements.push(`✅ Win rate improved: +${(wrDiff * 100).toFixed(1)}%`);
    }

    // Expectancy regression (most important)
    const expDiff = latest.metrics.expectancy - previous.metrics.expectancy;
    if (expDiff < -0.001) { // -1 mSOL per trade
      regressions.push(`❌ Expectancy degraded: ${(expDiff * 1000).toFixed(2)} mSOL/trade`);
    } else if (expDiff > 0.001) {
      improvements.push(`✅ Expectancy improved: +${(expDiff * 1000).toFixed(2)} mSOL/trade`);
    }

    // Rate limit errors
    const rlDiff = latest.metrics.rateLimitErrors - previous.metrics.rateLimitErrors;
    if (rlDiff > 5) {
      regressions.push(`❌ Rate limit errors increased: +${rlDiff}`);
    } else if (rlDiff < -5) {
      improvements.push(`✅ Rate limit errors decreased: ${rlDiff}`);
    }

    // P&L regression
    const pnlDiff = latest.metrics.totalPnl - previous.metrics.totalPnl;
    if (latest.metrics.totalPnl < 0 && previous.metrics.totalPnl > 0) {
      regressions.push(`❌ Became unprofitable: ${(latest.metrics.totalPnl * 1000).toFixed(2)} mSOL`);
    } else if (latest.metrics.totalPnl > 0 && previous.metrics.totalPnl < 0) {
      improvements.push(`✅ Became profitable: ${(latest.metrics.totalPnl * 1000).toFixed(2)} mSOL`);
    }

    // Print results
    if (regressions.length > 0) {
      console.log(this.red('REGRESSIONS DETECTED:\n'));
      regressions.forEach(r => console.log(`  ${r}`));
      console.log('');
    }

    if (improvements.length > 0) {
      console.log(this.green('IMPROVEMENTS:\n'));
      improvements.forEach(i => console.log(`  ${i}`));
      console.log('');
    }

    if (regressions.length === 0 && improvements.length === 0) {
      console.log(this.yellow('➖ No significant changes\n'));
    }

    // Overall verdict
    if (regressions.length > improvements.length) {
      console.log(this.red('⚠️  OVERALL: PERFORMANCE DEGRADED'));
      console.log(this.yellow('   Consider rolling back to: ' + previous.version + '\n'));
      return false;
    } else if (improvements.length > regressions.length) {
      console.log(this.green('✅ OVERALL: PERFORMANCE IMPROVED\n'));
      return true;
    } else {
      console.log(this.yellow('➖ OVERALL: NEUTRAL\n'));
      return null;
    }
  }

  async showTrend() {
    if (this.history.length === 0) {
      console.log(this.yellow('\n⚠️  No performance history available\n'));
      return;
    }

    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('📈 PERFORMANCE TREND'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    console.log('Version                    | WR%   | Exp (mSOL) | P&L (mSOL) | Trades | RL Errors');
    console.log('─'.repeat(85));

    for (const snap of this.history) {
      const version = snap.version.padEnd(25);
      const wr = `${(snap.metrics.winRate * 100).toFixed(1)}%`.padStart(5);
      const exp = `${(snap.metrics.expectancy * 1000).toFixed(2)}`.padStart(11);
      const pnl = `${(snap.metrics.totalPnl * 1000).toFixed(2)}`.padStart(11);
      const trades = `${snap.metrics.tradeCount}`.padStart(6);
      const errors = `${snap.metrics.rateLimitErrors}`.padStart(9);

      console.log(`${version} | ${wr} | ${exp} | ${pnl} | ${trades} | ${errors}`);
    }

    console.log('');

    // Show overall trend
    if (this.history.length >= 3) {
      const first = this.history[0];
      const latest = this.history[this.history.length - 1];

      const wrChange = latest.metrics.winRate - first.metrics.winRate;
      const expChange = latest.metrics.expectancy - first.metrics.expectancy;

      console.log('OVERALL TREND (first → latest):');
      console.log(`  Win Rate: ${wrChange >= 0 ? '+' : ''}${(wrChange * 100).toFixed(1)}%`);
      console.log(`  Expectancy: ${expChange >= 0 ? '+' : ''}${(expChange * 1000).toFixed(2)} mSOL/trade\n`);
    }
  }

  async clearHistory() {
    console.log(this.yellow('\n⚠️  Clearing performance history...\n'));
    this.history = [];
    await this.saveHistory();
    console.log(this.green('✅ History cleared\n'));
  }
}

// CLI
const command = process.argv[2];
const version = process.argv[3] || 'v2';

const monitor = new PerformanceMonitor();

switch (command) {
  case 'capture':
    await monitor.captureSnapshot(version);
    break;

  case 'check':
    await monitor.detectRegression();
    break;

  case 'trend':
    await monitor.showTrend();
    break;

  case 'clear':
    await monitor.clearHistory();
    break;

  default:
    console.log('\n📊 PERFORMANCE REGRESSION DETECTOR\n');
    console.log('Usage:');
    console.log('  bun performance-monitor.ts capture <version>  - Capture current performance');
    console.log('  bun performance-monitor.ts check              - Check for regression');
    console.log('  bun performance-monitor.ts trend              - Show performance trend');
    console.log('  bun performance-monitor.ts clear              - Clear history\n');
    console.log('Example:');
    console.log('  bun performance-monitor.ts capture "v2-confidence-70"\n');
    process.exit(1);
}
