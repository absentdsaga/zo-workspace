#!/usr/bin/env node
/**
 * NFT Scanner - Analyze Solana NFT Collections
 * 
 * Features:
 * - Collection stats (supply, minted, remaining)
 * - Holder distribution analysis
 * - Whale detection
 * - Wallet clustering via Bubblemaps integration
 */

const COLLECTIONS = {
    'neural-norse': {
        api: 'https://neural-norse.vercel.app/api',
        candyMachine: 'A4bJ1pWt14cimYCUqNv1iZyyQuLY5m58LzetySLsBURW',
        magicEdenSlug: 'neural_norse'
    }
};

async function getCollectionStats(collectionName) {
    const collection = COLLECTIONS[collectionName];
    if (!collection) {
        throw new Error(`Unknown collection: ${collectionName}. Available: ${Object.keys(COLLECTIONS).join(', ')}`);
    }

    console.log(`\n📊 Fetching stats for ${collectionName}...\n`);

    const response = await fetch(`${collection.api}/collection`);
    const data = await response.json();

    console.log(`═══════════════════════════════════════`);
    console.log(`  ${data.name} (${data.symbol})`);
    console.log(`═══════════════════════════════════════`);
    console.log(`  Description: ${data.description}`);
    console.log(`  Blockchain: ${data.blockchain}`);
    console.log(`  Standard: ${data.standard}`);
    console.log(`\n📈 SUPPLY`);
    console.log(`  Total Supply: ${data.totalSupply.toLocaleString()}`);
    console.log(`  Public Supply: ${data.publicSupply.toLocaleString()}`);
    console.log(`  Reserved: ${data.reserved.toLocaleString()}`);
    console.log(`\n🔥 MINT STATUS`);
    console.log(`  Status: ${data.mintStatus}`);
    console.log(`  Claimed: ${data.claimed.toLocaleString()} (${((data.claimed / data.totalSupply) * 100).toFixed(2)}%)`);
    console.log(`  Available: ${data.available.toLocaleString()}`);
    console.log(`  Price: ${data.price}`);
    console.log(`  Total Cost: ${data.totalCostPerMint}`);
    console.log(`\n⚙️  MINT METHOD`);
    console.log(`  Method: ${data.mint.method}`);
    console.log(`  Algorithm: ${data.mint.algorithm}`);
    console.log(`  Difficulty: ${data.mint.difficulty}`);
    console.log(`  Max Per Wallet: ${data.mint.maxPerWallet}`);
    console.log(`  Candy Machine: ${data.mint.candyMachine}`);
    console.log(`═══════════════════════════════════════\n`);

    return data;
}

async function analyzeHolders(collectionName) {
    const collection = COLLECTIONS[collectionName];
    if (!collection) {
        throw new Error(`Unknown collection: ${collectionName}`);
    }

    console.log(`\n👥 Fetching holder distribution for ${collectionName}...\n`);

    const response = await fetch(`https://api-mainnet.magiceden.dev/v2/collections/${collection.magicEdenSlug}/holder_stats`);
    const data = await response.json();

    const totalNFTs = data.totalSupply;
    const uniqueHolders = data.uniqueHolders;
    const avgPerHolder = (totalNFTs / uniqueHolders).toFixed(2);

    console.log(`═══════════════════════════════════════`);
    console.log(`  HOLDER DISTRIBUTION ANALYSIS`);
    console.log(`═══════════════════════════════════════`);
    console.log(`  Total NFTs: ${totalNFTs.toLocaleString()}`);
    console.log(`  Unique Holders: ${uniqueHolders.toLocaleString()}`);
    console.log(`  Avg per Holder: ${avgPerHolder}`);
    console.log(`\n📊 DISTRIBUTION BREAKDOWN`);

    // Analyze histogram
    const histogram = data.tokenHistogram.bars;
    for (const bar of histogram) {
        const range = bar.l_val === 1 ? '1 NFT' : 
                     bar.l_val === 2 ? '2-5 NFTs' :
                     bar.l_val === 6 ? '6-24 NFTs' :
                     bar.l_val === 25 ? '25-49 NFTs' :
                     bar.l_val === 50 ? '50+ NFTs' : `${bar.l_val}+ NFTs`;
        console.log(`  ${bar.hight} wallets hold ${range}`);
    }

    console.log(`\n🐋 TOP 10 WHALES`);
    console.log(`═══════════════════════════════════════`);

    const topHolders = data.topHolders.slice(0, 10);
    for (let i = 0; i < topHolders.length; i++) {
        const holder = topHolders[i];
        const percentage = ((holder.tokens / totalNFTs) * 100).toFixed(2);
        const shortAddress = holder.owner.slice(0, 8) + '...' + holder.owner.slice(-6);
        console.log(`  ${i + 1}. ${shortAddress}: ${holder.tokens} NFTs (${percentage}%)`);
    }

    // Calculate concentration
    const top10Total = topHolders.reduce((sum, h) => sum + h.tokens, 0);
    const top10Percentage = ((top10Total / totalNFTs) * 100).toFixed(2);

    console.log(`\n💡 CONCENTRATION ANALYSIS`);
    console.log(`  Top 10 holders own: ${top10Total.toLocaleString()} NFTs (${top10Percentage}%)`);
    
    if (top10Percentage > 50) {
        console.log(`  ⚠️  HIGH CONCENTRATION - Top 10 control majority`);
    } else if (top10Percentage > 30) {
        console.log(`  ⚡ MODERATE CONCENTRATION`);
    } else {
        console.log(`  ✅ WELL DISTRIBUTED - Decentralized ownership`);
    }

    console.log(`═══════════════════════════════════════\n`);

    return data;
}

async function checkClustering(candyMachineOrSlug) {
    // Try to determine if input is a candy machine address or collection slug
    let candyMachine, slug;
    
    if (candyMachineOrSlug.length > 40) {
        // Likely a candy machine address
        candyMachine = candyMachineOrSlug;
        // Try to find matching collection
        for (const [name, data] of Object.entries(COLLECTIONS)) {
            if (data.candyMachine === candyMachine) {
                slug = name;
                break;
            }
        }
    } else {
        // Collection name/slug
        slug = candyMachineOrSlug;
        const collection = COLLECTIONS[slug];
        if (collection) {
            candyMachine = collection.candyMachine;
        }
    }

    console.log(`\n🔍 Checking wallet clustering...\n`);

    if (candyMachine) {
        console.log(`Candy Machine: ${candyMachine}`);
        console.log(`\n📍 Bubblemaps Analysis:`);
        console.log(`   View interactive map: https://v2.bubblemaps.io/sol/token/${candyMachine}`);
    }

    // Try to fetch holder stats to analyze patterns
    if (slug) {
        const collection = COLLECTIONS[slug];
        if (collection && collection.magicEdenSlug) {
            try {
                const response = await fetch(`https://api-mainnet.magiceden.dev/v2/collections/${collection.magicEdenSlug}/holder_stats`);
                const data = await response.json();

                console.log(`\n🔬 CLUSTERING INDICATORS:\n`);

                // Look for suspicious patterns
                const topHolders = data.topHolders.slice(0, 30);
                const maxPerWallet = Math.max(...topHolders.map(h => h.tokens));
                const walletsAtMax = topHolders.filter(h => h.tokens === maxPerWallet).length;

                console.log(`  Max NFTs per wallet: ${maxPerWallet}`);
                console.log(`  Wallets at max: ${walletsAtMax}`);

                if (walletsAtMax >= 10) {
                    console.log(`  ⚠️  POTENTIAL CLUSTERING: Many wallets hitting same limit`);
                    console.log(`     → Could indicate single entity with multiple wallets`);
                } else {
                    console.log(`  ✅ Natural distribution pattern`);
                }

                // Check if there's a "max per wallet" limit being enforced
                const collection = COLLECTIONS[slug];
                if (collection) {
                    const statsResponse = await fetch(`${collection.api}/collection`);
                    const stats = await statsResponse.json();
                    if (stats.mint && stats.mint.maxPerWallet) {
                        console.log(`\n  Max Per Wallet Limit: ${stats.mint.maxPerWallet}`);
                        console.log(`  → Anti-whale mechanism in place`);
                        
                        const walletsAtLimit = topHolders.filter(h => h.tokens === stats.mint.maxPerWallet).length;
                        if (walletsAtLimit > 0) {
                            console.log(`  → ${walletsAtLimit} wallets have reached the limit`);
                        }
                    }
                }

            } catch (error) {
                console.log(`  Could not fetch holder data: ${error.message}`);
            }
        }
    }

    console.log(`\n💡 For detailed clustering analysis, visit Bubblemaps:`);
    if (candyMachine) {
        console.log(`   https://v2.bubblemaps.io/sol/token/${candyMachine}\n`);
    }
    console.log(`   Bubblemaps will show visual connections between wallets\n`);
}

// CLI Interface
const command = process.argv[2];
const arg = process.argv[3];

if (!command) {
    console.log(`
NFT Scanner - Analyze Solana NFT Collections

Usage:
  node scanner.js stats <collection-name>       - Show collection statistics
  node scanner.js holders <collection-name>     - Analyze holder distribution
  node scanner.js clustering <collection-name>  - Check for wallet clustering
  node scanner.js all <collection-name>         - Run all analyses

Available collections:
  ${Object.keys(COLLECTIONS).join(', ')}

Examples:
  node scanner.js stats neural-norse
  node scanner.js holders neural-norse
  node scanner.js all neural-norse
    `);
    process.exit(0);
}

(async () => {
    try {
        switch (command) {
            case 'stats':
                await getCollectionStats(arg);
                break;
            case 'holders':
                await analyzeHolders(arg);
                break;
            case 'clustering':
                await checkClustering(arg);
                break;
            case 'all':
                await getCollectionStats(arg);
                await analyzeHolders(arg);
                await checkClustering(arg);
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

module.exports = { getCollectionStats, analyzeHolders, checkClustering };
