---
name: nft-scanner
description: Scan and analyze Solana NFT collections - check mint status, holder distribution, whale concentration, and wallet clustering. Mint NFTs with proof-of-work challenges.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  version: 1.0.0
---

# NFT Scanner Skill

Analyze Solana NFT collections for mint progress, holder distribution, and potential whale/clustering risks. Also supports automated minting for PoW-based collections.

## Features

- **Collection Stats**: Check total supply, minted count, remaining supply
- **Holder Analysis**: Analyze unique holders, distribution patterns, whale concentration
- **Wallet Clustering Detection**: Identify potentially connected wallets via Bubblemaps integration
- **Automated Minting**: Mint NFTs with SHA-256 proof-of-work solver

## Usage

### Check Collection Stats

```bash
node scripts/scanner.js stats <collection-name>
```

Example:
```bash
node scripts/scanner.js stats neural-norse
```

### Analyze Holders

```bash
node scripts/scanner.js holders <collection-name>
```

### Check for Wallet Clustering

```bash
node scripts/scanner.js clustering <candy-machine-address>
```

### Mint NFTs (Neural Norse)

```bash
SEED_PHRASE="your seed phrase" node neural-norse-mint.js <count>
```

## Supported Collections

- **Neural Norse**: 10K Pepe collection with PoW minting
- **CLAWS**: Custom minting script included

## Scripts

- `scripts/scanner.js` - Main scanner tool for analyzing collections
- `neural-norse-mint.js` - Automated minting for Neural Norse
- `claws-mint.js` - Automated minting for CLAWS

## Configuration

Set `SOLANA_RPC` environment variable to use a custom RPC endpoint (defaults to mainnet-beta).

For minting, set `SEED_PHRASE` with your wallet's seed phrase.

## Dependencies

Install with:
```bash
npm install
```

Required packages:
- `@solana/web3.js` - Solana blockchain interaction
- `bip39` - Seed phrase handling
- `bs58` - Base58 encoding
- `ed25519-hd-key` - HD key derivation
