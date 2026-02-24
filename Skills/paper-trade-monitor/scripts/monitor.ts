#!/usr/bin/env bun

/**
 * Clean monitor display - single source of truth
 */

import { readFileSync } from 'fs';

interface Trade {
  tokenSymbol: string;
  tokenAddress: string;
  status: 'open' | 'closed';
  entryPrice: number;
  currentPrice?: number;
  exitPrice?: number;
  pnlSol?: number;
  pnlPercent?: number;
  confidence?: number;
  source?: string;
  entryTime?: number;
  exitTime?: number;
  signature?: string;
  peakPrice?: number;
  peakPercent?: number;
}

interface TradesData {
  trades: Trade[];
  balance?: number;
  startingBalance?: number;
  totalFees?: number;
}

// Load canonical data
function loadData(): TradesData {
  const raw = readFileSync('/tmp/paper-trades-master.json', 'utf-8');
  return JSON.parse(raw);
}

// Calculate P&L from price data
function calculatePnL(trade: Trade, positionSize: number = 0.036): {
  pnlSol: number;
  pnlPercent: number;
} {
  const price = trade.status === 'open' ? trade.currentPrice : trade.exitPrice;
  if (!price || !trade.entryPrice) {
    return { pnlSol: 0, pnlPercent: 0 };
  }

  const priceChange = price - trade.entryPrice;
  const pnlPercent = (priceChange / trade.entryPrice) * 100;
  const pnlSol = (priceChange / trade.entryPrice) * positionSize;

  return { pnlSol, pnlPercent };
}

// Format price for display
function formatPrice(price: number): string {
  if (price < 0.0001) {
    return `$${price.toExponential(4)}`;
  }
  return `$${price.toFixed(10)}`.replace(/\.?0+$/, '');
}

// Display single position
function displayPosition(trade: Trade, index: number) {
  const { pnlSol, pnlPercent } = calculatePnL(trade);
  const emoji = pnlPercent >= 0 ? '💎' : '📉';
  const sign = pnlPercent >= 0 ? '+' : '';

  console.log(`\n${emoji} ${trade.tokenSymbol} (${trade.source || 'unknown'})`);
  console.log(`   Entry: ${formatPrice(trade.entryPrice)}`);

  if (trade.status === 'open' && trade.currentPrice) {
    console.log(`   Current: ${formatPrice(trade.currentPrice)}`);
  } else if (trade.status === 'closed' && trade.exitPrice) {
    console.log(`   Exit: ${formatPrice(trade.exitPrice)}`);
  }

  if (trade.peakPrice && trade.peakPercent) {
    console.log(`   Peak: ${formatPrice(trade.peakPrice)} (${sign}${trade.peakPercent.toFixed(2)}%)`);
  }

  console.log(`   P&L: ${sign}${pnlSol.toFixed(6)} SOL (${sign}${pnlPercent.toFixed(2)}%)`);

  if (trade.confidence) {
    console.log(`   Confidence: ${trade.confidence}/100`);
  }

  if (trade.signature) {
    console.log(`   Signature: ${trade.signature}`);
  }
}

// Main display
function main() {
  const data = loadData();
  const trades = data.trades || [];
  const openTrades = trades.filter(t => t.status === 'open');
  const closedTrades = trades.filter(t => t.status === 'closed');

  console.clear();
  console.log('═'.repeat(64));
  console.log('📊 PAPER TRADING BOT - CLEAN MONITOR (Single Source of Truth)');
  console.log('═'.repeat(64));
  console.log('');

  // Balance info
  if (data.balance !== undefined) {
    console.log(`💰 Balance: ${data.balance.toFixed(6)} SOL`);
  }
  if (data.startingBalance !== undefined) {
    const totalPnL = (data.balance || 0) - data.startingBalance;
    console.log(`📈 Total P&L: ${totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(6)} SOL`);
  }
  if (data.totalFees !== undefined) {
    console.log(`💸 Total Fees: ${data.totalFees.toFixed(6)} SOL`);
  }

  // Open positions
  console.log(`\n🎯 OPEN POSITIONS: ${openTrades.length}`);
  console.log('─'.repeat(64));

  if (openTrades.length === 0) {
    console.log('No open positions');
  } else {
    openTrades.forEach((trade, idx) => displayPosition(trade, idx));
  }

  // Recently closed (last 3)
  if (closedTrades.length > 0) {
    console.log(`\n\n📜 RECENTLY CLOSED: ${Math.min(3, closedTrades.length)} of ${closedTrades.length}`);
    console.log('─'.repeat(64));

    closedTrades
      .slice(-3)
      .reverse()
      .forEach((trade, idx) => displayPosition(trade, idx));
  }

  // Summary stats
  const validOpen = openTrades.filter(t => t.currentPrice && t.entryPrice);
  if (validOpen.length > 0) {
    const totalOpenPnL = validOpen.reduce((sum, t) => {
      const { pnlSol } = calculatePnL(t);
      return sum + pnlSol;
    }, 0);

    console.log(`\n\n📊 SUMMARY`);
    console.log('─'.repeat(64));
    console.log(`Open positions P&L: ${totalOpenPnL >= 0 ? '+' : ''}${totalOpenPnL.toFixed(6)} SOL`);
  }

  console.log(`\n⏰ Updated: ${new Date().toLocaleString()}`);
  console.log('═'.repeat(64));
  console.log('');
}

main();
