/**
 * Claws NFT Minting Agent
 * Agent-only free mint on Solana
 * 
 * Supports both private key and seed phrase
 */

const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58');
const bip39 = require('bip39');
const { derivePath } = require('ed25519-hd-key');

// Configuration
const API_BASE = 'https://clawsnft.com/api';
const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';

// Get keypair from seed phrase
function keypairFromSeedPhrase(seedPhrase, accountIndex = 0) {
    const seed = bip39.mnemonicToSeedSync(seedPhrase);
    const path = `m/44'/501'/${accountIndex}'/0'`; // Solana derivation path
    const derived = derivePath(path, seed.toString('hex'));
    return Keypair.fromSeed(derived.key);
}

// Get keypair from private key (base58)
function keypairFromPrivateKey(privateKeyBase58) {
    const secretKey = bs58.decode(privateKeyBase58);
    return Keypair.fromSecretKey(secretKey);
}

// Get keypair from env
function getKeypair() {
    const seedPhrase = process.env.SEED_PHRASE;
    const privateKey = process.env.SOLANA_PRIVATE_KEY;
    
    if (seedPhrase) {
        console.log('🔑 Using seed phrase...');
        const kp = keypairFromSeedPhrase(seedPhrase);
        console.log(`   Wallet: ${kp.publicKey.toBase58()}`);
        return kp;
    } else if (privateKey) {
        console.log('🔑 Using private key...');
        const kp = keypairFromPrivateKey(privateKey);
        console.log(`   Wallet: ${kp.publicKey.toBase58()}`);
        return kp;
    }
    
    return null;
}

async function getChallenge(walletAddress) {
    console.log('🎯 Requesting challenge...');
    
    const response = await fetch(`${API_BASE}/challenge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletAddress })
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Challenge request failed: ${response.status} - ${error}`);
    }
    
    const data = await response.json();
    console.log(`📝 Challenge: "${data.challenge}"`);
    
    return data;
}

function solveChallenge(challenge) {
    console.log('🧮 Solving challenge...');
    
    // Most challenges are math expressions
    const mathMatch = challenge.match(/What is (.+)\?/i);
    
    if (mathMatch) {
        const expression = mathMatch[1]
            .replace(/×/g, '*')
            .replace(/÷/g, '/')
            .replace(/[^\d\+\-\*\/\.\(\)\s]/g, '');
        
        try {
            const answer = Function('"use strict"; return (' + expression + ')')();
            console.log(`✅ Answer: ${answer}`);
            return String(Math.round(answer));
        } catch (e) {
            console.error('Failed to evaluate:', expression, e);
        }
    }
    
    console.log('⚠️  Non-math challenge, may need manual solving');
    return null;
}

async function requestMint(walletAddress, challengeId, answer) {
    console.log('🚀 Requesting mint transaction...');
    
    const response = await fetch(`${API_BASE}/mint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletAddress, challengeId, answer })
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Mint request failed: ${response.status} - ${error}`);
    }
    
    const data = await response.json();
    console.log(`🎨 NFT Mint: ${data.nftMint}`);
    
    return data;
}

async function signAndExecute(transactionBase64, keypair) {
    console.log('✍️  Signing transaction...');
    
    const txBuffer = Buffer.from(transactionBase64, 'base64');
    const tx = VersionedTransaction.deserialize(txBuffer);
    
    tx.sign([keypair]);
    
    const signedTxBase64 = Buffer.from(tx.serialize()).toString('base64');
    
    console.log('📤 Submitting to Solana...');
    
    const response = await fetch(`${API_BASE}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transaction: signedTxBase64 })
    });
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Execute failed: ${response.status} - ${error}`);
    }
    
    const data = await response.json();
    console.log(`✅ SUCCESS! TX: ${data.signature}`);
    console.log(`🔗 https://solscan.io/tx/${data.signature}`);
    
    return data;
}

async function mint(count = 1) {
    console.log('\n' + '='.repeat(50));
    console.log('🦀 CLAWS NFT MINTING AGENT');
    console.log('='.repeat(50) + '\n');
    
    const keypair = getKeypair();
    if (!keypair) {
        console.log('⚠️  NO CREDENTIALS PROVIDED\n');
        console.log('Use one of these:');
        console.log('  SEED_PHRASE="word1 word2 ... word12" node claws-mint.js mint');
        console.log('  SOLANA_PRIVATE_KEY="base58key" node claws-mint.js mint');
        return;
    }
    
    const walletAddress = keypair.publicKey.toBase58();
    console.log(`Minting ${count} NFT(s)...\n`);
    
    const results = [];
    
    for (let i = 0; i < count; i++) {
        console.log(`\n--- Mint ${i + 1}/${count} ---\n`);
        
        try {
            const { challengeId, challenge } = await getChallenge(walletAddress);
            const answer = solveChallenge(challenge);
            
            if (!answer) {
                console.log('❌ Could not solve challenge');
                continue;
            }
            
            const { transaction, nftMint } = await requestMint(walletAddress, challengeId, answer);
            const { signature } = await signAndExecute(transaction, keypair);
            
            results.push({ nftMint, signature, success: true });
            
            if (i < count - 1) {
                console.log('\n⏳ Waiting 2s...');
                await new Promise(r => setTimeout(r, 2000));
            }
            
        } catch (error) {
            console.error(`❌ Failed:`, error.message);
            results.push({ success: false, error: error.message });
        }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 RESULTS');
    console.log('='.repeat(50));
    const success = results.filter(r => r.success).length;
    console.log(`✅ ${success}/${count} minted successfully`);
    results.forEach((r, i) => {
        if (r.success) {
            console.log(`   ${i + 1}. ${r.nftMint}`);
        }
    });
    
    return results;
}

async function checkStatus() {
    console.log('📊 Checking Claws NFT status...\n');
    
    try {
        const response = await fetch(`${API_BASE}/challenge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ walletAddress: 'A5NND3sjKHV5MK7RHqthLoBSEB4kkCv3xHroNQWoBxf6' })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Mint is LIVE!');
            console.log(`   Challenge: "${data.challenge}"`);
        } else {
            console.log(`⚠️  Status: ${response.status}`);
            console.log(`   ${await response.text()}`);
        }
    } catch (e) {
        console.log('❌ API unreachable:', e.message);
    }
}

// CLI
const args = process.argv.slice(2);
const command = args[0] || 'status';

if (command === 'mint') {
    mint(parseInt(args[1]) || 1);
} else if (command === 'status') {
    checkStatus();
} else {
    console.log('🦀 Claws NFT Minter\n');
    console.log('Commands:');
    console.log('  node claws-mint.js status');
    console.log('  node claws-mint.js mint [count]\n');
    console.log('Auth (pick one):');
    console.log('  SEED_PHRASE="your 12 words"');
    console.log('  SOLANA_PRIVATE_KEY="base58key"');
}
