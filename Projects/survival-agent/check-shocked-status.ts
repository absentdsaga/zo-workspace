import { ShockedAlphaScanner } from './strategies/shocked-alpha-scanner';

const scanner = new ShockedAlphaScanner();
await scanner.initialize();

console.log('🔍 Checking Shocked watchlist status...\n');

const watchlist = scanner.getWatchlist();
console.log(`📋 Watchlist: ${watchlist.length} tokens\n`);

for (const call of watchlist) {
  const age = (Date.now() - call.addedAt) / (1000 * 60 * 60);
  console.log(`💎 ${call.symbol}`);
  console.log(`   Address: ${call.address.slice(0, 20)}...`);
  console.log(`   Priority: ${call.priority}`);
  console.log(`   Age: ${age.toFixed(1)} hours`);
  console.log(`   Source: ${call.source}`);
  console.log();
}

console.log('🎯 Scanning for opportunities...\n');

const opps = await scanner.scan();
console.log(`Found ${opps.length} opportunities\n`);

for (const opp of opps) {
  console.log(`💎 ${opp.symbol}`);
  console.log(`   Score: ${opp.score}/100 (threshold: 30)`);
  console.log(`   Active: ${opp.isCallActive}`);
  console.log(`   Priority: ${opp.priority}`);
  console.log(`   Momentum 1h: ${opp.momentum.priceChange1h.toFixed(2)}%`);
  console.log(`   Volume 1h: $${opp.momentum.volume1h.toLocaleString()}`);
  
  if (opp.score >= 30 && opp.isCallActive) {
    console.log(`   ✅ WOULD BE PICKED UP BY BOT`);
  } else {
    console.log(`   ❌ Filtered out: ${opp.score < 30 ? 'Score too low' : 'Call not active'}`);
  }
  console.log();
}
