#!/usr/bin/env bun

/**
 * Validates paper trading data from all sources and reports inconsistencies
 */

import { readFileSync } from 'fs';

interface Trade {
  tokenSymbol: string;
  status: string;
  entryPrice: number;
  currentPrice?: number;
  pnlSol?: number;
  tokenAddress?: string;
}

interface ValidationIssue {
  severity: 'error' | 'warning';
  source: string;
  issue: string;
  details?: any;
}

const issues: ValidationIssue[] = [];

// Load data from JSON source
function loadJSON(): Trade[] {
  try {
    const data = JSON.parse(readFileSync('/tmp/paper-trades-master.json', 'utf-8'));
    return data.trades || [];
  } catch (e) {
    issues.push({
      severity: 'error',
      source: 'JSON',
      issue: 'Failed to load /tmp/paper-trades-master.json',
      details: e
    });
    return [];
  }
}

// Validate individual trade data
function validateTrade(trade: Trade, index: number) {
  // Check for missing required fields
  if (!trade.tokenSymbol) {
    issues.push({
      severity: 'error',
      source: `Trade ${index}`,
      issue: 'Missing tokenSymbol'
    });
  }

  if (!trade.entryPrice || trade.entryPrice <= 0) {
    issues.push({
      severity: 'error',
      source: trade.tokenSymbol || `Trade ${index}`,
      issue: 'Invalid entry price',
      details: { entryPrice: trade.entryPrice }
    });
  }

  if (trade.status === 'open') {
    if (!trade.currentPrice) {
      issues.push({
        severity: 'warning',
        source: trade.tokenSymbol,
        issue: 'Open position missing current price'
      });
    }

    if (trade.currentPrice && trade.currentPrice <= 0) {
      issues.push({
        severity: 'error',
        source: trade.tokenSymbol,
        issue: 'Invalid current price',
        details: { currentPrice: trade.currentPrice }
      });
    }

    // Check for unrealistic price movements
    if (trade.currentPrice && trade.entryPrice) {
      const change = Math.abs((trade.currentPrice - trade.entryPrice) / trade.entryPrice);
      if (change > 10) { // 1000% move
        issues.push({
          severity: 'warning',
          source: trade.tokenSymbol,
          issue: 'Unrealistic price movement (>1000%)',
          details: {
            entry: trade.entryPrice,
            current: trade.currentPrice,
            changePercent: (change * 100).toFixed(2)
          }
        });
      }
    }
  }

  // Validate P&L if present
  if (trade.pnlSol !== null && trade.pnlSol !== undefined) {
    if (isNaN(trade.pnlSol)) {
      issues.push({
        severity: 'error',
        source: trade.tokenSymbol,
        issue: 'P&L is NaN',
        details: { pnlSol: trade.pnlSol }
      });
    }
  }
}

// Main validation
function main() {
  console.log('🔍 Validating paper trading data...\n');

  const trades = loadJSON();
  console.log(`📊 Found ${trades.length} total trades\n`);

  const openTrades = trades.filter(t => t.status === 'open');
  console.log(`🟢 Open positions: ${openTrades.length}`);
  console.log(`🔴 Closed positions: ${trades.length - openTrades.length}\n`);

  // Validate each trade
  trades.forEach((trade, idx) => validateTrade(trade, idx));

  // Report issues
  if (issues.length === 0) {
    console.log('✅ No issues found!\n');
  } else {
    const errors = issues.filter(i => i.severity === 'error');
    const warnings = issues.filter(i => i.severity === 'warning');

    if (errors.length > 0) {
      console.log(`❌ ERRORS: ${errors.length}\n`);
      errors.forEach(e => {
        console.log(`  [${e.source}] ${e.issue}`);
        if (e.details) console.log(`    Details: ${JSON.stringify(e.details)}`);
      });
      console.log('');
    }

    if (warnings.length > 0) {
      console.log(`⚠️  WARNINGS: ${warnings.length}\n`);
      warnings.forEach(w => {
        console.log(`  [${w.source}] ${w.issue}`);
        if (w.details) console.log(`    Details: ${JSON.stringify(w.details)}`);
      });
      console.log('');
    }
  }

  // Summary stats
  console.log('📈 SUMMARY');
  console.log('─'.repeat(60));

  const validOpen = openTrades.filter(t =>
    t.entryPrice > 0 &&
    t.currentPrice &&
    t.currentPrice > 0 &&
    t.pnlSol !== null &&
    !isNaN(t.pnlSol)
  );

  console.log(`Valid open positions: ${validOpen.length}/${openTrades.length}`);

  if (validOpen.length > 0) {
    const totalPnL = validOpen.reduce((sum, t) => sum + (t.pnlSol || 0), 0);
    console.log(`Total P&L (valid positions): ${totalPnL.toFixed(6)} SOL`);
  }

  process.exit(issues.filter(i => i.severity === 'error').length > 0 ? 1 : 0);
}

main();
