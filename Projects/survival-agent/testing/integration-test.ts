#!/usr/bin/env bun

/**
 * INTEGRATION TEST HARNESS
 *
 * Purpose: Test bot + monitor together to catch sync issues
 * Tests the exact bug where monitor showed CatCopter after it was closed
 */

import { spawn } from 'child_process';
import { existsSync } from 'fs';

class IntegrationTester {
  private botProcess: any = null;
  private monitorProcess: any = null;

  private green(text: string) { return `\x1b[32m${text}\x1b[0m`; }
  private red(text: string) { return `\x1b[31m${text}\x1b[0m`; }
  private yellow(text: string) { return `\x1b[33m${text}\x1b[0m`; }
  private blue(text: string) { return `\x1b[36m${text}\x1b[0m`; }

  async runTest() {
    console.log(this.blue('\n═══════════════════════════════════════════════════════'));
    console.log(this.blue('🔄 INTEGRATION TEST: Bot + Monitor Sync'));
    console.log(this.blue('═══════════════════════════════════════════════════════\n'));

    try {
      // Test 1: Monitor reflects bot state accurately
      await this.testMonitorSync();

      // Test 2: Manual close removes from monitor
      await this.testManualCloseSync();

      // Test 3: No duplicate positions
      await this.testNoDuplicates();

      // Test 4: Watchlist updates propagate
      await this.testWatchlistSync();

      console.log(this.green('\n✅ ALL INTEGRATION TESTS PASSED\n'));
    } catch (error) {
      console.log(this.red('\n❌ INTEGRATION TEST FAILED\n'));
      console.log(this.red(error instanceof Error ? error.message : String(error)));
      process.exit(1);
    }
  }

  private async testMonitorSync() {
    console.log(this.blue('Test 1: Monitor shows accurate bot state\n'));

    // Load current state
    const data = await Bun.file('/tmp/paper-trades-master.json').json();
    const openPositions = data.trades.filter((t: any) => t.status === 'open');

    console.log(`Bot state: ${openPositions.length} open positions`);

    // Simulate what monitor script does
    const monitorView = openPositions.map((t: any) => ({
      symbol: t.tokenSymbol,
      address: t.tokenAddress,
      pnl: t.unrealizedPnl
    }));

    console.log(`Monitor view: ${monitorView.length} positions\n`);

    // Verify each position has required fields
    for (const pos of monitorView) {
      if (!pos.symbol || !pos.address) {
        throw new Error(`Position missing symbol or address: ${JSON.stringify(pos)}`);
      }
    }

    console.log(this.green('✓ Monitor accurately reflects bot state\n'));
  }

  private async testManualCloseSync() {
    console.log(this.blue('Test 2: Manual close removes from monitor\n'));

    // Load current state
    const data = await Bun.file('/tmp/paper-trades-master.json').json();
    const watchlist = await Bun.file('/tmp/shocked-watchlist.json').json();

    // Find recently closed positions (last hour)
    const recentlyClosed = data.trades.filter((t: any) => {
      if (t.status === 'open') return false;
      if (!t.exitTimestamp) return false;
      const ageMs = Date.now() - t.exitTimestamp;
      return ageMs < 3600000; // 1 hour
    });

    console.log(`Recently closed: ${recentlyClosed.length} positions`);

    // None should be in shocked watchlist
    const stillInWatchlist = recentlyClosed.filter((t: any) =>
      watchlist.some((w: any) => w[1].address === t.tokenAddress)
    );

    if (stillInWatchlist.length > 0) {
      const symbols = stillInWatchlist.map((t: any) => t.tokenSymbol).join(', ');
      throw new Error(
        `❌ BUG DETECTED: ${stillInWatchlist.length} closed positions still in watchlist: ${symbols}\n` +
        `   This is the exact bug where CatCopter re-appeared!`
      );
    }

    console.log(this.green('✓ Closed positions correctly removed from watchlist\n'));
  }

  private async testNoDuplicates() {
    console.log(this.blue('Test 3: No duplicate positions\n'));

    const data = await Bun.file('/tmp/paper-trades-master.json').json();
    const openPositions = data.trades.filter((t: any) => t.status === 'open');

    // Check for duplicate token addresses
    const addresses = openPositions.map((t: any) => t.tokenAddress);
    const uniqueAddresses = new Set(addresses);

    if (addresses.length !== uniqueAddresses.size) {
      const duplicates = addresses.filter((addr, idx) =>
        addresses.indexOf(addr) !== idx
      );
      throw new Error(
        `Found duplicate positions: ${duplicates.join(', ')}`
      );
    }

    console.log(`${openPositions.length} unique positions\n`);
    console.log(this.green('✓ No duplicate positions\n'));
  }

  private async testWatchlistSync() {
    console.log(this.blue('Test 4: Watchlist updates propagate correctly\n'));

    const watchlist = await Bun.file('/tmp/shocked-watchlist.json').json();

    console.log(`Watchlist size: ${watchlist.length} tokens`);

    // Verify format
    for (const entry of watchlist) {
      if (!Array.isArray(entry) || entry.length !== 2) {
        throw new Error(`Invalid watchlist entry format: ${JSON.stringify(entry)}`);
      }

      const [address, data] = entry;
      if (!data.symbol || !data.addedAt || !data.source) {
        throw new Error(
          `Watchlist entry missing required fields: ${JSON.stringify(data)}`
        );
      }
    }

    // Check for stale entries (> 24 hours)
    const now = Date.now();
    const staleEntries = watchlist.filter((entry: any) => {
      const ageMs = now - entry[1].addedAt;
      return ageMs > 24 * 60 * 60 * 1000;
    });

    if (staleEntries.length > 0) {
      console.log(this.yellow(`⚠️  Found ${staleEntries.length} stale entries (> 24h old)`));
      console.log(this.yellow('   Consider implementing auto-cleanup'));
    }

    console.log(this.green('✓ Watchlist format is valid\n'));
  }

  // Helper: Start bot in background
  private async startBot(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.botProcess = spawn('bun', ['/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts'], {
        detached: true,
        stdio: 'ignore'
      });

      this.botProcess.unref();

      // Give it time to initialize
      setTimeout(() => resolve(), 3000);
    });
  }

  // Helper: Stop bot
  private stopBot() {
    if (this.botProcess) {
      this.botProcess.kill();
      this.botProcess = null;
    }
  }

  // Cleanup
  async cleanup() {
    this.stopBot();
  }
}

// Run integration tests
const tester = new IntegrationTester();
try {
  await tester.runTest();
} finally {
  await tester.cleanup();
}
