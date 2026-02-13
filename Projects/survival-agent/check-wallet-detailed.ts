#!/usr/bin/env bun

import { Connection, Keypair, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';

async function main() {
  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const heliusKey = process.env.HELIUS_RPC_URL;

  if (!privateKey || !heliusKey) {
    console.error('❌ Missing environment variables');
    process.exit(1);
  }

  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;
  const connection = new Connection(rpcUrl, 'confirmed');

  const keypair = Keypair.fromSecretKey(new Uint8Array(JSON.parse(privateKey)));
  const walletPubkey = keypair.publicKey;

  console.log(`\n🔍 WALLET INVESTIGATION`);
  console.log(`Wallet: ${walletPubkey.toString()}\n`);

  // Get SOL balance
  const balance = await connection.getBalance(walletPubkey);
  const sol = balance / LAMPORTS_PER_SOL;
  console.log(`💰 SOL Balance: ${sol.toFixed(4)} SOL (~$${(sol * 119).toFixed(2)})\n`);

  // Get all token accounts
  const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
    walletPubkey,
    { programId: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA') }
  );

  console.log(`📊 Token Holdings (${tokenAccounts.value.length} tokens):\n`);

  for (const account of tokenAccounts.value) {
    const mint = account.account.data.parsed.info.mint;
    const amount = account.account.data.parsed.info.tokenAmount.uiAmount;
    const decimals = account.account.data.parsed.info.tokenAmount.decimals;

    console.log(`Token: ${mint}`);
    console.log(`  Amount: ${amount} (${decimals} decimals)`);

    // Try to get token info from DexScreener
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${mint}`);
      if (response.ok) {
        const data = await response.json();
        if (data.pairs && data.pairs.length > 0) {
          const pair = data.pairs[0];
          const price = parseFloat(pair.priceUsd);
          const value = amount * price;
          console.log(`  Symbol: ${pair.baseToken.symbol}`);
          console.log(`  Price: $${price.toFixed(8)}`);
          console.log(`  Value: $${value.toFixed(2)}`);
        }
      }
    } catch (error) {
      console.log(`  (Unable to fetch price)`);
    }
    console.log('');
  }

  // Get recent transaction signatures
  console.log(`\n📜 Recent Transactions (last 20):\n`);

  const signatures = await connection.getSignaturesForAddress(walletPubkey, { limit: 20 });

  for (const sig of signatures) {
    const time = new Date(sig.blockTime! * 1000).toLocaleString();
    const status = sig.err ? '❌ FAILED' : '✅ SUCCESS';
    console.log(`${status} ${time}`);
    console.log(`  Sig: ${sig.signature}`);
    console.log(`  https://solscan.io/tx/${sig.signature}`);
    console.log('');
  }

  // Check for NPC token specifically
  console.log(`\n🔍 Checking for NPC token trades...\n`);

  const NPC_MINT = 'APVtp27iz6y4GuXeKT9pVD96VvPA5k1po1f2eryKpump';

  let npcBuyCount = 0;
  let npcSellCount = 0;

  for (const sig of signatures) {
    try {
      const tx = await connection.getParsedTransaction(sig.signature, {
        maxSupportedTransactionVersion: 0
      });

      if (!tx) continue;

      const instructions = tx.transaction.message.instructions;
      
      for (const ix of instructions) {
        if ('parsed' in ix && ix.parsed && ix.parsed.type === 'transfer') {
          const info = ix.parsed.info;
          // Check if involves NPC token
          if (info.mint === NPC_MINT || info.destination === NPC_MINT || info.source === NPC_MINT) {
            const time = new Date(sig.blockTime! * 1000).toLocaleTimeString();
            console.log(`${time} - NPC activity in ${sig.signature.substring(0, 8)}...`);
          }
        }
      }

      // Check if it's a Jupiter swap involving NPC
      const logMessages = tx.meta?.logMessages || [];
      const isJupiterSwap = logMessages.some(log => log.includes('Jupiter'));
      const involvesNPC = logMessages.some(log => log.includes(NPC_MINT));

      if (isJupiterSwap && involvesNPC) {
        const time = new Date(sig.blockTime! * 1000).toLocaleTimeString();
        
        // Determine if buy or sell by checking SOL transfers
        const preBalances = tx.meta?.preBalances || [];
        const postBalances = tx.meta?.postBalances || [];
        const solChange = (postBalances[0] - preBalances[0]) / LAMPORTS_PER_SOL;

        if (solChange < 0) {
          npcBuyCount++;
          console.log(`🟢 BUY  ${time}: ${Math.abs(solChange).toFixed(4)} SOL → NPC`);
        } else {
          npcSellCount++;
          console.log(`🔴 SELL ${time}: NPC → ${solChange.toFixed(4)} SOL`);
        }
        console.log(`   Tx: https://solscan.io/tx/${sig.signature}`);
        console.log('');
      }

    } catch (error) {
      // Skip failed tx parsing
    }
  }

  console.log(`\n📊 NPC Summary:`);
  console.log(`  Total Buys: ${npcBuyCount}`);
  console.log(`  Total Sells: ${npcSellCount}`);
  console.log(`  Net: ${npcBuyCount - npcSellCount} (${npcBuyCount - npcSellCount > 0 ? 'still holding' : 'fully exited'})`);
}

main();
