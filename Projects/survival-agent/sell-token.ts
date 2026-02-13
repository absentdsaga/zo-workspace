#!/usr/bin/env bun
/**
 * Manual Token Sell Function
 * Sells all of a specific token from paper trading positions
 */

import { JupiterValidator } from './core/jupiter-validator';

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
}

async function loadTrades(): Promise<PaperTrade[]> {
  try {
    const tradesFile = '/tmp/paper-trades.json';
    const content = await Bun.file(tradesFile).text();
    return JSON.parse(content);
  } catch {
    return [];
  }
}

async function saveTrades(trades: PaperTrade[]) {
  const tradesFile = '/tmp/paper-trades.json';
  await Bun.write(tradesFile, JSON.stringify(trades, null, 2));
}

async function sellToken(tokenAddress: string) {
  console.log('💼 Manual Token Sell\n');

  const validator = new JupiterValidator();
  const trades = await loadTrades();

  // Find all open positions for this token
  const openPositions = trades.filter(
    t => t.status === 'open' &&
    (t.tokenAddress === tokenAddress || t.tokenAddress.startsWith(tokenAddress))
  );

  if (openPositions.length === 0) {
    console.log(`❌ No open positions found for: ${tokenAddress}\n`);
    console.log('Open positions:');
    const allOpen = trades.filter(t => t.status === 'open');
    if (allOpen.length === 0) {
      console.log('   None\n');
    } else {
      allOpen.forEach(t => {
        console.log(`   - ${t.tokenSymbol} (${t.tokenAddress.slice(0, 8)}...)`);
      });
    }
    return;
  }

  const token = openPositions[0];
  console.log(`🎯 Selling: ${token.tokenSymbol}`);
  console.log(`   Address: ${token.tokenAddress}`);
  console.log(`   Positions to close: ${openPositions.length}`);
  console.log('');

  // Get current price
  console.log('Fetching current price from Jupiter...');
  const currentPrice = await validator.getRealExecutablePrice(
    token.tokenAddress,
    'sell',
    token.amountSol
  );

  if (!currentPrice) {
    console.log('❌ Cannot sell - No sell route available (token may be rugged)\n');
    console.log('Force close anyway? (y/n)');

    // Simple prompt simulation
    const forceClose = process.argv.includes('--force');

    if (forceClose) {
      console.log('💀 Force closing all positions as rugged...\n');

      for (const position of openPositions) {
        position.status = 'closed';
        position.exitTimestamp = Date.now();
        position.exitReason = 'MANUAL SELL (RUGGED)';
        position.pnl = -position.amountSol;

        console.log(`   ❌ ${position.tokenSymbol} - Loss: -${position.amountSol.toFixed(4)} SOL`);
      }

      await saveTrades(trades);
      console.log('\n✅ Positions closed\n');
    } else {
      console.log('ℹ️  Add --force flag to force close rugged positions\n');
    }
    return;
  }

  // Calculate totals
  let totalInvested = 0;
  let totalPnl = 0;

  console.log('✅ Current Price: $' + currentPrice.toFixed(8));
  console.log('\nClosing positions:\n');

  for (const position of openPositions) {
    const pnlPercent = ((currentPrice - position.entryPrice) / position.entryPrice);
    const pnlSol = position.amountSol * pnlPercent;

    position.status = 'closed';
    position.exitPrice = currentPrice;
    position.exitTimestamp = Date.now();
    position.exitReason = 'MANUAL SELL';
    position.pnl = pnlSol;

    totalInvested += position.amountSol;
    totalPnl += pnlSol;

    const emoji = pnlSol >= 0 ? '✅' : '❌';
    const sign = pnlSol >= 0 ? '+' : '';

    console.log(`   ${emoji} Position ${position.amountSol.toFixed(4)} SOL`);
    console.log(`      Entry: $${position.entryPrice.toFixed(8)}`);
    console.log(`      Exit:  $${currentPrice.toFixed(8)}`);
    console.log(`      P&L:   ${sign}${pnlSol.toFixed(4)} SOL (${sign}${(pnlPercent * 100).toFixed(2)}%)`);
    console.log('');
  }

  await saveTrades(trades);

  console.log('━'.repeat(60));
  console.log('📊 SELL SUMMARY');
  console.log(`Total Positions Closed: ${openPositions.length}`);
  console.log(`Total Invested: ${totalInvested.toFixed(4)} SOL`);
  console.log(`Total Returned: ${(totalInvested + totalPnl).toFixed(4)} SOL`);
  console.log(`Net P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL (${totalPnl >= 0 ? '+' : ''}${((totalPnl / totalInvested) * 100).toFixed(2)}%)`);
  console.log('━'.repeat(60));
  console.log('\n✅ Sell complete!\n');
}

// Main
const tokenAddress = process.argv[2];

if (!tokenAddress) {
  console.log('Usage: bun sell-token.ts <token-address> [--force]\n');
  console.log('Examples:');
  console.log('  bun sell-token.ts DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263');
  console.log('  bun sell-token.ts DezXAZ8 (partial address works)');
  console.log('  bun sell-token.ts DezXAZ8 --force (force close rugged token)\n');
  process.exit(1);
}

sellToken(tokenAddress).catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
