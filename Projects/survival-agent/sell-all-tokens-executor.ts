#!/usr/bin/env bun
/**
 * Sell all token holdings using OptimizedExecutor
 */

import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID } from '@solana/spl-token';
import bs58 from 'bs58';
import { OptimizedExecutor } from './core/optimized-executor';

async function main() {
  console.log('🔥 SELLING ALL MEME TOKENS\n');

  // Load credentials
  const privateKeyBase58 = process.env.SOLANA_PRIVATE_KEY;
  const heliusKey = process.env.HELIUS_RPC_URL || process.env.HELIUS_API_KEY;
  const jupToken = process.env.JUP_TOKEN;

  if (!privateKeyBase58 || !heliusKey || !jupToken) {
    console.error('❌ Missing credentials');
    process.exit(1);
  }

  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;
  const connection = new Connection(rpcUrl, 'confirmed');
  const keypair = Keypair.fromSecretKey(bs58.decode(privateKeyBase58));
  const walletAddress = keypair.publicKey;

  console.log(`💼 Wallet: ${walletAddress.toString()}\n`);

  // Initialize executor
  const executor = new OptimizedExecutor(rpcUrl, privateKeyBase58, jupToken, heliusKey);

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

  let successCount = 0;
  let failCount = 0;
  let totalSolReceived = 0;

  for (const account of holdings) {
    const info = account.account.data.parsed.info;
    const mint = info.mint;
    const balance = info.tokenAmount.uiAmount;
    const amountRaw = info.tokenAmount.amount;

    console.log(`\n💎 Token: ${mint}`);
    console.log(`   Balance: ${balance}`);
    console.log(`   🔄 Selling for SOL...`);

    try {
      // Use executor to sell
      const result = await executor.executeTrade({
        inputMint: mint,
        outputMint: 'So11111111111111111111111111111111111111112', // SOL
        amount: parseInt(amountRaw),
        slippageBps: 1000 // 10% slippage for illiquid meme coins
      });

      if (result.success) {
        const solReceived = result.outputAmount! / 1e9;
        totalSolReceived += solReceived;
        successCount++;

        console.log(`   ✅ SOLD!`);
        console.log(`   💰 Received: ${solReceived.toFixed(4)} SOL`);
        console.log(`   📝 Signature: ${result.signature}`);
        console.log(`   🔗 https://solscan.io/tx/${result.signature}`);
      } else {
        failCount++;
        console.log(`   ❌ Failed: ${result.error}`);
      }

      // Wait between swaps
      await new Promise(resolve => setTimeout(resolve, 2000));

    } catch (error: any) {
      failCount++;
      console.log(`   ❌ Error: ${error.message}`);
    }
  }

  console.log('\n' + '═'.repeat(60));
  console.log('\n📊 SELL SUMMARY:');
  console.log(`   ✅ Successful: ${successCount}`);
  console.log(`   ❌ Failed: ${failCount}`);
  console.log(`   💰 Total SOL received: ${totalSolReceived.toFixed(4)} SOL\n`);

  // Final balance check
  const balance = await connection.getBalance(walletAddress);
  console.log(`💰 Final SOL balance: ${(balance / 1e9).toFixed(4)} SOL\n`);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
