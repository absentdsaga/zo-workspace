#!/usr/bin/env bun
/**
 * Enhanced Token Monitor
 * Shows each individual token position with live P&L
 */

import { JupiterValidator } from '../core/jupiter-validator';

interface PaperTrade {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  amountIn: number;
  entryPrice: number;
  status: 'open' | 'closed';
  exitPrice?: number;
  exitTimestamp?: number;
  pnl?: number;
  exitReason?: string;
  isRunner?: boolean;
  partialExitPrice?: number;
}

// Simple price cache to avoid redundant API calls
const priceCache = new Map<string, { price: number | null; timestamp: number }>();
const CACHE_TTL = 10000; // 10 seconds

async function getCachedPrice(validator: JupiterValidator, address: string, amount: number): Promise<number | null> {
  const cached = priceCache.get(address);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.price;
  }

  const price = await validator.getRealExecutablePrice(address, 'sell', amount);
  priceCache.set(address, { price, timestamp: Date.now() });
  return price;
}

async function loadTrades(): Promise<PaperTrade[]> {
  try {
    const tradesFile = '/tmp/paper-trades-master.json';
    const content = await Bun.file(tradesFile).text();
    return JSON.parse(content);
  } catch {
    return [];
  }
}

async function monitorTokens() {
  const validator = new JupiterValidator();
  const trades = await loadTrades();
  const openTrades = trades.filter(t => t.status === 'open');

  if (openTrades.length === 0) {
    console.log('❌ No open positions found\n');
    return;
  }

  console.clear();
  console.log('🎯 TOKEN POSITION MONITOR');
  console.log('='.repeat(80));
  console.log(`Found ${openTrades.length} open position(s)\n`);
  console.log('Fetching live prices...\n');

  // Fetch all prices in parallel with caching
  const pricePromises = openTrades.map(trade =>
    getCachedPrice(validator, trade.tokenAddress, trade.amountIn)
  );
  const prices = await Promise.all(pricePromises);

  let totalInvested = 0;
  let totalCurrentValue = 0;
  let tokenIndex = 1;

  for (let i = 0; i < openTrades.length; i++) {
    const trade = openTrades[i];
    const currentPrice = prices[i];

    const holdTime = Date.now() - trade.timestamp;
    const holdMinutes = Math.floor(holdTime / 60000);
    const holdHours = Math.floor(holdMinutes / 60);
    const holdMins = holdMinutes % 60;

    const positionType = trade.isRunner ? ' 🏃 RUNNER' : '';
    console.log(`\n📌 Token ${tokenIndex}/${openTrades.length}: ${trade.tokenSymbol}${positionType}`);
    console.log('─'.repeat(80));
    console.log(`   Address: ${trade.tokenAddress}`);
    console.log(`   Entry Time: ${new Date(trade.timestamp).toLocaleString()}`);
    console.log(`   Hold Duration: ${holdHours}h ${holdMins}m`);
    console.log(`   Position Size: ${trade.amountIn.toFixed(4)} SOL`);
    console.log(`   Entry Price: $${trade.entryPrice.toFixed(8)}`);
    if (trade.isRunner && trade.partialExitPrice) {
      console.log(`   💰 80% Sold At: $${trade.partialExitPrice.toFixed(8)} (+100%)`);
    }

    totalInvested += trade.amountIn;

    if (!currentPrice) {
      console.log('   ❌ RUGGED - No sell route available');
      console.log(`   💀 Expected Loss: -${trade.amountIn.toFixed(4)} SOL (-100%)`);
    } else {
      const pnlPercent = ((currentPrice - trade.entryPrice) / trade.entryPrice);
      const pnlSol = trade.amountIn * pnlPercent;
      const currentValue = trade.amountIn + pnlSol;

      totalCurrentValue += currentValue;

      console.log(`   ✅ Current Price: $${currentPrice.toFixed(8)}`);
      console.log(`   💰 Current Value: ${currentValue.toFixed(4)} SOL`);

      const pnlEmoji = pnlSol >= 0 ? '📈' : '📉';
      const pnlSign = pnlSol >= 0 ? '+' : '';
      console.log(`   ${pnlEmoji} P&L: ${pnlSign}${pnlSol.toFixed(4)} SOL (${pnlSign}${(pnlPercent * 100).toFixed(2)}%)`);

      // Show exit signals
      if (pnlPercent >= 1.0) {
        console.log('   🎯 SIGNAL: TAKE PROFIT TARGET HIT (+100%)');
      } else if (pnlPercent <= -0.30) {
        console.log('   🛑 SIGNAL: STOP LOSS TRIGGERED (-30%)');
      } else if (holdTime >= 60 * 60 * 1000) {
        console.log('   ⏰ SIGNAL: MAX HOLD TIME REACHED (60min)');
      }
    }

    tokenIndex++;
  }

  // Portfolio summary
  const totalPnl = totalCurrentValue - totalInvested;
  const totalPnlPercent = totalInvested > 0 ? (totalPnl / totalInvested) * 100 : 0;

  console.log('\n' + '='.repeat(80));
  console.log('📊 PORTFOLIO SUMMARY');
  console.log('='.repeat(80));
  console.log(`Total Invested: ${totalInvested.toFixed(4)} SOL`);
  console.log(`Current Value: ${totalCurrentValue.toFixed(4)} SOL`);
  console.log(`Total P&L: ${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(4)} SOL (${totalPnl >= 0 ? '+' : ''}${totalPnlPercent.toFixed(2)}%)`);
  console.log('='.repeat(80));
  console.log('\nℹ️  Use `bun sell-token.ts <address>` to manually sell a token\n');
}

// Run
monitorTokens().catch(console.error);
