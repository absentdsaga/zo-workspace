/**
 * MAINNET E2E TEST - Nominal cost (~0.001 SOL)
 *
 * Tests the full execution pipeline with real transactions:
 *   1. Pre-flight check (wallet, RPC, Jupiter)
 *   2. Buy 0.001 SOL of USDC (most liquid token = minimal slippage)
 *   3. Immediately sell back to SOL
 *   4. Report tx signatures and net cost
 *
 * Expected cost: ~0.001 SOL swap amount + ~0.0001 SOL fees = ~$0.20 total
 * Run with: bun testing/test-mainnet-e2e.ts
 */

import { Connection, Keypair, LAMPORTS_PER_SOL, VersionedTransaction, type SignatureStatus } from '@solana/web3.js';
import bs58 from 'bs58';

// USDC on Solana - most liquid, tightest spreads, minimal loss on round-trip
const USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';
const SOL_MINT = 'So11111111111111111111111111111111111111112';
const TEST_AMOUNT_LAMPORTS = 1_000_000; // 0.001 SOL
const SLIPPAGE_BPS = 100; // 1% - tight since USDC is liquid

async function getQuote(inputMint: string, outputMint: string, amount: number, jupToken: string) {
  const url = `https://api.jup.ag/swap/v1/quote?inputMint=${inputMint}&outputMint=${outputMint}&amount=${amount}&slippageBps=${SLIPPAGE_BPS}`;
  const res = await fetch(url, {
    headers: { 'x-api-key': jupToken }
  });
  if (!res.ok) throw new Error(`Quote failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function getSwapTx(quote: any, walletPubkey: string, jupToken: string) {
  const res = await fetch('https://api.jup.ag/swap/v1/swap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': jupToken },
    body: JSON.stringify({
      quoteResponse: quote,
      userPublicKey: walletPubkey,
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: 5000, // fixed small fee for test
    })
  });
  if (!res.ok) throw new Error(`Swap tx failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function pollConfirm(connection: Connection, sig: string, timeoutMs = 60000): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    await new Promise(r => setTimeout(r, 2000));
    const status = await connection.getSignatureStatus(sig);
    const conf = status?.value?.confirmationStatus;
    if (conf === 'confirmed' || conf === 'finalized') return;
    if (status?.value?.err) throw new Error(`Tx failed on-chain: ${JSON.stringify(status.value.err)}`);
  }
  throw new Error(`Confirmation timeout after ${timeoutMs}ms`);
}

async function main() {
  console.log('🧪 MAINNET E2E TEST\n');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('Testing full pipeline: RPC → Jupiter → Sign → Send → Confirm');
  console.log(`Test amount: 0.001 SOL (~$0.18) → USDC → SOL back`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupToken = process.env.JUP_TOKEN || '';
  const heliusKey = process.env.HELIUS_RPC_URL;

  if (!privateKey || !heliusKey) {
    console.error('❌ Need SOLANA_PRIVATE_KEY and HELIUS_RPC_URL');
    process.exit(1);
  }

  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;
  const connection = new Connection(rpcUrl, { commitment: 'confirmed' });
  const wallet = Keypair.fromSecretKey(bs58.decode(privateKey));
  const pubkey = wallet.publicKey.toBase58();

  // Step 1: Pre-flight
  console.log('1️⃣  Pre-flight check...');
  const balance = await connection.getBalance(wallet.publicKey);
  const solBalance = balance / LAMPORTS_PER_SOL;
  console.log(`   Wallet: ${pubkey}`);
  console.log(`   Balance: ${solBalance.toFixed(6)} SOL`);

  if (solBalance < 0.005) {
    console.error('❌ Need at least 0.005 SOL for test');
    process.exit(1);
  }
  console.log('   ✅ Pre-flight passed\n');

  // Step 2: Buy USDC
  console.log('2️⃣  BUY: 0.001 SOL → USDC...');
  const buyQuote = await getQuote(SOL_MINT, USDC_MINT, TEST_AMOUNT_LAMPORTS, jupToken);
  const usdcOut = parseInt(buyQuote.outAmount) / 1_000_000; // USDC has 6 decimals
  console.log(`   Quote: 0.001 SOL → ${usdcOut.toFixed(4)} USDC (impact: ${buyQuote.priceImpactPct}%)`);

  const buySwapData = await getSwapTx(buyQuote, pubkey, jupToken);
  const buyTxBuf = Buffer.from(buySwapData.swapTransaction, 'base64');
  const buyTx = VersionedTransaction.deserialize(buyTxBuf);
  buyTx.sign([wallet]);

  const buySig = await connection.sendRawTransaction(buyTx.serialize(), { skipPreflight: true, maxRetries: 5 });
  console.log(`   Sent: ${buySig}`);
  console.log(`   Confirming...`);
  await pollConfirm(connection, buySig);
  console.log(`   ✅ BUY confirmed: https://solscan.io/tx/${buySig}\n`);

  // Brief pause to let token account settle
  await new Promise(r => setTimeout(r, 2000));

  // Step 3: Sell USDC back to SOL
  console.log('3️⃣  SELL: USDC → SOL back...');
  const usdcAmountRaw = buyQuote.outAmount; // sell exactly what we received
  const sellQuote = await getQuote(USDC_MINT, SOL_MINT, usdcAmountRaw, jupToken);
  const solBack = parseInt(sellQuote.outAmount) / LAMPORTS_PER_SOL;
  console.log(`   Quote: ${usdcOut.toFixed(4)} USDC → ${solBack.toFixed(6)} SOL`);

  const sellSwapData = await getSwapTx(sellQuote, pubkey, jupToken);
  const sellTxBuf = Buffer.from(sellSwapData.swapTransaction, 'base64');
  const sellTx = VersionedTransaction.deserialize(sellTxBuf);
  sellTx.sign([wallet]);

  const sellSig = await connection.sendRawTransaction(sellTx.serialize(), { skipPreflight: true, maxRetries: 5 });
  console.log(`   Sent: ${sellSig}`);
  console.log(`   Confirming...`);
  await pollConfirm(connection, sellSig);
  console.log(`   ✅ SELL confirmed: https://solscan.io/tx/${sellSig}\n`);

  // Step 4: Report
  const newBalance = await connection.getBalance(wallet.publicKey);
  const newSolBalance = newBalance / LAMPORTS_PER_SOL;
  const netCost = solBalance - newSolBalance;

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('✅ E2E TEST COMPLETE');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`Buy tx:  https://solscan.io/tx/${buySig}`);
  console.log(`Sell tx: https://solscan.io/tx/${sellSig}`);
  console.log(`Balance before: ${solBalance.toFixed(6)} SOL`);
  console.log(`Balance after:  ${newSolBalance.toFixed(6)} SOL`);
  console.log(`Net cost:       ${netCost.toFixed(6)} SOL (~$${(netCost * 180).toFixed(3)})`);
  console.log('');
  console.log('Pipeline verified: RPC ✅ Jupiter ✅ Sign ✅ Send ✅ Confirm ✅');
}

main().catch(e => {
  console.error('❌ Test failed:', e.message);
  process.exit(1);
});
