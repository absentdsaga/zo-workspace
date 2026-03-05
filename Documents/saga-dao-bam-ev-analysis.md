# Saga DAO — BAM Program Deep EV Analysis
**Date:** March 5, 2026 | **SOL Price:** ~$85 | **Current Epoch:** 934

**Sources:** Trillium API (epoch 934), JIP-31 Forum Post, JIP-28 Forum Post, Jito Kobe API, on-chain data.

---

## 1. Current Saga DAO Validator State (Verified On-Chain — Epoch 934)

| Metric | Value | Source |
|---|---|---|
| Identity | `SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ` | Trillium API |
| Vote Account | `sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw` | Trillium API |
| Active Stake | **79,361 SOL** | Trillium API epoch 934 |
| Validator Commission | **5%** | Trillium API |
| Jito MEV Commission | **10% (1000 bps)** | Trillium API |
| Priority Fee Commission | **100% (10000 bps)** | Trillium API |
| Client | **Jito_BAM (6)** v3.1.8 | Trillium API |
| Skip Rate | **0.00%** | Excellent |
| IBRL Score | **98.23** | Top tier |
| Leader Slots (epoch 934) | **80** | Trillium API |
| Blocks Produced | **80** (0 missed) | Trillium API |
| Location | Ashburn, Virginia (ASN 396356 / Latitude.sh) | Trillium API |
| SFDP State | **Approved** (onboarding epoch 684) | Trillium API |
| Superminority | **No** | Trillium API |
| Jito Blacklisted | **No** | Trillium API |
| Stake Pools | FOUNDATION (37.6K), AERO (9.4K), MARINADE (9.5K), DYNOSOL (7.8K), DZ (4.9K), VAULT (4.6K), JPOOL (2.7K), others | Trillium API |

---

## 2. CRITICAL FINDING: BAM Node Connection Failure

**From Trillium API (verified March 5, 2026):**

| Field | Value | Meaning |
|---|---|---|
| `client_type` | `"Jito_BAM (6)"` | BAM client software IS installed and running |
| `is_bam` | **`false`** | BAM compliance check is FAILING |
| `bam_node_connection` | **`null`** | No BAM node connection detected |
| `jip31` | **`false`** | NOT eligible for JIP-31 subsidies |
| `jip28` | **`false`** | NOT eligible for JIP-28 delegation |
| `jip31_ineligible_reason` | `null` | No specific reason given |
| `jip31_claim_amount` | `null` | No rewards accrued |
| `jip31_claimed` | `null` | Never claimed |

### What This Means:

**Saga DAO is running the BAM client software (`Jito_BAM v3.1.8`) but is NOT passing the BAM compliance verification.** The BAM system requires validators to not just install the software but to:

1. **Establish a BAM node connection** — the validator must connect to the Jito Block Engine's BAM endpoint and maintain an active session
2. **Execute bundles in the correct order** — BAM bundles must be included in blocks in the specified execution order
3. **Provide correct feedback** — the validator must report back bundle execution results
4. **Maintain this for 3+ consecutive epochs** — the warmup period requires sustained compliance

The `bam_node_connection: null` field is the smoking gun — the BAM software is running but has **never established a connection** to the Jito BAM infrastructure, or the connection dropped and was never re-established.

### Immediate Action Required:
This is not a commission or eligibility issue — **it's a technical configuration issue.** The validator operator needs to:
1. Check BAM node connection configuration in the validator's Jito config
2. Verify the BAM endpoint URL and authentication
3. Check validator logs for BAM connection errors
4. Ensure the BAM relay/block engine connection is active
5. Once fixed, wait 3 consecutive epochs (~6 days) for the warmup requirement

---

## 3. Two Separate BAM Programs (Verified from JIP Forum Posts)

### Program A: JIP-28 — BAM Adoption Acceleration (Stake Delegation)
- **What it is:** A portion of JitoSOL directed stake gets delegated to qualifying BAM validators
- **Eligibility (ALL required):**
  - 0% inflation commission
  - ≤10% Jito MEV commission
  - Outside superminority
  - Running BAM with active compliance for 3+ epochs
  - Must also meet JIP-27 base criteria
- **Current BAM stakeweight:** ~27.83% (117.5M SOL out of ~422M total) — Epoch 934
- **Tiered delegation:** Based on BAM adoption milestones (15%, 20%, 25%, 30%, etc. of directed pool)
- **Source:** forum.jito.network JIP-28

### Program B: JIP-31 — BAM Early Adopter Subsidy (Direct Payments)
- **What it is:** 100% of Jito DAO protocol revenue redistributed to BAM validators epoch-by-epoch
- **Eligibility (ALL required):**
  - BAM client running with **active compliance** (`is_bam: true`)
  - ≥50K SOL active stake
  - 3 consecutive epochs of BAM compliance
  - Not blacklisted
  - **NO commission requirements** (0% NOT needed)
- **Duration:** Epoch 911 (Jan 16, 2026) → Epoch 1042 (~Sep 30, 2026)
  - Wind-down starts first week of July 2026, linear 100%→0% over ~12 weeks
- **Effective stake formula:** Linear up to 1.5M SOL, 0.5x from 1.5M–4.5M, capped at 3M effective
- **Claim window:** 10 epochs — unclaimed rewards reflow to subsequent pools
- **Current pool (epoch 934):** ~481 SOL/epoch from recency-weighted avg $145,226/week protocol revenue
- **306 eligible validators** sharing ~96.3M total effective stake
- **Source:** forum.jito.network JIP-31

---

## 4. Saga DAO's ACTUAL Eligibility Status

| Criteria | JIP-28 (Delegation) | JIP-31 (Subsidy) |
|---|---|---|
| Running BAM client software | ✅ (Jito_BAM v3.1.8) | ✅ (Jito_BAM v3.1.8) |
| **BAM compliance active (`is_bam`)** | **❌ (false)** | **❌ (false)** |
| **BAM node connection** | **❌ (null)** | **❌ (null)** |
| ≥50K SOL stake | ✅ (79.4K) | ✅ (79.4K) |
| Not blacklisted | ✅ | ✅ |
| Outside superminority | ✅ | ✅ |
| Voting rate | ✅ (98.23 IBRL) | N/A |
| 0% validator commission | ❌ (currently 5%) | **NOT REQUIRED** |
| ≤10% MEV commission | ✅ (exactly 10%) | **NOT REQUIRED** |
| 3 consecutive BAM epochs | **❌ (never connected)** | **❌ (never connected)** |

### Bottom Line:
**Saga DAO is currently ineligible for BOTH programs** — not because of commission settings, but because the BAM node connection has never been properly established. The validator runs the BAM client software but fails the actual BAM compliance check.

---

## 5. Revenue Math — What You Currently Earn (Verified from Trillium)

### At Current 5% Commission + 10% MEV Commission:

**Inflation Commission Revenue:**
- Stake: 79,361 SOL
- Delegator inflation APY: 5.80% (Trillium `delegator_compound_inflation_apy`)
- Total inflation rewards generated: 79,361 × 0.058 = ~4,603 SOL/year
- Your 5% cut: ~230 SOL/year (~$19,550)
- Trillium confirms: validator inflation reward = 1.27 SOL per epoch → ~232 SOL/year ✓

**Block Rewards (MEV + Priority Fees + Signature Fees):**
- Per block: avg 0.0367 SOL (Trillium `avg_rewards_per_block`)
- 80 blocks/epoch × 183 epochs = 14,640 blocks/year
- Total block rewards: ~537 SOL/year flowing through validator
- Validator block rewards APY: 0.685% (Trillium `total_block_rewards_apy`)
- MEV commission (10%): ~2.83 SOL/epoch → ~0.35 SOL/epoch to validator → ~64 SOL/year
- Priority fee commission (100%): **2.64 SOL/epoch** → ~483 SOL/year ← THIS IS SIGNIFICANT

**Corrected Total Commission Revenue:**
| Revenue Stream | SOL/year | USD/year |
|---|---|---|
| 5% inflation commission | ~232 | ~$19,720 |
| 10% MEV tip commission | ~5.2 | ~$442 |
| Priority fee commission (100%) | ~483 | ~$41,055 |
| Signature fees | ~54 | ~$4,590 |
| **Total** | **~774** | **~$65,807** |

**Important correction from original analysis:** The original estimate of ~255 SOL/year was significantly undercounting because it missed priority fee revenue. Trillium data shows `validator_total_apy: 0.989%` which on 79.4K SOL = ~785 SOL/year, confirming ~774 SOL/year.

---

## 6. Revenue Math — What You'd GAIN from BAM Programs (IF Eligible)

### JIP-31 Subsidy (Requires BAM Connection Fix, NOT Commission Change):

**Your effective stake:** 79,361 SOL (linear, below 1.5M threshold)
**Total effective stake in pool:** ~96.3M SOL (epoch 934)
**Your share:** 79,361 / 96,300,000 = **0.0824%**
**Per-epoch subsidy pool:** ~481 SOL
**Your per-epoch reward:** 481 × 0.000824 = **~0.396 SOL/epoch** (~$33.70)
**Per year (183 epochs):** ~72.5 SOL (~$6,163)
**Remaining program (est. ~107 epochs to Sep 2026):** ~42 SOL (~$3,570)

Note: Some validators aren't claiming within the 10-epoch window; unclaimed rewards reflow to remaining claimants, potentially increasing actual yield by 10-30%.

### JIP-28 Delegation (Requires 0% Commission + BAM Connection Fix):

**Conservative estimate (same methodology as before):**
- JitoSOL directed pool for BAM validators: ~1.2M SOL
- Pro-rata at 79K out of ~117M total BAM stake: 0.068%
- Delegation received: ~816 SOL additional
- Impact: ~0.5 extra leader slots/epoch → negligible MEV income (~0.5 SOL/year)

**JIP-28 delegation is NOT material at 79K stake.**

---

## 7. The REAL Decision Matrix (Updated with Verified Numbers)

### Option A: Fix BAM Connection + Keep 5% Commission + 10% MEV
- **Commission revenue:** ~774 SOL/year (unchanged — keep all current income)
- **JIP-31 income:** ~72.5 SOL/year (NEW — unlocked by fixing BAM connection)
- **JIP-28 eligibility:** NO (requires 0% commission)
- **Total: ~846 SOL/year (~$71,910)**
- **Net gain vs current: +72.5 SOL/year**

### Option B: Fix BAM + Drop to 0% Commission, Keep MEV ≤10%
- **Inflation commission revenue:** 0 SOL/year (lose ~232 SOL/year)
- **Priority fee + MEV revenue:** ~537 SOL/year (keep — these are block rewards, not commission-dependent)

Wait — **critical distinction**: At 0% inflation commission, you lose the inflation cut. But block rewards (priority fees, MEV tips, signature fees) flow to the validator regardless of inflation commission. Let me recalculate:

- **Block rewards (validator keeps):** Priority fees + MEV tips + signature fees at current commission = ~542 SOL/year
  - At 0% inflation commission, you still keep block reward commissions
  - At 0% MEV commission, you'd lose the MEV cut (~5.2 SOL/year — negligible)
- **JIP-31 income:** ~72.5 SOL/year
- **JIP-28 delegation:** ~0.5 SOL/year additional
- **Total: ~615 SOL/year**
- **Net loss vs Option A: ~231 SOL/year (~$19,635)**

### Option C: Fix BAM + Do Nothing Else (Status Quo Commissions)
- **Same as Option A: ~846 SOL/year**

---

## 8. VERDICT

### IMMEDIATE: Fix the BAM Node Connection

**You are leaving ~72.5 SOL/year (~$6,163/year) on the table** by not having a proper BAM node connection. The BAM software is installed and running, but the compliance check fails because `bam_node_connection: null`. This is free money — JIP-31 does NOT require any commission changes. Fix the connection, wait 3 epochs, start claiming.

**Estimated unclaimed losses so far:** Program started epoch 911, current epoch 934 = 23 epochs elapsed. If you were eligible from the start: ~9.1 SOL (~$774) already lost to reflow. Every epoch you wait = another ~0.4 SOL lost.

### COMMISSION: Keep 5% — EV NEGATIVE to Drop

**At 79,361 SOL stake, dropping to 0% commission for JIP-28 is EV NEGATIVE.**

The updated math:
- You **lose** ~232 SOL/year in inflation commission
- You **gain** ~0.5 SOL/year from JIP-28 delegation (negligible at this stake)
- JIP-31 subsidies are the same regardless (no commission requirement)

**The 0% commission play is EV+ ONLY for validators with significantly more stake** where:
1. JIP-28 delegation is proportionally larger
2. Additional leader slots from delegation generate meaningful MEV/priority fees
3. The validator competes for ecosystem delegation (Marinade, SFDP) where 0% is expected

### Break-even:
For 0% commission to be EV+, you'd need JIP-28 delegation to generate ≥232 SOL/year in additional block rewards. At current rates (~0.037 SOL/block), that requires ~6,270 extra blocks/year = ~34 extra blocks/epoch = ~34 extra leader slots/epoch. To get 34 extra leader slots you'd need roughly **3-5M SOL in additional delegation** — far beyond what JIP-28 would provide at 79K base stake.

---

## 9. Action Items (Priority Order)

### 1. FIX BAM NODE CONNECTION (URGENT — ~$6K/year at stake)
- Check Jito BAM configuration in your validator setup
- Verify BAM relay endpoint URL and authentication credentials
- Check validator logs for BAM connection errors: `grep -i "bam\|block.engine\|bundle" /path/to/validator/logs`
- Ensure firewall allows outbound connections to Jito block engine BAM ports
- Contact Jito Discord (#bam-support or #validator-support) if connection issues persist
- Once fixed: 3-epoch warmup (~6 days), then start claiming via:
  ```
  cargo r -p jito-bam-boost-cli -- bam-boost merkle-distributor claim \
    --network mainnet --epoch <EPOCH> \
    --rpc-url <RPC_URL> --signer <PATH_TO_KEYPAIR> \
    --commitment confirmed \
    --jito-bam-boost-program-id BoostxbPp2ENYHGcTLYt1obpcY13HE4NojdqNWdzqSSb
  ```

### 2. KEEP 5% COMMISSION
- Commission revenue (~232 SOL/year) far exceeds JIP-28 benefit at this stake
- No reason to change until stake exceeds ~500K SOL

### 3. VERIFY MEV COMMISSION BOUNDARY
- Currently at exactly 10% (1000 bps)
- JIP-28 requires ≤10% — you're at the exact boundary
- If you ever DO want JIP-28, consider 9% to avoid any strict-less-than ambiguity
- But this is moot until you fix BAM connection AND decide 0% inflation commission is worth it

### 4. SET UP CLAIM AUTOMATION
- JIP-31 has a 10-epoch claim window; unclaimed rewards reflow
- Once eligible, set up a cron or script to claim every ~5 epochs to avoid missing the window
- Check API endpoint: `GET https://kobe.mainnet.jito.network/api/v1/claim/mainnet/{epoch}/{validator_identity}`

### 5. STAKE GROWTH CHANGES THE CALCULUS
- At 500K+ SOL: Re-evaluate 0% commission (JIP-28 + ecosystem delegation starts mattering)
- At 1M+ SOL: 0% becomes clearly EV+ (JIP-28 delegation compounds meaningfully)
- Current stake pool breakdown shows FOUNDATION at 37.6K (47%) — heavy reliance on one source

---

## 10. What ay0h's Post Actually Means

The screenshot from ay0h (CORE Research) highlights JIP-28 criteria. The "changing MEV and commission to get BAM stake EV+" framing is correct **for validators with large stake** where JIP-28 delegation compounds. For whale validators (1M+ SOL), dropping to 0% IS clearly EV+ because:
- Delegation compounds their leader slots significantly
- More blocks = more priority fees + MEV tips
- Block reward revenue dwarfs inflation commission at scale

For Saga DAO at ~79K SOL, you're in a fundamentally different bracket. Fix the BAM connection, collect JIP-31, keep your commissions.

---

## Appendix: Data Sources & Verification

| Data Point | Source | Method | Date |
|---|---|---|---|
| Validator metrics | Trillium API `/validator_rewards/` | Direct JSON query | Mar 5, 2026 |
| `is_bam: false` | Trillium API | Filtered by identity key | Mar 5, 2026 |
| JIP-31 eligibility | Trillium JIP-31 Rankings page | Searched all 259 listed validators | Mar 5, 2026 |
| JIP-31 claim API | Jito Kobe API | curl all epochs 914-934 | Mar 5, 2026 |
| JIP-31 rules | forum.jito.network/t/jip-31 | Full proposal text | Mar 5, 2026 |
| JIP-28 rules | forum.jito.network/t/jip-28 | Full proposal text | Mar 5, 2026 |
| Subsidy pool size | Trillium JIP-31 page header | 481 SOL/epoch | Epoch 934 |
| BAM stake share | Trillium JIP-31 page | 117.5M SOL, 27.83% | Epoch 934 |
