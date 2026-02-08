/**
 * Neural Norse Pepes - Agent-Only Minting Script
 * 10K Viking Pepes on Solana - SHA-256 Proof-of-Work Mint
 * 
 * Price: 0.02 SOL + ~0.0035 SOL rent = ~0.024 SOL total per mint
 * Method: SHA-256 PoW (find nonce where hash starts with 0000)
 */

const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58');
const bip39 = require('bip39');
const { derivePath } = require('ed25519-hd-key');
const crypto = require('crypto');

const API_BASE = 'https://neural-norse.vercel.app/api';
const RPC_URL = process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com';

// Get keypair from seed phrase (Phantom/Solflare compatible)
function keypairFromSeedPhrase(seedPhrase, accountIndex = 0) {
    const seed = bip39.mnemonicToSeedSync(seedPhrase);
    const path = `m/44'/501'/${accountIndex}'/0'`;
    const derived = derivePath(path, seed.toString('hex'));
    return Keypair.fromSeed(derived.key);
}

// SHA-256 proof-of-work solver
function solveChallenge(challenge, wallet, difficulty = 4) {
    const target = '0'.repeat(difficulty); // e.g., "0000" for difficulty 4
    let nonce = 0;
    const startTime = Date.now();
    
    console.log(`Solving PoW puzzle (difficulty ${difficulty})...`);
    
    while (true) {
        const input = `${challenge}${wallet}${nonce}`;
        const hash = crypto.createHash('sha256').update(input).digest('hex');
        
        if (hash.startsWith(target)) {
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
            console.log(`Found solution in ${elapsed}s after ${nonce.toLocaleString()} iterations`);
            console.log(`Hash: ${hash}`);
            return nonce.toString();
        }
        
        nonce++;
        
        // Progress update every 100k iterations
        if (nonce % 100000 === 0) {
            console.log(`  ...${nonce.toLocaleString()} hashes computed`);
        }
    }
}

async function getChallenge(wallet) {
    const url = `${API_BASE}/challenge?wallet=${wallet}`;
    console.log(`Requesting challenge for wallet: ${wallet}`);
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(`Challenge failed: ${JSON.stringify(data)}`);
    }
    
    console.log(`Challenge received (difficulty: ${data.difficulty}, expires in ${data.expiresIn}s)`);
    return data;
}

async function requestMint(wallet, challenge, nonce) {
    console.log(`Submitting solution: nonce=${nonce}`);
    
    const response = await fetch(`${API_BASE}/mint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet, challenge, nonce })
    });
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(`Mint request failed: ${JSON.stringify(data)}`);
    }
    
    console.log(`Transaction received! Asset: ${data.asset}`);
    console.log(`Collection: ${data.collection.claimed}/${data.collection.total} claimed`);
    
    return data;
}

async function getCollectionStats() {
    const response = await fetch(`${API_BASE}/collection`);
    return await response.json();
}

async function mint(count = 1) {
    // Load wallet from seed phrase
    const seedPhrase = process.env.SEED_PHRASE;
    if (!seedPhrase) {
        throw new Error('SEED_PHRASE environment variable required');
    }
    
    const keypair = keypairFromSeedPhrase(seedPhrase);
    const walletAddress = keypair.publicKey.toBase58();
    console.log(`\n=== Neural Norse Minting Agent ===`);
    console.log(`Wallet: ${walletAddress}`);
    console.log(`Minting: ${count} NFT(s)`);
    console.log(`Cost: ~${(0.024 * count).toFixed(4)} SOL`);
    
    // Check collection stats first
    try {
        const stats = await getCollectionStats();
        console.log(`\nCollection Status: ${stats.claimed || '?'}/${stats.total || '?'} minted`);
        if (stats.remaining === 0) {
            console.log('Collection is sold out!');
            return;
        }
    } catch (e) {
        console.log('Could not fetch collection stats, proceeding anyway...');
    }
    
    const connection = new Connection(RPC_URL, 'confirmed');
    
    // Check balance
    const balance = await connection.getBalance(keypair.publicKey);
    const balanceSOL = balance / 1e9;
    console.log(`Balance: ${balanceSOL.toFixed(4)} SOL`);
    
    const requiredSOL = 0.024 * count;
    if (balanceSOL < requiredSOL) {
        console.log(`Insufficient balance! Need ~${requiredSOL.toFixed(4)} SOL, have ${balanceSOL.toFixed(4)} SOL`);
        return;
    }
    
    const results = [];
    
    for (let i = 0; i < count; i++) {
        console.log(`\n--- Mint ${i + 1}/${count} ---`);
        
        try {
            // Step 1: Get challenge
            const challengeData = await getChallenge(walletAddress);
            
            // Step 2: Solve SHA-256 puzzle
            const nonce = solveChallenge(
                challengeData.challenge, 
                walletAddress, 
                challengeData.difficulty
            );
            
            // Step 3: Request mint transaction
            const mintData = await requestMint(walletAddress, challengeData.challenge, nonce);
            
            // Step 4: Sign and submit transaction
            const txBuffer = Buffer.from(mintData.transaction, 'base64');
            const vtx = VersionedTransaction.deserialize(new Uint8Array(txBuffer));
            
            vtx.sign([keypair]);
            
            console.log('Submitting transaction to Solana...');
            const signature = await connection.sendRawTransaction(vtx.serialize(), {
                skipPreflight: true,
                maxRetries: 3
            });
            
            console.log(`Transaction submitted: ${signature}`);
            
            // Wait for confirmation
            const confirmation = await connection.confirmTransaction(signature, 'confirmed');
            
            if (confirmation.value.err) {
                console.log(`Transaction failed: ${JSON.stringify(confirmation.value.err)}`);
                results.push({ success: false, error: confirmation.value.err });
            } else {
                console.log(`SUCCESS! Minted Neural Norse NFT`);
                console.log(`Asset: ${mintData.asset}`);
                console.log(`TX: https://solscan.io/tx/${signature}`);
                results.push({ success: true, signature, asset: mintData.asset });
            }
            
            // Small delay between mints
            if (i < count - 1) {
                await new Promise(r => setTimeout(r, 1000));
            }
            
        } catch (error) {
            console.log(`Mint ${i + 1} failed: ${error.message}`);
            results.push({ success: false, error: error.message });
        }
    }
    
    // Summary
    console.log('\n=== Minting Complete ===');
    const successful = results.filter(r => r.success).length;
    console.log(`Successful: ${successful}/${count}`);
    
    return results;
}

// CLI entry point
if (require.main === module) {
    const count = parseInt(process.argv[2]) || 1;
    mint(count).catch(console.error);
}

module.exports = { mint, solveChallenge, keypairFromSeedPhrase };
