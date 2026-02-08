// Simple clustering heuristic based on holder stats
const holderData = {
  totalSupply: 7287,
  uniqueHolders: 986,
  topHolders: [
    { tokens: 109 },
    { tokens: 100 },
    { tokens: 84 },
    { tokens: 51 },
    { tokens: 33 }
  ],
  histogram: [
    { range: "1 NFT", count: 51 },
    { range: "2-5 NFTs", count: 229 },
    { range: "6-24 NFTs", count: 704 },
    { range: "25-49 NFTs", count: 2 },
    { range: "50+ NFTs", count: 4 }
  ],
  maxPerWallet: 10
};

console.log("\n🔍 HEURISTIC CLUSTERING ANALYSIS\n");
console.log("════════════════════════════════════════\n");

// Check 1: Max per wallet enforcement
const walletsOver10 = holderData.histogram.filter(h => h.range.includes("25-") || h.range.includes("50+"))
  .reduce((sum, h) => sum + h.count, 0);

console.log("✅ Max Per Wallet Check:");
console.log(`   ${walletsOver10} wallets exceed the 10 NFT limit`);
console.log(`   This is ${((walletsOver10/holderData.uniqueHolders)*100).toFixed(1)}% of holders`);

if (walletsOver10 > 10) {
  console.log(`   ⚠️  Limit bypass detected - possible early minter privilege\n`);
} else {
  console.log(`   → Very few exceptions, limit mostly enforced\n`);
}

// Check 2: Distribution entropy
const avgPerHolder = holderData.totalSupply / holderData.uniqueHolders;
console.log("📊 Distribution Metrics:");
console.log(`   Avg per holder: ${avgPerHolder.toFixed(2)} NFTs`);
console.log(`   Most common range: 6-24 NFTs (${holderData.histogram[2].count} wallets)`);

// Check 3: Whale concentration
const top5 = holderData.topHolders.slice(0, 5).reduce((sum, h) => sum + h.tokens, 0);
const top5Pct = (top5 / holderData.totalSupply * 100).toFixed(1);
console.log(`   Top 5 whales own: ${top5Pct}% of supply`);

if (top5Pct < 10) {
  console.log(`   ✅ LOW concentration - well distributed\n`);
} else if (top5Pct < 20) {
  console.log(`   ⚠️  MODERATE concentration\n`);
} else {
  console.log(`   🚨 HIGH concentration - possible clustering\n`);
}

// Check 4: Expected Sybil patterns
console.log("🕵️  Sybil Attack Indicators:");

const walletsAt10Exactly = Math.floor((holderData.histogram[2].count * 0.15)); // estimate
console.log(`   Est. ${walletsAt10Exactly}+ wallets at exactly 10 NFTs`);

if (walletsAt10Exactly > 100) {
  console.log(`   ⚠️  Many wallets hitting exact limit - POSSIBLE Sybil pattern`);
  console.log(`   → Single entity could be using multiple wallets\n`);
} else {
  console.log(`   → Natural distribution, not hitting limit uniformly\n`);
}

// Final verdict
console.log("════════════════════════════════════════");
console.log("🏁 VERDICT:\n");

const clusteringScore = 
  (top5Pct < 10 ? 0 : 1) + 
  (walletsOver10 > 10 ? 1 : 0) +
  (walletsAt10Exactly > 100 ? 1 : 0);

if (clusteringScore === 0) {
  console.log("✅ LOW RISK - Appears organically distributed");
  console.log("   • Low whale concentration");
  console.log("   • Natural distribution pattern");
  console.log("   • Anti-whale limits working");
} else if (clusteringScore === 1) {
  console.log("⚡ MODERATE RISK - Some clustering indicators");
  console.log("   • May have some multi-wallet holders");
  console.log("   • Overall distribution still reasonable");
} else {
  console.log("🚨 HIGH RISK - Multiple Sybil indicators");
  console.log("   • Suspicious concentration patterns");
  console.log("   • Possible coordinated multi-wallet strategy");
}

console.log("\n💡 NOTE: On-chain tracing required for definitive proof");
console.log("   Use Bubblemaps or Helius RPC for deep analysis");
console.log("════════════════════════════════════════\n");
