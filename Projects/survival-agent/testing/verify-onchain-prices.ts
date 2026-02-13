#!/usr/bin/env bun
/**
 * On-Chain Price Verification
 * Compares DexScreener API vs actual on-chain Jupiter quotes
 */

import { Connection, PublicKey } from '@solana/web3.js';

const HELIUS_API_KEY = process.env.HELIUS_API_KEY || process.env.HELIUS_RPC_URL;
const JUP_API_KEY = process.env.JUP_TOKEN;

interface PriceComparison {
  token: string;
  address: string;
  dexScreener: {
    price: number;
    timestamp: string;
    liquidity: number;
    source: string;
  } | null;
  jupiter: {
    price: number;
    inAmount: string;
    outAmount: string;
  } | null;
  helius: {
    exists: boolean;
    metadata?: any;
  } | null;
}

async function getDexScreenerPrice(address: string) {
  try {
    const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
    const data = await response.json();

    if (data.pairs && data.pairs.length > 0) {
      const bestPair = data.pairs.sort((a: any, b: any) =>
        (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)
      )[0];

      return {
        price: parseFloat(bestPair.priceUsd || '0'),
        timestamp: bestPair.pairCreatedAt || 'unknown',
        liquidity: bestPair.liquidity?.usd || 0,
        source: bestPair.dexId || 'unknown'
      };
    }
  } catch (error) {
    console.error(`DexScreener error: ${error}`);
  }
  return null;
}

async function getJupiterQuote(tokenAddress: string) {
  // Get a quote for swapping 0.01 SOL to this token
  const SOL_MINT = 'So11111111111111111111111111111111111111112';
  const amountInLamports = 10_000_000; // 0.01 SOL

  try {
    const url = `https://quote-api.jup.ag/v6/quote?inputMint=${SOL_MINT}&outputMint=${tokenAddress}&amount=${amountInLamports}&slippageBps=50`;

    const response = await fetch(url, {
      headers: JUP_API_KEY ? { 'x-api-key': JUP_API_KEY } : {}
    });

    if (!response.ok) {
      return null;
    }

    const quote = await response.json();

    if (quote.outAmount) {
      // Calculate price: how much USD per token
      // If we're swapping 0.01 SOL ($1.19) for X tokens, price = $1.19 / X
      const solPrice = 119; // Approximate SOL price
      const amountInUsd = (amountInLamports / 1e9) * solPrice;
      const tokensReceived = parseInt(quote.outAmount) / 1e6; // Assume 6 decimals (may vary)
      const pricePerToken = amountInUsd / tokensReceived;

      return {
        price: pricePerToken,
        inAmount: quote.inAmount,
        outAmount: quote.outAmount
      };
    }
  } catch (error) {
    console.error(`Jupiter error: ${error}`);
  }
  return null;
}

async function getHeliusTokenInfo(address: string) {
  try {
    const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}`;
    const connection = new Connection(rpcUrl, 'confirmed');

    const pubkey = new PublicKey(address);
    const accountInfo = await connection.getAccountInfo(pubkey);

    if (accountInfo) {
      return {
        exists: true,
        metadata: {
          owner: accountInfo.owner.toString(),
          lamports: accountInfo.lamports,
          dataLength: accountInfo.data.length
        }
      };
    }
  } catch (error) {
    console.error(`Helius error: ${error}`);
  }
  return { exists: false };
}

async function verifyToken(symbol: string, address: string): Promise<PriceComparison> {
  console.log(`\n🔍 Verifying ${symbol} (${address})...`);
  console.log('━'.repeat(70));

  const [dexScreener, jupiter, helius] = await Promise.all([
    getDexScreenerPrice(address),
    getJupiterQuote(address),
    getHeliusTokenInfo(address)
  ]);

  return {
    token: symbol,
    address,
    dexScreener,
    jupiter,
    helius
  };
}

async function main() {
  console.log('🔬 ON-CHAIN PRICE VERIFICATION TOOL\n');
  console.log('Comparing DexScreener API vs Jupiter on-chain quotes');
  console.log('━'.repeat(70));

  if (!HELIUS_API_KEY || !JUP_API_KEY) {
    console.error('❌ Missing API keys');
    console.error('Required: HELIUS_API_KEY, JUP_TOKEN');
    process.exit(1);
  }

  // Parse current positions from paper trade log
  const logPath = '/tmp/paper-trade-final.log';
  let positions: { symbol: string; address: string }[] = [];

  try {
    const logContent = await Bun.file(logPath).text();
    const lines = logContent.split('\n');

    // Extract unique tokens from "Token: NAME (ADDRESS...)" lines
    const tokenMatches = new Set<string>();
    for (const line of lines) {
      const match = line.match(/Token: (.+?) \(([A-Za-z0-9]+)\.\.\.\)/);
      if (match) {
        tokenMatches.add(JSON.stringify({ symbol: match[1], address: match[2] }));
      }
    }

    positions = Array.from(tokenMatches).map(s => JSON.parse(s));
  } catch (error) {
    console.error('⚠️  Could not read log file');
  }

  if (positions.length === 0) {
    console.log('\n❌ No positions found in log\n');
    console.log('Testing with example token instead...\n');
    positions = [{
      symbol: 'Example',
      address: 'So11111111111111111111111111111111111111112' // SOL
    }];
  }

  // Verify each token
  const results: PriceComparison[] = [];
  for (const pos of positions) {
    const result = await verifyToken(pos.symbol, pos.address);
    results.push(result);

    // Display results
    console.log(`\n📊 ${result.token}`);
    console.log('─'.repeat(70));

    if (result.dexScreener) {
      console.log(`✅ DexScreener:`);
      console.log(`   Price: $${result.dexScreener.price.toFixed(8)}`);
      console.log(`   Liquidity: $${result.dexScreener.liquidity.toLocaleString()}`);
      console.log(`   Source: ${result.dexScreener.source}`);
      console.log(`   Timestamp: ${result.dexScreener.timestamp}`);
    } else {
      console.log(`❌ DexScreener: No data (token may be delisted)`);
    }

    if (result.jupiter) {
      console.log(`✅ Jupiter (on-chain quote):`);
      console.log(`   Estimated Price: $${result.jupiter.price.toFixed(8)}`);
      console.log(`   Quote: ${result.jupiter.inAmount} → ${result.jupiter.outAmount}`);
    } else {
      console.log(`❌ Jupiter: No route (token may be illiquid/rugged)`);
    }

    if (result.helius?.exists) {
      console.log(`✅ Helius: Token account exists on-chain`);
    } else {
      console.log(`❌ Helius: Token account not found`);
    }

    // Compare prices
    if (result.dexScreener && result.jupiter) {
      const priceDiff = Math.abs(result.dexScreener.price - result.jupiter.price);
      const priceDiffPercent = (priceDiff / result.dexScreener.price) * 100;

      console.log(`\n🔄 Price Comparison:`);
      console.log(`   Difference: ${priceDiffPercent.toFixed(2)}%`);

      if (priceDiffPercent > 10) {
        console.log(`   ⚠️  LARGE DISCREPANCY - DexScreener may have stale data`);
      } else {
        console.log(`   ✅ Prices match (within 10%)`);
      }
    }
  }

  // Final summary
  console.log('\n' + '━'.repeat(70));
  console.log('📈 SUMMARY\n');

  const dexScreenerWorking = results.filter(r => r.dexScreener !== null).length;
  const jupiterWorking = results.filter(r => r.jupiter !== null).length;
  const onChainExists = results.filter(r => r.helius?.exists).length;

  console.log(`DexScreener API: ${dexScreenerWorking}/${results.length} tokens found`);
  console.log(`Jupiter quotes: ${jupiterWorking}/${results.length} tokens routable`);
  console.log(`On-chain verification: ${onChainExists}/${results.length} tokens exist\n`);

  if (jupiterWorking === 0 && results.length > 0) {
    console.log('⚠️  WARNING: Jupiter cannot route any of these tokens');
    console.log('   This suggests tokens are rugged/delisted/illiquid\n');
  }

  if (dexScreenerWorking > 0 && jupiterWorking === 0) {
    console.log('⚠️  CRITICAL: DexScreener shows data but Jupiter has no routes');
    console.log('   DexScreener data is likely STALE/CACHED - NOT real-time\n');
  }
}

main().catch(console.error);
