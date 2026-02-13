/**
 * Populate blacklist from existing trade history
 * Run this once to blacklist all tokens that have rugged in past trades
 */

const TRADES_FILE = '/tmp/paper-trades-master.json';
const BLACKLIST_FILE = '/tmp/paper-trades-blacklist.json';

async function main() {
  console.log('🔍 Analyzing trade history for rugged tokens...\n');

  // Load existing trades
  let trades: any[] = [];
  try {
    const content = await Bun.file(TRADES_FILE).text();
    const data = JSON.parse(content);
    trades = Array.isArray(data) ? data : (data.trades || []);
  } catch {
    console.error('❌ Could not load trade history');
    process.exit(1);
  }

  // Find all rugged tokens
  const ruggedTokens = new Set<string>();
  const ruggedDetails: { address: string; symbol: string; count: number }[] = [];

  for (const trade of trades) {
    if (trade.exitReason?.includes('rugged') || trade.exitReason?.includes('No sell route')) {
      if (!ruggedTokens.has(trade.tokenAddress)) {
        ruggedDetails.push({
          address: trade.tokenAddress,
          symbol: trade.tokenSymbol,
          count: 1
        });
      } else {
        const existing = ruggedDetails.find(d => d.address === trade.tokenAddress);
        if (existing) existing.count++;
      }
      ruggedTokens.add(trade.tokenAddress);
    }
  }

  console.log(`📊 Found ${ruggedTokens.size} rugged tokens:\n`);
  
  // Sort by count (most rugged first)
  ruggedDetails.sort((a, b) => b.count - a.count);
  
  for (const detail of ruggedDetails) {
    console.log(`   🚫 ${detail.symbol} (${detail.address.slice(0, 8)}...) - rugged ${detail.count}x`);
  }

  // Save to blacklist file
  const blacklistData = {
    ruggedTokens: Array.from(ruggedTokens),
    lastUpdated: Date.now()
  };

  await Bun.write(BLACKLIST_FILE, JSON.stringify(blacklistData, null, 2));
  
  console.log(`\n✅ Blacklist saved to ${BLACKLIST_FILE}`);
  console.log(`🚫 ${ruggedTokens.size} tokens will now be blocked from future trades\n`);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
