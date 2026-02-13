#!/usr/bin/env bun
/**
 * Sell all meme token holdings
 */

import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddress, TOKEN_PROGRAM_ID } from '@solana/spl-token';
import bs58 from 'bs58';

async function main() {
  console.log('🔥 SELLING ALL MEME TOKENS\n');

  // Load credentials
  const privateKeyBase58 = process.env.SOLANA_PRIVATE_KEY;
  const heliusKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const jupToken = process.env.JUP_TOKEN;

  if (!privateKeyBase58 || !heliusKey || !jupToken) {
    console.error('❌ Missing credentials');
    console.error('Need: SOLANA_PRIVATE_KEY, HELIUS_RPC_URL (or HELIUS_API_KEY), JUP_TOKEN');
    console.error(`Got: PK=${!!privateKeyBase58}, Helius=${!!heliusKey}, Jup=${!!jupToken}`);
    process.exit(1);
  }

  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;
  const connection = new Connection(rpcUrl, 'confirmed');

  // Parse private key (base58 format)
  const keypair = Keypair.fromSecretKey(bs58.decode(privateKeyBase58));
  const walletAddress = keypair.publicKey;

  console.log(`💼 Wallet: ${walletAddress.toString()}\n`);

  // Get all token accounts
  console.log('🔍 Scanning for token holdings...\n');
  const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
    walletAddress,
    { programId: TOKEN_PROGRAM_ID }
  );

  if (tokenAccounts.value.length === 0) {
    console.log('✅ No tokens found - wallet is clean!');
    process.exit(0);
  }

  console.log(`Found ${tokenAccounts.value.length} token account(s)\n`);

  // Filter for non-zero balances
  const holdings = tokenAccounts.value.filter(account => {
    const balance = account.account.data.parsed.info.tokenAmount.uiAmount;
    return balance > 0;
  });

  if (holdings.length === 0) {
    console.log('✅ All token accounts have zero balance - wallet is clean!');
    process.exit(0);
  }

  console.log(`📊 Tokens with balance: ${holdings.length}\n`);
  console.log('═'.repeat(60));

  for (const account of holdings) {
    const info = account.account.data.parsed.info;
    const mint = info.mint;
    const balance = info.tokenAmount.uiAmount;
    const decimals = info.tokenAmount.decimals;

    console.log(`\n💎 Token: ${mint}`);
    console.log(`   Balance: ${balance}`);
    console.log(`   Decimals: ${decimals}`);

    // Sell via Jupiter
    console.log(`   🔄 Selling for SOL...`);

    try {
      // Get quote
      const quoteResponse = await fetch(
        `https://quote-api.jup.ag/v6/quote?` +
        `inputMint=${mint}` +
        `&outputMint=So11111111111111111111111111111111111111112` + // SOL
        `&amount=${info.tokenAmount.amount}` +
        `&slippageBps=500` // 5% slippage
      );

      if (!quoteResponse.ok) {
        console.log(`   ❌ No liquidity/route found - skipping`);
        continue;
      }

      const quoteData = await quoteResponse.json();
      const outAmount = quoteData.outAmount / 1e9; // Convert lamports to SOL

      console.log(`   📈 Expected: ${outAmount.toFixed(4)} SOL`);

      // Get swap transaction
      const swapResponse = await fetch('https://quote-api.jup.ag/v6/swap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${jupToken}`
        },
        body: JSON.stringify({
          quoteResponse: quoteData,
          userPublicKey: walletAddress.toString(),
          wrapAndUnwrapSol: true,
          dynamicComputeUnitLimit: true,
          prioritizationFeeLamports: 'auto'
        })
      });

      const swapData = await swapResponse.json();

      if (swapData.error) {
        console.log(`   ❌ Swap failed: ${swapData.error}`);
        continue;
      }

      // Deserialize and sign transaction
      const swapTransactionBuf = Buffer.from(swapData.swapTransaction, 'base64');
      const transaction = require('@solana/web3.js').VersionedTransaction.deserialize(swapTransactionBuf);
      transaction.sign([keypair]);

      // Send transaction
      const signature = await connection.sendRawTransaction(transaction.serialize(), {
        skipPreflight: true,
        maxRetries: 3
      });

      console.log(`   ✅ SOLD!`);
      console.log(`   📝 Signature: ${signature}`);
      console.log(`   🔗 https://solscan.io/tx/${signature}`);

      // Wait a bit between swaps
      await new Promise(resolve => setTimeout(resolve, 2000));

    } catch (error: any) {
      console.log(`   ❌ Error: ${error.message}`);
    }
  }

  console.log('\n' + '═'.repeat(60));
  console.log('\n✅ Sell operation complete!\n');

  // Final balance check
  const balance = await connection.getBalance(walletAddress);
  console.log(`💰 Final SOL balance: ${(balance / 1e9).toFixed(4)} SOL\n`);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
