/**
 * ANALYZE UPGRADE IMPACT
 * 
 * Compare current settings vs proposed upgrade
 * Show expected mainnet performance improvement
 */

import { readFileSync } from 'fs';

interface Trade {
  timestamp: number;
  tokenAddress: string;
  tokenSymbol: string;
  strategy: string;
  amountIn: number;
  entryPrice: number;
  currentPrice: number;
  status: string;
  pnl?: number;
  exitTimestamp?: number;
  exitReason?: string;
  source?: string;
  shocked_confidence?: number;
  smart_money_confidence?: number;
}

// Load trade history
const tradesFile = '/home/workspace/Projects/survival-agent/testing/paper-trades-history.json';
let trades: Trade[] = [];

try {
  const data = readFileSync(tradesFile, 'utf-8');
  trades = JSON.parse(data);
  console.log(`✅ Loaded ${trades.length} historical trades\n`);
} catch (error) {
  console.error('❌ Failed to load trade history:', error);
  process.exit(1);
}

// CURRENT SETTINGS
const CURRENT = {
  name: 'Current Production Settings',
  minScore: 60,
  minSmartMoney: 35,
  positionSize: 0.10, // 10%
  filters: {
    excludeSources: [] as string[],
  }
};

// PROPOSED UPGRADE
const PROPOSED = {
  name: 'Proposed Upgrade v2',
  minScore: 60, // Keep same
  minSmartMoney: 35, // Keep same
  positionSize: 0.12, // Increase to 12%
  filters: {
    excludeSources: ['dexscreener'], // Exclude smart-money-only
  }
};

function analyzeStrategy(config: typeof CURRENT, trades: Trade[]) {
  // Filter trades that would qualify under this config
  const qualifyingTrades = trades.filter(trade => {
    // Check source exclusions
    if (config.filters.excludeSources.includes(trade.source || '')) {
      return false;
    }
    
    // All other filters are already applied in the historical data
    return true;
  });

  // Calculate metrics
  const totalTrades = qualifyingTrades.length;
  const wins = qualifyingTrades.filter(t => (t.pnl || 0) > 0).length;
  const losses = qualifyingTrades.filter(t => (t.pnl || 0) < 0).length;
  const winRate = totalTrades > 0 ? (wins / totalTrades) * 100 : 0;

  // P&L calculation
  const paperPnl = qualifyingTrades.reduce((sum, t) => sum + (t.pnl || 0), 0);
  
  // Mainnet costs (more accurate)
  const jupiterFeePerTrade = 0.0005; // 0.05% platform fee
  const slippagePerTrade = 0.003; // 0.3% average slippage
  const solanaFeePerTrade = 0.00001; // ~$0.001 network fee
  
  const totalFees = totalTrades * (jupiterFeePerTrade + slippagePerTrade + solanaFeePerTrade);
  const mainnetPnl = paperPnl - totalFees;

  // With adjusted position size
  const sizeMultiplier = config.positionSize / 0.10; // Relative to base 10%
  const adjustedMainnetPnl = mainnetPnl * sizeMultiplier;

  return {
    config,
    totalTrades,
    wins,
    losses,
    winRate,
    paperPnl,
    totalFees,
    mainnetPnl,
    adjustedMainnetPnl,
    sizeMultiplier,
    qualifyingTrades,
  };
}

// Analyze both strategies
console.log('📊 STRATEGY COMPARISON\n');
console.log('='.repeat(80));

const currentResults = analyzeStrategy(CURRENT, trades);
const proposedResults = analyzeStrategy(PROPOSED, trades);

function printResults(results: ReturnType<typeof analyzeStrategy>) {
  console.log(`\n🎯 ${results.config.name}`);
  console.log('-'.repeat(80));
  console.log(`Min Score: ${results.config.minScore} | Min Smart Money: ${results.config.minSmartMoney}`);
  console.log(`Position Size: ${(results.config.positionSize * 100).toFixed(0)}%`);
  console.log(`Exclude Sources: ${results.config.filters.excludeSources.join(', ') || 'None'}\n`);
  
  console.log(`📈 Performance:`);
  console.log(`   Total Trades: ${results.totalTrades}`);
  console.log(`   Wins: ${results.wins} | Losses: ${results.losses}`);
  console.log(`   Win Rate: ${results.winRate.toFixed(1)}%\n`);
  
  console.log(`💰 P&L:`);
  console.log(`   Paper P&L: ${results.paperPnl >= 0 ? '+' : ''}${results.paperPnl.toFixed(4)} SOL`);
  console.log(`   Total Fees: -${results.totalFees.toFixed(4)} SOL`);
  console.log(`   Mainnet P&L (10% size): ${results.mainnetPnl >= 0 ? '+' : ''}${results.mainnetPnl.toFixed(4)} SOL`);
  console.log(`   Mainnet P&L (${(results.config.positionSize * 100).toFixed(0)}% size): ${results.adjustedMainnetPnl >= 0 ? '+' : ''}${results.adjustedMainnetPnl.toFixed(4)} SOL`);
}

printResults(currentResults);
printResults(proposedResults);

// COMPARISON
console.log('\n\n🔥 UPGRADE IMPACT ANALYSIS');
console.log('='.repeat(80));

const tradeReduction = currentResults.totalTrades - proposedResults.totalTrades;
const tradeReductionPct = (tradeReduction / currentResults.totalTrades) * 100;

const winRateImprovement = proposedResults.winRate - currentResults.winRate;

const mainnetImprovement = proposedResults.adjustedMainnetPnl - currentResults.mainnetPnl;
const mainnetImprovementPct = currentResults.mainnetPnl !== 0 
  ? (mainnetImprovement / Math.abs(currentResults.mainnetPnl)) * 100 
  : 0;

console.log(`\n📉 Trade Volume:`);
console.log(`   ${currentResults.totalTrades} → ${proposedResults.totalTrades} trades (-${tradeReduction} trades, -${tradeReductionPct.toFixed(1)}%)`);

console.log(`\n📈 Win Rate:`);
console.log(`   ${currentResults.winRate.toFixed(1)}% → ${proposedResults.winRate.toFixed(1)}% (${winRateImprovement >= 0 ? '+' : ''}${winRateImprovement.toFixed(1)}%)`);

console.log(`\n💰 Mainnet P&L:`);
console.log(`   ${currentResults.mainnetPnl >= 0 ? '+' : ''}${currentResults.mainnetPnl.toFixed(4)} SOL → ${proposedResults.adjustedMainnetPnl >= 0 ? '+' : ''}${proposedResults.adjustedMainnetPnl.toFixed(4)} SOL`);
console.log(`   Improvement: ${mainnetImprovement >= 0 ? '+' : ''}${mainnetImprovement.toFixed(4)} SOL (${mainnetImprovementPct >= 0 ? '+' : ''}${mainnetImprovementPct.toFixed(1)}%)`);

console.log(`\n🎯 Key Changes:`);
console.log(`   1. Exclude smart-money-only trades (dexscreener source)`);
console.log(`   2. Increase position size from 10% → 12%`);
console.log(`   3. Keep same score/confidence thresholds (60/35)`);

console.log(`\n✅ Expected Outcome:`);
if (proposedResults.adjustedMainnetPnl > currentResults.mainnetPnl) {
  const multiplier = proposedResults.adjustedMainnetPnl / currentResults.mainnetPnl;
  console.log(`   ${multiplier.toFixed(1)}x better mainnet performance`);
  console.log(`   Fewer trades = lower fees`);
  console.log(`   Higher win rate = better capital efficiency`);
} else {
  console.log(`   ⚠️  Upgrade shows worse performance - DO NOT IMPLEMENT`);
}

// BACKUP CURRENT SETTINGS
console.log(`\n\n💾 BACKING UP CURRENT SETTINGS`);
console.log('='.repeat(80));

const backupConfig = {
  version: '1.0',
  timestamp: Date.now(),
  date: new Date().toISOString(),
  settings: CURRENT,
  performance: {
    totalTrades: currentResults.totalTrades,
    winRate: currentResults.winRate,
    mainnetPnl: currentResults.mainnetPnl,
  }
};

const backupFile = '/home/workspace/Projects/survival-agent/config-backup-v1.json';
require('fs').writeFileSync(backupFile, JSON.stringify(backupConfig, null, 2));
console.log(`\n✅ Saved to: ${backupFile}`);

console.log(`\n\n🚀 RECOMMENDATION`);
console.log('='.repeat(80));

if (proposedResults.adjustedMainnetPnl > currentResults.mainnetPnl) {
  console.log(`\n✅ PROCEED WITH UPGRADE`);
  console.log(`\nExpected improvement: ${mainnetImprovement >= 0 ? '+' : ''}${mainnetImprovement.toFixed(4)} SOL`);
  console.log(`Current settings backed up to: config-backup-v1.json`);
  console.log(`\nIf performance worsens, revert using the backup file.`);
} else {
  console.log(`\n❌ DO NOT UPGRADE - Current settings are better`);
}
