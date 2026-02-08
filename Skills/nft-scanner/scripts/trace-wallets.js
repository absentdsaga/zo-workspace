#!/usr/bin/env node
/**
 * Wallet Tracing Tool - Detect Sybil Attacks
 * 
 * Analyzes wallet funding patterns to identify:
 * - Root wallets funding multiple holder wallets
 * - Coordinated funding patterns (same amounts, same timing)
 * - Sybil clusters (fake unique holders)
 */

const { Connection, PublicKey } = require('@solana/web3.js');

const RPC_URL = process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com';
const connection = new Connection(RPC_URL, 'confirmed');

async function getWalletFundingSources(walletAddress, limit = 100) {
    const pubkey = new PublicKey(walletAddress);
    
    // Get transaction signatures (oldest first to find initial funding)
    const signatures = await connection.getSignaturesForAddress(pubkey, { limit });
    
    if (signatures.length === 0) {
        return { wallet: walletAddress, fundingSources: [], error: 'No transactions found' };
    }
    
    // Get the oldest transaction (likely the funding transaction)
    const oldestSig = signatures[signatures.length - 1];
    const tx = await connection.getParsedTransaction(oldestSig.signature, {
        maxSupportedTransactionVersion: 0
    });
    
    if (!tx || !tx.meta) {
        return { wallet: walletAddress, fundingSources: [], error: 'Could not parse transaction' };
    }
    
    // Find SOL transfers to this wallet
    const fundingSources = [];
    
    if (tx.transaction.message.instructions) {
        for (const instruction of tx.transaction.message.instructions) {
            if (instruction.program === 'system' && instruction.parsed?.type === 'transfer') {
                const info = instruction.parsed.info;
                if (info.destination === walletAddress) {
                    fundingSources.push({
                        source: info.source,
                        amount: info.lamports / 1e9,
                        signature: oldestSig.signature,
                        blockTime: oldestSig.blockTime
                    });
                }
            }
        }
    }
    
    return { wallet: walletAddress, fundingSources, blockTime: oldestSig.blockTime };
}

async function analyzeFundingPatterns(holders) {
    console.log(`\n🔍 Analyzing funding patterns for ${holders.length} wallets...\n`);
    console.log('This may take several minutes due to RPC rate limits...\n');
    
    const results = [];
    const fundingSourceMap = new Map(); // source -> [wallets it funded]
    
    for (let i = 0; i < holders.length; i++) {
        const holder = holders[i];
        
        if (i > 0 && i % 10 === 0) {
            console.log(`Progress: ${i}/${holders.length} wallets analyzed...`);
            // Rate limiting
            await new Promise(r => setTimeout(r, 1000));
        }
        
        try {
            const result = await getWalletFundingSources(holder.owner);
            results.push(result);
            
            // Track funding sources
            for (const source of result.fundingSources) {
                if (!fundingSourceMap.has(source.source)) {
                    fundingSourceMap.set(source.source, []);
                }
                fundingSourceMap.get(source.source).push({
                    wallet: holder.owner,
                    amount: source.amount,
                    tokens: holder.tokens,
                    blockTime: result.blockTime
                });
            }
        } catch (error) {
            console.error(`  Error analyzing ${holder.owner}: ${error.message}`);
            results.push({ wallet: holder.owner, fundingSources: [], error: error.message });
        }
    }
    
    return { results, fundingSourceMap };
}

async function detectSybilClusters(magicEdenSlug, sampleSize = 50) {
    console.log(`\n🕵️  SYBIL ATTACK DETECTION\n`);
    console.log(`═══════════════════════════════════════`);
    
    // Get holder data
    const response = await fetch(`https://api-mainnet.magiceden.dev/v2/collections/${magicEdenSlug}/holder_stats`);
    const data = await response.json();
    
    console.log(`Total Holders: ${data.uniqueHolders.toLocaleString()}`);
    console.log(`Sample Size: ${sampleSize} top holders\n`);
    
    // Analyze top holders
    const holdersToCheck = data.topHolders.slice(0, sampleSize);
    
    const { results, fundingSourceMap } = await analyzeFundingPatterns(holdersToCheck);
    
    console.log(`\n\n📊 FUNDING SOURCE ANALYSIS\n`);
    console.log(`═══════════════════════════════════════\n`);
    
    // Find suspicious funding sources (funding multiple holders)
    const suspiciousSources = [];
    
    for (const [source, wallets] of fundingSourceMap.entries()) {
        if (wallets.length > 1) {
            const totalTokens = wallets.reduce((sum, w) => sum + w.tokens, 0);
            const avgAmount = wallets.reduce((sum, w) => sum + w.amount, 0) / wallets.length;
            
            suspiciousSources.push({
                source,
                walletsCount: wallets.length,
                totalTokens,
                avgFundingAmount: avgAmount.toFixed(4),
                wallets
            });
        }
    }
    
    // Sort by number of wallets funded
    suspiciousSources.sort((a, b) => b.walletsCount - a.walletsCount);
    
    if (suspiciousSources.length === 0) {
        console.log('✅ NO SUSPICIOUS PATTERNS DETECTED\n');
        console.log('Each sampled holder was funded by a unique source.\n');
        console.log('This suggests genuine organic holder distribution.\n');
    } else {
        console.log(`⚠️  POTENTIAL SYBIL CLUSTERS DETECTED\n`);
        console.log(`Found ${suspiciousSources.length} funding sources that funded multiple holders:\n`);
        
        for (let i = 0; i < Math.min(10, suspiciousSources.length); i++) {
            const cluster = suspiciousSources[i];
            const shortSource = cluster.source.slice(0, 8) + '...' + cluster.source.slice(-6);
            
            console.log(`${i + 1}. Root Wallet: ${shortSource}`);
            console.log(`   → Funded ${cluster.walletsCount} holder wallets`);
            console.log(`   → Those wallets hold ${cluster.totalTokens} NFTs total`);
            console.log(`   → Avg funding: ${cluster.avgFundingAmount} SOL`);
            
            // Check if funding amounts are suspiciously similar
            const amounts = cluster.wallets.map(w => w.amount);
            const uniqueAmounts = new Set(amounts);
            if (uniqueAmounts.size === 1) {
                console.log(`   ⚠️  All funded with EXACT same amount (${amounts[0]} SOL)`);
            }
            
            // Check if funded at similar times
            const times = cluster.wallets.map(w => w.blockTime).filter(t => t);
            if (times.length > 1) {
                const timeRange = Math.max(...times) - Math.min(...times);
                if (timeRange < 3600) { // Within 1 hour
                    console.log(`   ⚠️  All funded within ${Math.floor(timeRange / 60)} minutes`);
                }
            }
            
            console.log();
        }
        
        // Calculate what % of sampled holders are in clusters
        const walletsInClusters = suspiciousSources.reduce((sum, s) => sum + s.walletsCount, 0);
        const clusterPercentage = ((walletsInClusters / sampleSize) * 100).toFixed(1);
        
        console.log(`\n💡 CLUSTER IMPACT`);
        console.log(`   ${walletsInClusters}/${sampleSize} sampled wallets (${clusterPercentage}%) are in suspicious clusters`);
        
        if (clusterPercentage > 30) {
            console.log(`   🚨 HIGH RISK - Significant Sybil activity detected`);
        } else if (clusterPercentage > 15) {
            console.log(`   ⚡ MODERATE RISK - Some clustering detected`);
        } else {
            console.log(`   ⚠️  LOW RISK - Minor clustering (could be legitimate multi-wallet users)`);
        }
    }
    
    console.log(`\n═══════════════════════════════════════\n`);
    
    return { suspiciousSources, sampleSize, analysisResults: results };
}

// CLI
const command = process.argv[2];
const arg = process.argv[3];

if (!command) {
    console.log(`
Wallet Tracing Tool - Detect Sybil Attacks

Usage:
  node trace-wallets.js detect <magic-eden-slug> [sample-size]
  node trace-wallets.js trace <wallet-address>

Examples:
  node trace-wallets.js detect neural_norse 50
  node trace-wallets.js trace 991x9hnsaKBBqfLRsayPHoC91n3rT9waWDPBUSu35HzG

Note: Due to RPC rate limits, analyzing 50 wallets takes ~5-10 minutes
    `);
    process.exit(0);
}

(async () => {
    try {
        switch (command) {
            case 'detect':
                const sampleSize = parseInt(process.argv[4]) || 50;
                await detectSybilClusters(arg, sampleSize);
                break;
            case 'trace':
                const result = await getWalletFundingSources(arg);
                console.log(JSON.stringify(result, null, 2));
                break;
            default:
                console.error(`Unknown command: ${command}`);
                process.exit(1);
        }
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
})();

module.exports = { getWalletFundingSources, detectSybilClusters };
