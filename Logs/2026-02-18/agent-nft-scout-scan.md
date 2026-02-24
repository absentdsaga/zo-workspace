# Agent-Only NFT Mint Scout Report
**Scan Time:** 2026-02-18 12:20:00 UTC (07:20:00 EST)

## 🔥 LIVE NOW - Agent-Only NFT Mints Found

### 1. Neural Norse ⚔️
- **URL:** https://neural-norse.vercel.app
- **Chain:** Solana Mainnet
- **Supply:** 10,000 NFTs
- **Price:** 0.02 SOL (~$1.70) + ~0.004 SOL rent
- **Status:** LIVE NOW - Minting in progress
- **Method:** SHA-256 proof-of-work challenge (agents only)
- **Standard:** Metaplex Core
- **Description:** First 10K Pepe collection exclusively for AI agents. Norse myth theme with "Valhalla" narrative. Agents must solve a SHA-256 puzzle to mint. No browser UI - pure API-based minting.

**How it works:**
1. Agent calls `GET /api/challenge?wallet=YOUR_WALLET`
2. Receives HMAC challenge and difficulty target
3. Finds nonce where `SHA256(challenge + wallet + nonce)` starts with `0000` (~65K iterations)
4. Submits to `POST /api/mint` to get partially-signed Candy Machine transaction
5. Signs and submits to Solana

**Twitter:** @neuralnorse
**Collection:** https://solscan.io/collection/BTeNHYBTnKU5H8MDFieDPXibbNFPda4FYVN8pfeyx485

---

### 2. Claws 🦞
- **URL:** https://clawsnft.com
- **Chain:** Solana Mainnet
- **Supply:** 4,200 NFTs
- **Price:** FREE (need ~0.025 SOL for transaction fees)
- **Status:** LIVE NOW - **0/4,200 minted** (just launched!)
- **Method:** Moltbook identity verification (agents only)
- **Standard:** Metaplex Candy Machine v3 with thirdPartySigner guard
- **Description:** First PFP collection for Moltbook residents. Agents must verify through Moltbook identity system to mint.

**How it works:**
1. Agent reads skill.md from `https://clawsnft.com/skill.md`
2. Generates Moltbook identity token
3. Calls mint endpoint with wallet address
4. Receives partially-signed transaction
5. Countersigns and submits to Solana

**Candy Machine:** `3shVtfQzi1jwXP5gsVer6DVSxNDazTbe4ad3msLbCKwZ`
**Collection Mint:** `C66iWj3kQu65wZJkoexcP8nJZHwpuejPY9ynCF7V3nbf`

---

## Other Notable Agent-Only Projects (Not NFT Mints)

### SPOT Protocol
- **URL:** https://mintspotcoin.com
- **Type:** Token (not NFT)
- **Chain:** Ethereum Sepolia Testnet
- **Status:** Live
- **Description:** AI agents prove intelligence through 5-round challenge to mint SPOT tokens. Agent-first protocol.

---

## SMS Delivery Status
❌ **FAILED** - User has not responded to recent SMS messages. SMS delivery blocked by system.

## Next Scan
Scheduled for 10 minutes from now.
