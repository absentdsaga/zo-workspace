#!/usr/bin/env bun

/**
 * STATE SNAPSHOT & ROLLBACK SYSTEM
 *
 * Purpose: Prevent degradation by allowing instant rollback to known-good states
 * Usage:
 *   - bun state-snapshot.ts save "Before rate limit fix"
 *   - bun state-snapshot.ts list
 *   - bun state-snapshot.ts rollback <id>
 *   - bun state-snapshot.ts compare <id1> <id2>
 */

import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';

interface Snapshot {
  id: string;
  timestamp: number;
  label: string;
  files: {
    paperTrades: any;
    watchlist: any;
    botCode: string;
    validatorCode: string;
  };
  metrics: {
    balance: number;
    openPositions: number;
    totalTrades: number;
    winRate: number;
    totalPnl: number;
  };
}

class StateManager {
  private snapshotDir = '/tmp/bot-snapshots';
  private snapshotsFile = join(this.snapshotDir, 'snapshots.json');

  constructor() {
    if (!existsSync(this.snapshotDir)) {
      mkdirSync(this.snapshotDir, { recursive: true });
    }
  }

  async save(label: string): Promise<string> {
    const id = Date.now().toString();
    console.log(`\n📸 Creating snapshot: ${label}\n`);

    // Load current state
    const paperTrades = await Bun.file('/tmp/paper-trades-master.json').json();
    const watchlist = await Bun.file('/tmp/shocked-watchlist.json').json();
    const botCode = await Bun.file('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts').text();
    const validatorCode = await Bun.file('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts').text();

    // Calculate metrics
    const openPositions = paperTrades.trades.filter((t: any) => t.status === 'open');
    const closedTrades = paperTrades.trades.filter((t: any) => t.status !== 'open');
    const wins = closedTrades.filter((t: any) => t.pnl > 0);
    const totalPnl = closedTrades.reduce((sum: number, t: any) => sum + (t.pnl || 0), 0);

    const snapshot: Snapshot = {
      id,
      timestamp: Date.now(),
      label,
      files: {
        paperTrades,
        watchlist,
        botCode,
        validatorCode
      },
      metrics: {
        balance: paperTrades.balance,
        openPositions: openPositions.length,
        totalTrades: paperTrades.trades.length,
        winRate: closedTrades.length > 0 ? wins.length / closedTrades.length : 0,
        totalPnl
      }
    };

    // Save snapshot
    const snapshots = await this.loadSnapshots();
    snapshots.push(snapshot);
    await Bun.write(this.snapshotsFile, JSON.stringify(snapshots, null, 2));

    console.log(`✅ Snapshot saved: ${id}`);
    console.log(`   Balance: ${snapshot.metrics.balance.toFixed(4)} SOL`);
    console.log(`   Open positions: ${snapshot.metrics.openPositions}`);
    console.log(`   Total trades: ${snapshot.metrics.totalTrades}`);
    console.log(`   Win rate: ${(snapshot.metrics.winRate * 100).toFixed(1)}%`);
    console.log(`   Total P&L: ${(snapshot.metrics.totalPnl * 1000).toFixed(2)} mSOL\n`);

    return id;
  }

  async list() {
    const snapshots = await this.loadSnapshots();

    if (snapshots.length === 0) {
      console.log('\n📭 No snapshots found\n');
      return;
    }

    console.log('\n📸 SAVED SNAPSHOTS\n');
    console.log('═══════════════════════════════════════════════════════\n');

    for (const snap of snapshots.reverse()) {
      const date = new Date(snap.timestamp).toLocaleString();
      console.log(`ID: ${snap.id}`);
      console.log(`Label: ${snap.label}`);
      console.log(`Date: ${date}`);
      console.log(`Balance: ${snap.metrics.balance.toFixed(4)} SOL | Open: ${snap.metrics.openPositions} | Trades: ${snap.metrics.totalTrades}`);
      console.log(`Win Rate: ${(snap.metrics.winRate * 100).toFixed(1)}% | P&L: ${(snap.metrics.totalPnl * 1000).toFixed(2)} mSOL`);
      console.log('');
    }
  }

  async rollback(id: string) {
    const snapshots = await this.loadSnapshots();
    const snapshot = snapshots.find(s => s.id === id);

    if (!snapshot) {
      console.error(`\n❌ Snapshot ${id} not found\n`);
      process.exit(1);
    }

    console.log(`\n⏮️  Rolling back to: ${snapshot.label}\n`);

    // Create backup of current state
    await this.save(`Auto-backup before rollback to ${id}`);

    // Restore files
    await Bun.write('/tmp/paper-trades-master.json', JSON.stringify(snapshot.files.paperTrades, null, 2));
    await Bun.write('/tmp/shocked-watchlist.json', JSON.stringify(snapshot.files.watchlist, null, 2));
    await Bun.write('/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts', snapshot.files.botCode);
    await Bun.write('/home/workspace/Projects/survival-agent/core/jupiter-validator.ts', snapshot.files.validatorCode);

    console.log('✅ Rollback complete!\n');
    console.log('Restored state:');
    console.log(`   Balance: ${snapshot.metrics.balance.toFixed(4)} SOL`);
    console.log(`   Open positions: ${snapshot.metrics.openPositions}`);
    console.log(`   Total trades: ${snapshot.metrics.totalTrades}`);
    console.log(`   Win rate: ${(snapshot.metrics.winRate * 100).toFixed(1)}%\n`);
  }

  async compare(id1: string, id2: string) {
    const snapshots = await this.loadSnapshots();
    const snap1 = snapshots.find(s => s.id === id1);
    const snap2 = snapshots.find(s => s.id === id2);

    if (!snap1 || !snap2) {
      console.error('\n❌ One or both snapshots not found\n');
      process.exit(1);
    }

    console.log('\n📊 SNAPSHOT COMPARISON\n');
    console.log('═══════════════════════════════════════════════════════\n');

    console.log(`BEFORE: ${snap1.label} (${id1})`);
    console.log(`AFTER:  ${snap2.label} (${id2})\n`);

    const balanceDiff = snap2.metrics.balance - snap1.metrics.balance;
    const tradesDiff = snap2.metrics.totalTrades - snap1.metrics.totalTrades;
    const pnlDiff = snap2.metrics.totalPnl - snap1.metrics.totalPnl;
    const wrDiff = snap2.metrics.winRate - snap1.metrics.winRate;

    console.log('METRICS DELTA:\n');
    console.log(`Balance:     ${balanceDiff >= 0 ? '+' : ''}${(balanceDiff * 1000).toFixed(2)} mSOL`);
    console.log(`Trades:      ${tradesDiff >= 0 ? '+' : ''}${tradesDiff}`);
    console.log(`Total P&L:   ${pnlDiff >= 0 ? '+' : ''}${(pnlDiff * 1000).toFixed(2)} mSOL`);
    console.log(`Win Rate:    ${wrDiff >= 0 ? '+' : ''}${(wrDiff * 100).toFixed(1)}%\n`);

    // Determine if this was an improvement
    const improved = balanceDiff > 0 && wrDiff >= 0;
    const degraded = balanceDiff < 0 || wrDiff < -0.05;

    if (improved) {
      console.log('✅ IMPROVEMENT - Metrics got better');
    } else if (degraded) {
      console.log('❌ DEGRADATION - Metrics got worse');
      console.log('   Consider rolling back to ' + id1);
    } else {
      console.log('➖ NEUTRAL - Mixed results');
    }
    console.log('');
  }

  private async loadSnapshots(): Promise<Snapshot[]> {
    if (!existsSync(this.snapshotsFile)) {
      return [];
    }
    return await Bun.file(this.snapshotsFile).json();
  }
}

// CLI
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

const manager = new StateManager();

switch (command) {
  case 'save':
    if (!arg1) {
      console.error('\n❌ Usage: bun state-snapshot.ts save "Description"\n');
      process.exit(1);
    }
    await manager.save(arg1);
    break;

  case 'list':
    await manager.list();
    break;

  case 'rollback':
    if (!arg1) {
      console.error('\n❌ Usage: bun state-snapshot.ts rollback <id>\n');
      process.exit(1);
    }
    await manager.rollback(arg1);
    break;

  case 'compare':
    if (!arg1 || !arg2) {
      console.error('\n❌ Usage: bun state-snapshot.ts compare <id1> <id2>\n');
      process.exit(1);
    }
    await manager.compare(arg1, arg2);
    break;

  default:
    console.log('\n📸 STATE SNAPSHOT & ROLLBACK SYSTEM\n');
    console.log('Usage:');
    console.log('  bun state-snapshot.ts save "Description"');
    console.log('  bun state-snapshot.ts list');
    console.log('  bun state-snapshot.ts rollback <id>');
    console.log('  bun state-snapshot.ts compare <id1> <id2>\n');
    process.exit(1);
}
