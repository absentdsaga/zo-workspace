import { Connection, Keypair, VersionedTransaction, LAMPORTS_PER_SOL } from "@solana/web3.js";
import bs58 from "bs58";

/**
 * WORKING TRADE EXECUTOR
 * Uses Jupiter Swap API v1 with x-api-key authentication
 * Tested and verified to work with Zo environment
 */

interface TradeParams {
  inputMint: string;
  outputMint: string;
  amount: number; // in lamports
  slippageBps?: number;
  strategy?: 'meme' | 'arbitrage' | 'perp' | 'volume';
}

interface TradeResult {
  success: boolean;
  signature?: string;
  error?: string;
  executionTime: number;
  inputAmount?: number;
  outputAmount?: number;
  priceImpact?: number;
}

class WorkingExecutor {
  private connection: Connection;
  private wallet: Keypair;
  private apiKey: string;
  private baseUrl = 'https://api.jup.ag';

  // Strategy-specific priority fees (from testing)
  private priorityFees = {
    meme: 1000,      // micro-lamports
    arbitrage: 1000,
    perp: 100,
    volume: 500,
    default: 1000
  };

  constructor(rpcUrl: string, privateKey: string, jupiterApiKey: string) {
    this.connection = new Connection(rpcUrl, {
      commitment: 'confirmed',
      confirmTransactionInitialTimeout: 60000
    });
    this.wallet = Keypair.fromSecretKey(bs58.decode(privateKey));
    this.apiKey = jupiterApiKey;

    console.log('🔧 Working Trade Executor initialized');
    console.log(`👛 Wallet: ${this.wallet.publicKey.toBase58()}`);
    console.log(`🔑 API Key: ${jupiterApiKey.substring(0, 8)}...${jupiterApiKey.substring(jupiterApiKey.length - 4)}`);
  }

  /**
   * Get quote from Jupiter
   */
  private async getQuote(params: TradeParams): Promise<any> {
    const url = `${this.baseUrl}/swap/v1/quote?` +
      `inputMint=${params.inputMint}&` +
      `outputMint=${params.outputMint}&` +
      `amount=${params.amount}&` +
      `slippageBps=${params.slippageBps || 300}`;

    const response = await fetch(url, {
      headers: {
        'x-api-key': this.apiKey,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Quote API error ${response.status}: ${errorText}`);
    }

    return await response.json();
  }

  /**
   * Get swap transaction from Jupiter
   */
  private async getSwapTransaction(quote: any, priorityFeeLamports: number): Promise<any> {
    const url = `${this.baseUrl}/swap/v1/swap`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'x-api-key': this.apiKey,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        quoteResponse: quote,
        userPublicKey: this.wallet.publicKey.toBase58(),
        wrapAndUnwrapSol: true,
        dynamicComputeUnitLimit: true,
        prioritizationFeeLamports: priorityFeeLamports
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Swap API error ${response.status}: ${errorText}`);
    }

    return await response.json();
  }

  /**
   * Execute trade
   */
  async executeTrade(params: TradeParams): Promise<TradeResult> {
    const startTime = Date.now();

    console.log(`\n🚀 Executing ${params.strategy || 'standard'} trade`);
    console.log(`   Input: ${(params.amount / LAMPORTS_PER_SOL).toFixed(6)} SOL`);
    console.log(`   Output: ${params.outputMint.substring(0, 8)}...`);

    try {
      // Step 1: Get quote
      console.log(`1️⃣  Getting quote...`);
      const quote = await this.getQuote(params);

      console.log(`✅ Quote received:`);
      console.log(`   In: ${quote.inAmount} lamports`);
      console.log(`   Out: ${quote.outAmount} lamports`);
      console.log(`   Price impact: ${quote.priceImpactPct}%`);
      console.log(`   Route: ${quote.routePlan[0].swapInfo.label}`);

      // Step 2: Get swap transaction
      console.log(`\n2️⃣  Getting swap transaction...`);
      const priorityFee = this.priorityFees[params.strategy || 'default'];
      const swapData = await this.getSwapTransaction(quote, priorityFee);

      console.log(`✅ Swap transaction received (${swapData.swapTransaction.length} bytes)`);

      // Step 3: Deserialize and sign
      console.log(`\n3️⃣  Signing transaction...`);
      const swapTransactionBuf = Buffer.from(swapData.swapTransaction, 'base64');
      const transaction = VersionedTransaction.deserialize(swapTransactionBuf);
      transaction.sign([this.wallet]);

      console.log(`✅ Transaction signed`);

      // Step 4: Send transaction
      console.log(`\n4️⃣  Broadcasting to network...`);
      const signature = await this.connection.sendRawTransaction(
        transaction.serialize(),
        {
          skipPreflight: false,
          maxRetries: 3
        }
      );

      console.log(`✅ Transaction sent: ${signature}`);

      // Step 5: Confirm transaction
      console.log(`\n5️⃣  Waiting for confirmation...`);
      const latestBlockhash = await this.connection.getLatestBlockhash();

      await this.connection.confirmTransaction({
        signature,
        blockhash: latestBlockhash.blockhash,
        lastValidBlockHeight: latestBlockhash.lastValidBlockHeight
      }, 'confirmed');

      const executionTime = Date.now() - startTime;

      console.log(`\n✅ TRADE COMPLETE in ${executionTime}ms`);
      console.log(`📝 Signature: ${signature}`);

      return {
        success: true,
        signature,
        executionTime,
        inputAmount: parseInt(quote.inAmount),
        outputAmount: parseInt(quote.outAmount),
        priceImpact: parseFloat(quote.priceImpactPct)
      };

    } catch (error: any) {
      const executionTime = Date.now() - startTime;

      console.log(`\n❌ Trade failed after ${executionTime}ms`);
      console.log(`   Error: ${error.message}`);

      return {
        success: false,
        error: error.message,
        executionTime
      };
    }
  }

  /**
   * Get wallet balance
   */
  async getBalance(): Promise<number> {
    const balance = await this.connection.getBalance(this.wallet.publicKey);
    return balance / LAMPORTS_PER_SOL;
  }

  /**
   * Pre-flight check
   */
  async preFlightCheck(): Promise<{
    ready: boolean;
    balance: number;
    issues: string[];
  }> {
    console.log('\n🔍 Running pre-flight check...\n');

    const issues: string[] = [];

    // Check balance
    const balance = await this.getBalance();
    console.log(`💰 Balance: ${balance.toFixed(4)} SOL`);

    if (balance < 0.01) {
      issues.push('Insufficient balance (<0.01 SOL)');
    }

    // Test Jupiter API
    console.log('🔬 Testing Jupiter API...');
    try {
      const testQuote = await this.getQuote({
        inputMint: 'So11111111111111111111111111111111111111112',
        outputMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        amount: 1000000,
        slippageBps: 50
      });

      console.log(`✅ Jupiter API working (quote: ${testQuote.outAmount} lamports)`);
    } catch (error: any) {
      issues.push(`Jupiter API error: ${error.message}`);
    }

    // Test RPC
    console.log('🔬 Testing RPC connection...');
    try {
      await this.connection.getLatestBlockhash();
      console.log('✅ RPC connection working');
    } catch (error: any) {
      issues.push(`RPC error: ${error.message}`);
    }

    console.log('\n' + '='.repeat(60));
    if (issues.length === 0) {
      console.log('✅ ALL SYSTEMS READY FOR TRADING');
    } else {
      console.log('⚠️  ISSUES DETECTED:');
      for (const issue of issues) {
        console.log(`   • ${issue}`);
      }
    }
    console.log('='.repeat(60) + '\n');

    return {
      ready: issues.length === 0,
      balance,
      issues
    };
  }
}

// CLI usage
async function main() {
  const privateKey = process.env.SOLANA_PRIVATE_KEY;
  const jupiterKey = process.env.JUP_TOKEN;
  const rpcUrl = process.env.HELIUS_RPC_URL
    ? `https://mainnet.helius-rpc.com/?api-key=${process.env.HELIUS_RPC_URL}`
    : 'https://api.mainnet-beta.solana.com';

  if (!privateKey) {
    console.error('❌ SOLANA_PRIVATE_KEY not set');
    process.exit(1);
  }

  if (!jupiterKey) {
    console.error('❌ JUP_TOKEN not set');
    process.exit(1);
  }

  const executor = new WorkingExecutor(rpcUrl, privateKey, jupiterKey);

  // Run pre-flight check
  const check = await executor.preFlightCheck();

  if (!check.ready) {
    console.log('❌ Not ready for trading\n');
    process.exit(1);
  }

  // Check if user wants to test trade
  const shouldTest = process.argv.includes('--test');

  if (shouldTest) {
    console.log('⚠️  TEST TRADE MODE');
    console.log('⚠️  This will execute a REAL trade: 0.005 SOL → USDC');
    console.log('⚠️  Cost: ~$0.60 + fees\n');

    const SOL_MINT = 'So11111111111111111111111111111111111111112';
    const USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';

    const result = await executor.executeTrade({
      inputMint: SOL_MINT,
      outputMint: USDC_MINT,
      amount: 5000000, // 0.005 SOL
      slippageBps: 100, // 1% slippage
      strategy: 'meme'
    });

    if (result.success) {
      console.log('\n🎉 SUCCESS! System is fully operational!');
      console.log('🎉 Ready to begin live trading strategy!');
      console.log(`🎉 Execution speed: ${result.executionTime}ms`);
    } else {
      console.log('\n❌ Test trade failed');
      console.log(`❌ Error: ${result.error}`);
    }
  } else {
    console.log('ℹ️  Run with --test flag to execute a small test trade');
    console.log('ℹ️  Example: bun run working-executor.ts --test\n');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { WorkingExecutor, TradeParams, TradeResult };
