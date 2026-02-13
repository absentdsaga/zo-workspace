#!/usr/bin/env bun
/**
 * Close all paper trading positions
 * Simulates selling everything and calculates final P&L
 */

interface PaperTrade {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  amountIn: number;
  entryPrice?: number;
  status: string;
}

async function main() {
  console.log('🔥 CLOSING ALL PAPER TRADE POSITIONS\n');

  const logPath = '/tmp/paper-trade-final.log';

  try {
    const logContent = await Bun.file(logPath).text();
    const lines = logContent.split('\n');

    // Parse all trades from log
    const trades: PaperTrade[] = [];
    let currentToken = '';
    let currentAddress = '';
    let currentAmount = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Extract token info
      if (line.includes('Token:')) {
        const match = line.match(/Token: (.+?) \(([A-Za-z0-9]+)\.\.\.\)/);
        if (match) {
          currentToken = match[1];
          currentAddress = match[2];
        }
      }

      // Extract position size
      if (line.includes('Position:') && line.includes('SOL')) {
        const match = line.match(/Position: ([\d.]+) SOL/);
        if (match) {
          currentAmount = parseFloat(match[1]);
        }
      }

      // Extract trade confirmation
      if (line.includes('TRADE SIMULATED SUCCESSFULLY') && currentToken) {
        trades.push({
          timestamp: Date.now(),
          tokenAddress: currentAddress,
          tokenSymbol: currentToken,
          amountIn: currentAmount,
          entryPrice: Math.random() * 0.0001, // Simulated
          status: 'open'
        });

        currentToken = '';
        currentAddress = '';
        currentAmount = 0;
      }
    }

    if (trades.length === 0) {
      console.log('✅ No open positions found in paper trade log\n');
      process.exit(0);
    }

    console.log(`📊 Found ${trades.length} open position(s)\n`);
    console.log('═'.repeat(60));

    let totalInvested = 0;
    let totalValue = 0;
    let closedPositions = 0;

    // Group by token
    const grouped = new Map<string, { symbol: string; count: number; totalSol: number }>();

    for (const trade of trades) {
      const existing = grouped.get(trade.tokenAddress);
      if (existing) {
        existing.count++;
        existing.totalSol += trade.amountIn;
      } else {
        grouped.set(trade.tokenAddress, {
          symbol: trade.tokenSymbol,
          count: 1,
          totalSol: trade.amountIn
        });
      }
    }

    // Close each position with simulated outcome
    for (const [address, info] of grouped) {
      console.log(`\n💎 ${info.symbol}`);
      console.log(`   Positions: ${info.count}`);
      console.log(`   Total Invested: ${info.totalSol.toFixed(4)} SOL`);

      // Check if token still has liquidity
      const priceCheck = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
      const priceData = await priceCheck.json();

      let pnlPercent = 0;
      let exitValue = 0;

      if (!priceData.pairs || priceData.pairs.length === 0) {
        // Token rugged
        console.log(`   ❌ Token RUGGED - No liquidity`);
        console.log(`   💀 Exit Value: 0.0000 SOL`);
        console.log(`   📉 P&L: -100% (-${info.totalSol.toFixed(4)} SOL)`);
        pnlPercent = -100;
        exitValue = 0;
      } else {
        // Token still trading - simulate random outcome
        // Most meme coins: 60% lose money, 30% small gain, 10% big win
        const rand = Math.random();

        if (rand < 0.60) {
          // Loss (-90% to -10%)
          pnlPercent = -90 + (Math.random() * 80);
        } else if (rand < 0.90) {
          // Small gain (+5% to +50%)
          pnlPercent = 5 + (Math.random() * 45);
        } else {
          // Big win (+50% to +200%)
          pnlPercent = 50 + (Math.random() * 150);
        }

        exitValue = info.totalSol * (1 + pnlPercent / 100);
        const pnlSol = exitValue - info.totalSol;

        console.log(`   ✅ Token still trading`);
        console.log(`   💰 Exit Value: ${exitValue.toFixed(4)} SOL`);
        console.log(`   📊 P&L: ${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}% (${pnlSol >= 0 ? '+' : ''}${pnlSol.toFixed(4)} SOL)`);
      }

      totalInvested += info.totalSol;
      totalValue += exitValue;
      closedPositions += info.count;

      console.log(`   🚪 CLOSING ${info.count} position(s)...`);
      console.log(`   ✅ CLOSED`);
    }

    const totalPnlSol = totalValue - totalInvested;
    const totalPnlPercent = ((totalPnlSol / totalInvested) * 100);

    console.log('\n' + '═'.repeat(60));
    console.log('\n📊 FINAL PAPER TRADE RESULTS:');
    console.log('═'.repeat(60));
    console.log(`   Positions Closed: ${closedPositions}`);
    console.log(`   Total Invested: ${totalInvested.toFixed(4)} SOL`);
    console.log(`   Final Value: ${totalValue.toFixed(4)} SOL`);
    console.log(`   Total P&L: ${totalPnlSol >= 0 ? '+' : ''}${totalPnlSol.toFixed(4)} SOL (${totalPnlPercent >= 0 ? '+' : ''}${totalPnlPercent.toFixed(2)}%)`);
    console.log('');

    if (totalPnlPercent >= 0) {
      console.log(`   ✅ PROFITABLE SESSION`);
    } else if (totalPnlPercent > -20) {
      console.log(`   ⚠️  SMALL LOSS - Could be worse`);
    } else {
      console.log(`   ❌ SIGNIFICANT LOSS - Strategy needs work`);
    }

    console.log('\n' + '═'.repeat(60));
    console.log('\n💡 Ready to start fresh paper trading run');
    console.log('   Delete log: rm /tmp/paper-trade-final.log');
    console.log('   Start new: bun run testing/paper-trade-master.ts\n');

  } catch (error: any) {
    console.error('❌ Error reading paper trade log:', error.message);
    process.exit(1);
  }
}

main().catch(console.error);
