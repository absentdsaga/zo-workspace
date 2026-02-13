#!/usr/bin/env bun

import { Connection, Keypair, LAMPORTS_PER_SOL } from '@solana/web3.js';

async function main() {
  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const heliusKey = process.env.HELIUS_RPC_URL;

  if (!privateKey || !heliusKey) {
    console.error('❌ Missing environment variables');
    process.exit(1);
  }

  const rpcUrl = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;
  const connection = new Connection(rpcUrl, 'confirmed');

  const keypair = Keypair.fromSecretKey(
    new Uint8Array(JSON.parse(privateKey))
  );

  console.log(`\n💰 Wallet: ${keypair.publicKey.toString()}\n`);

  const balance = await connection.getBalance(keypair.publicKey);
  const sol = balance / LAMPORTS_PER_SOL;
  const usd = sol * 119;

  console.log(`Balance: ${sol.toFixed(4)} SOL (~$${usd.toFixed(2)} USD)`);
  console.log(`Circuit breaker: 0.1 SOL`);
  console.log(`Distance to death: ${(sol - 0.1).toFixed(4)} SOL (${Math.floor((sol - 0.1) / 0.02)} trades at 5%)\n`);
}

main();
