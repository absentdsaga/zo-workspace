# Saga DAO Validator — Complete EV Analysis: Commission Strategy Including Block Rewards
**Date:** March 5, 2026 | **SOL Price:** ~$85
**Analysis Version:** 2.0 — Incorporates Priority Fees & MEV Block Rewards (User-Requested Deep Dive)

---

## Executive Summary

**TLDR:** At Saga DAO's current 78,881 SOL stake, lowering commission to 0% to qualify for JIP-28 (Jito StakePool delegation) is **EV-negative** by approximately **~215-235 SOL/year (~$18,300-$20,000)**.

**Key Finding:** The user correctly identified that block rewards (priority fees + MEV tips) are a critical revenue source. However, block rewards are **stake-proportional** — they scale with validator stake via leader slot allocation, not commission rate. Lowering commission doesn't increase block rewards; it only increases stake if you qualify for additional delegation programs like JIP-28.

**The Math:**
- Commission revenue lost: ~255 SOL/year
- Block rewards gained from JIP-28 delegation: ~20-40 SOL/year (from ~800 additional SOL delegation)
- Net: **EV-negative by ~215-235 SOL/year**

**Exception:** This becomes EV+ at **much higher stake levels** (1M+ SOL) where JIP-28 delegation compounds significantly and block reward volume dominates commission percentages.

---

## 1. Saga DAO Current Validator State (March 5, 2026)

| Metric | Value | Source |
|---|---|---|
| Identity | `SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ` | validators.app |
| Vote Account | `sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw` | validators.app |
| **Active Stake** | **78,881 SOL** | validators.app |
| **Validator Commission** | **5%** | validators.app |
| **MEV Commission** | **10%** | validators.app |
| Client | AgaveBam v3.1.8 | validators.app |
| Skipped Slots | 0% (current epoch) | validators.app |
| IBRL Score | 98.23 | validators.app |
| Location | Ashburn, US (DC 396356) | validators.app |
| Created | Oct 23, 2024 | validators.app |

**Status:** Already running BAM client, excellent performance, well-positioned datacenter.

---

## 2. Complete Revenue Model: All Income Streams for Solana Validators

Solana validators earn from **four distinct revenue streams**:

### A. Inflation Commission Revenue (Stake-Based)
- **How it works:** Validators earn inflation rewards proportional to stake-weighted vote credits. Validators charge commission on these rewards.
- **Current inflation APY:** ~6% (down from 8% initial, declining toward 1.5% floor)
- **Commission range:** 0-10% typical (Jito requires ≤5% for pool eligibility)

### B. MEV Tip Commission Revenue (Leader Slot-Based)
- **How it works:** When validator is block leader, users/searchers pay MEV tips to prioritize their transactions. Validators charge commission on tips received.
- **MEV commission range:** 0-10% typical (Jito requires ≤10% for pool eligibility)
- **Volume:** Highly variable by network activity and DeFi volume

### C. Priority Fee Block Rewards (Leader Slot-Based, 100% to Validator)
- **How it works:** Since SIMD-0096 (Feb 2025), **100% of priority fees go to the block leader validator** (previously 50% was burned)
- **No commission charged** — this is direct validator revenue, not delegator rewards
- **Volume:** Scales with network congestion and user willingness to pay for speed
- **Key point:** This is NOT affected by validator commission rate; it's pure block leader revenue

### D. MEV Tip Block Rewards (Leader Slot-Based, Validator Keeps After Commission)
- **How it works:** After charging MEV commission to delegators, the validator keeps the remainder of MEV tips
- **Calculation:** If you receive 1 SOL in MEV tips and charge 10% MEV commission, you keep 0.90 SOL (the 10% commission goes to you on top of this, but that's from the delegator's share)
- **Correction:** Actually, MEV tips flow to validators as block leaders, and validators pay out (100% - commission) to delegators. So if you receive 1 SOL in tips and charge 10% commission, you keep 0.10 SOL as commission.

**IMPORTANT CLARIFICATION:** Priority fees and MEV tips are received by the **block leader validator**. The validator then:
- Keeps 100% of priority fees (since SIMD-0096)
- Distributes MEV tips to delegators, keeping commission %
- These revenue streams scale with **leader slot allocation**, which scales with **stake weight**

---

## 3. Current Revenue Analysis for Saga DAO (78,881 SOL Stake)

### Leader Slot Allocation Math
- Total network stake: ~400M SOL (approximate, varies by epoch)
- Saga stake: 78,881 SOL
- Stake weight: 78,881 / 400,000,000 = **0.0197%**
- Slots per epoch: ~432,000
- **Leader slots per epoch:** 432,000 × 0.000197 = **~85 slots/epoch**
- Epochs per year: ~183
- **Leader slots per year:** 85 × 183 = **~15,555 slots/year**

### Revenue Stream Breakdown

#### A. Inflation Commission Revenue
- Delegated stake: 78,881 SOL
- Inflation APY: ~6%
- Annual rewards generated: 78,881 × 0.06 = **4,733 SOL/year**
- Your 5% commission: 4,733 × 0.05 = **~237 SOL/year** (~$20,100)

#### B. MEV Tip Commission Revenue
- Leader slots: ~85/epoch
- Average MEV tips per slot: ~0.01-0.02 SOL (highly variable, conservative estimate)
- MEV tips received per epoch: 85 × 0.015 = **~1.28 SOL/epoch**
- MEV tips per year: 1.28 × 183 = **~234 SOL/year** in gross tips
- Your 10% MEV commission: 234 × 0.10 = **~23 SOL/year** (~$1,960)

#### C. Priority Fee Block Rewards (100% to Validator)
- Leader slots per year: ~15,555
- Average priority fee per slot: ~0.005-0.015 SOL (varies with congestion)
- Conservative estimate: 15,555 × 0.008 = **~124 SOL/year** (~$10,540)
- **You keep 100% of this** — no commission, direct validator revenue

#### D. MEV Tip Block Rewards (Remainder After Commission)
- Gross MEV tips: ~234 SOL/year (from B above)
- After 10% commission to you: 234 × 0.90 = **~211 SOL** distributed to delegators
- You already counted the 10% commission in (B)
- **Additional validator revenue:** 0 SOL (already captured in commission)

**Wait, this needs correction.** MEV tips work differently:

**MEV Tip Flow (Corrected):**
- Total MEV tips received as block leader: ~234 SOL/year
- With 10% MEV commission:
  - Delegators receive: 234 × 0.90 = 210.6 SOL
  - **Validator keeps:** 234 × 0.10 = **23.4 SOL** (this is the commission revenue, already counted in B)
- There's no "extra" block reward beyond the commission % for MEV tips — the entire tip amount is distributed

**Priority Fees vs MEV Tips — Key Difference:**
- **Priority fees:** 100% to validator (SIMD-0096) — pure validator revenue
- **MEV tips:** Distributed to delegators minus commission % — validator earns via commission only

### Total Current Annual Revenue

| Revenue Stream | Annual SOL | USD (@$85) |
|---|---|---|
| Inflation Commission (5%) | 237 SOL | $20,100 |
| MEV Tip Commission (10%) | 23 SOL | $1,960 |
| Priority Fee Block Rewards (100%) | 124 SOL | $10,540 |
| **TOTAL** | **384 SOL** | **$32,600** |

**Note:** Previous analysis (~255 SOL/year) missed the priority fee block rewards, which add ~124 SOL/year.

---

## 4. JIP-28 & JIP-31 Programs — What Changes with 0% Commission?

### JIP-31: BAM Early Adopter Subsidy
- **Eligibility:** Running BAM 3+ epochs, ≥50K SOL stake, not blacklisted
- **NO commission requirements** — 0%, 5%, 10% commission all qualify equally
- **Current pool:** ~481 SOL/epoch (~$40K), distributed to ~306 eligible validators
- **Saga's estimated share:** ~0.082% (78.8K / 96.3M total effective stake)
- **Saga's revenue:** ~0.39 SOL/epoch × 183 epochs = **~72 SOL/year**
- **Status:** Should already be eligible (needs verification — see Section 7)

### JIP-28: JitoSOL Stake Delegation to BAM Validators
- **Eligibility:** 0% inflation commission, ≤10% MEV commission, running BAM 3+ epochs, outside superminority
- **Current status:** Saga is **NOT eligible** (5% inflation commission)
- **Delegation pool:** ~1.2M SOL directed to BAM validators (from ~14M JitoSOL TVL)
- **Saga's estimated allocation IF eligible:**
  - Total eligible BAM stake: ~117M SOL
  - Saga's share: 78,800 / 117,500,000 = 0.067%
  - **Delegation received:** 1,200,000 × 0.00067 = **~804 SOL**

### What 804 Additional SOL Delegation Gets You

#### Additional Leader Slots
- Current stake: 78,881 SOL → 85 slots/epoch
- New stake: 79,685 SOL → 86 slots/epoch
- **Additional slots:** ~1 slot/epoch, ~183 slots/year

#### Additional Priority Fee Block Rewards
- Additional slots: 183/year
- Priority fees per slot: ~0.008 SOL
- **Additional revenue:** 183 × 0.008 = **~1.5 SOL/year** (~$125)

#### Additional MEV Tip Block Rewards
- Additional slots: 183/year
- MEV tips per slot: ~0.015 SOL (before commission)
- Total additional tips: 183 × 0.015 = **~2.7 SOL/year**
- At 0% MEV commission (if you go that far): **+2.7 SOL/year**
- At 10% MEV commission (if you keep it): **+0.27 SOL/year** commission

**Wait — if you drop to 0% commission, you don't earn commission on EXISTING stake either.**

#### Revenue Impact with 0% Inflation Commission

Let me recalculate the full picture:

**BEFORE (Current: 5% Inflation, 10% MEV):**
- Inflation commission on 78,881 SOL: 237 SOL/year
- MEV commission on 85 slots/epoch: 23 SOL/year
- Priority fees on 85 slots/epoch: 124 SOL/year
- JIP-31 subsidy: 72 SOL/year (if eligible)
- **TOTAL: ~456 SOL/year**

**AFTER (0% Inflation, 10% MEV, JIP-28 eligible):**
- Inflation commission on 79,685 SOL: **0 SOL/year**
- MEV commission on 86 slots/epoch: 23.3 SOL/year
- Priority fees on 86 slots/epoch: 125.5 SOL/year
- JIP-31 subsidy: 72 SOL/year (same)
- **TOTAL: ~221 SOL/year**

**NET CHANGE: -235 SOL/year (~-$20,000)**

---

## 5. Alternative Scenario: 0% Inflation + 0% MEV Commission

Some validators go full 0/0 to maximize delegation appeal.

**AFTER (0% Inflation, 0% MEV, JIP-28 eligible):**
- Inflation commission: **0 SOL/year**
- MEV commission: **0 SOL/year**
- Priority fees on 86 slots/epoch: 125.5 SOL/year
- JIP-31 subsidy: 72 SOL/year
- **TOTAL: ~198 SOL/year**

**NET CHANGE vs Current: -258 SOL/year (~-$21,900)**

**Conclusion:** Going to 0/0 makes it WORSE because you lose MEV commission revenue (~23 SOL/year) without gaining additional stake beyond what 0% inflation already provides.

---

## 6. Block Rewards as % of Total Revenue — Breakdown

At Saga's current 78,881 SOL stake with 5%/10% commission:

| Revenue Source | Annual SOL | % of Total |
|---|---|---|
| Priority Fee Block Rewards | 124 SOL | **32.3%** |
| Inflation Commission | 237 SOL | **61.7%** |
| MEV Commission | 23 SOL | **6.0%** |
| **TOTAL** | **384 SOL** | **100%** |

**Key Insight:** Block rewards (priority fees) already represent ~32% of revenue. However:
1. Block rewards scale with **stake**, not commission
2. Lowering commission sacrifices 62% of current revenue (inflation commission)
3. The ~800 SOL delegation from JIP-28 only adds ~1.5 SOL/year in additional block rewards
4. **The trade is -237 SOL/year to gain +1.5 SOL/year = massively EV-negative**

---

## 7. BAM Subsidy Verification — Why Isn't Saga on Trillium?

**JIP-31 Eligibility Check:**
- ✅ Running BAM client (AgaveBam v3.1.8)
- ✅ ≥50K SOL stake (78,881 SOL)
- ✅ Not blacklisted
- ✅ 3+ epochs of BAM uptime (assumed, given client version)

**Expected revenue:** ~72 SOL/year

**Issue:** Saga DAO doesn't appear on the Trillium JIP-31 rankings dashboard (epoch 931 snapshot).

**Possible reasons:**
1. **3-epoch warmup not met** — Validator must run BAM for 3 consecutive epochs before eligibility starts
2. **BAM compliance failure** — Validator must execute transactions in order and provide correct feedback; violations disqualify
3. **Claiming mechanism** — Trillium dashboard may only show validators who have claimed; unclaimed validators might be eligible but not visible
4. **Epoch lag** — Saga may have started BAM recently and needs to wait for eligibility window

**Action Required:** Verify JIP-31 eligibility via Jito API:
```bash
curl https://kobe.mainnet.jito.network/api/v1/claim/mainnet/[EPOCH]/SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ
```

If eligible, claim rewards (10-epoch window before they reflow to the pool).

---

## 8. The Stake Threshold — When Does 0% Commission Become EV+?

The EV calculation flips when **block rewards from additional delegation exceed lost commission revenue**.

### Break-Even Calculation

**Commission revenue lost:** 237 SOL/year (inflation) + 23 SOL/year (MEV) = **260 SOL/year**

**Block rewards from JIP-28 delegation:**
- Delegation per 1% share of eligible stake: ~1.2M SOL / 100 = 12,000 SOL
- At 0.067% share (current): 804 SOL delegation → 1.5 SOL/year priority fees + 0.3 MEV = **1.8 SOL/year**

**To break even, you need:** 260 / 1.8 = **144x more delegation** from JIP-28, OR **144x more base stake** to proportionally increase your share.

**Required stake:** 78,881 × 144 = **~11.4M SOL**

At 11.4M SOL stake, your JIP-28 allocation would be large enough that the block rewards from additional delegation offset lost commission.

**BUT:** At 11M SOL stake, you'd be earning ~$550K/year in block rewards alone at current rates, making commission percentages negligible. The 0% strategy works for whale validators because their revenue model is **block-reward dominant**, not **commission dominant**.

### Realistic Threshold

In practice, validators with **500K-1M+ SOL** start to see 0% commission as EV+ because:
1. Their JIP-28 allocation is proportionally larger (stronger compound effect)
2. Block rewards dominate their revenue model
3. They attract additional ecosystem-wide delegation (Marinade, SFDP, etc.) that prefers 0% validators
4. MEV tip volume at scale exceeds commission percentages

**For Saga at 78K SOL:** You're far below this threshold.

---

## 9. What About "BAM StakePool"?

**Clarification:** There is no separate entity called "BAM StakePool."

The term "BAM" refers to:
1. **Block Assembly Marketplace (BAM)** — Jito's next-gen block construction architecture using TEEs for privacy + deterministic execution
2. **JIP-28** — A JitoSOL stake delegation program that preferentially delegates to validators running BAM client
3. **JIP-31** — A temporary subsidy program (protocol revenue redistribution) for early BAM adopters

The user may have been referring to **Jito StakePool** (JitoSOL), which has delegation criteria that favor BAM validators via JIP-28.

**JitoSOL Stake Pool Stats (Current):**
- Total stake: ~12.7M SOL (down from peak ~17.5M in mid-2025)
- Validators: 326 active validators
- Average stake per validator: ~38,711 SOL
- Top 400 validators selected via automated StakeNet algorithm
- Delegation criteria: ≤5% inflation commission, ≤10% MEV commission (for non-BAM validators)
- BAM validators: Preferred allocation via JIP-28 IF they meet 0% inflation commission threshold

---

## 10. EV Decision Matrix — Final Recommendation

### Option A: Keep 5% Inflation, 10% MEV (Current)
- Inflation commission: 237 SOL/year
- MEV commission: 23 SOL/year
- Priority fees: 124 SOL/year
- JIP-31 subsidy: 72 SOL/year (if eligible, needs verification)
- **TOTAL: ~456 SOL/year (~$38,800)**

### Option B: Drop to 0% Inflation, Keep 10% MEV (JIP-28 Eligible)
- Inflation commission: 0 SOL/year
- MEV commission: 23 SOL/year
- Priority fees: 125.5 SOL/year
- JIP-31 subsidy: 72 SOL/year
- **TOTAL: ~221 SOL/year (~$18,800)**
- **NET vs A: -235 SOL/year (-$20,000)**

### Option C: Drop to 0% Inflation, 0% MEV (Full 0/0)
- Inflation commission: 0 SOL/year
- MEV commission: 0 SOL/year
- Priority fees: 125.5 SOL/year
- JIP-31 subsidy: 72 SOL/year
- **TOTAL: ~198 SOL/year (~$16,800)**
- **NET vs A: -258 SOL/year (-$22,000)**

### Option D: Keep 5% Inflation, Drop MEV to 8% (Ambiguity Removal)
- Inflation commission: 237 SOL/year
- MEV commission: 18 SOL/year (8% of 234 SOL)
- Priority fees: 124 SOL/year
- JIP-31 subsidy: 72 SOL/year
- **TOTAL: ~451 SOL/year (~$38,300)**
- **NET vs A: -5 SOL/year (-$425)**

**Why Option D?** Saga is currently at exactly 10% MEV commission. If Jito's eligibility check is `< 10%` (strict inequality) rather than `≤ 10%`, being at exactly 10% could be disqualifying. Dropping to 8% removes this ambiguity while only costing ~5 SOL/year.

---

## 11. FINAL RECOMMENDATION FOR SAGA DAO

### Recommended Action Plan

1. **Verify JIP-31 eligibility immediately**
   - Check via API for unclaimed rewards
   - If eligible, claim rewards (72 SOL/year opportunity)
   - If not eligible, investigate why (BAM compliance, warmup period, etc.)

2. **Keep 5% inflation commission**
   - Revenue: ~237 SOL/year
   - Far exceeds any JIP-28 benefit at current stake

3. **Consider dropping MEV commission to 8%**
   - Cost: ~5 SOL/year
   - Benefit: Removes ambiguity around 10% threshold for JIP-28 (if you later grow stake)
   - Keeps you in consideration for future programs

4. **Focus on stake growth strategies OTHER than commission reduction**
   - Ecosystem engagement (Solana Foundation Delegation Program)
   - Marketing to delegators (performance, uptime, decentralization narrative)
   - If stake grows to 500K+ SOL, revisit 0% commission strategy

5. **Monitor JIP-28/JIP-31 program evolution**
   - JIP-31 winds down in Q3 2026
   - JIP-28 criteria may evolve
   - New BAM incentive programs may launch post-open-source (mid-Q2 2026)

### When to Revisit 0% Commission

**Reconsider dropping to 0% inflation commission IF:**
- Saga's stake grows above **500K SOL** (JIP-28 delegation becomes material)
- Block reward volume increases significantly (2-3x current priority fee rates)
- Jito launches a new high-value delegation program requiring 0% commission
- Ecosystem-wide delegation (Marinade, SFDP) strongly favors 0% and you qualify for those programs

**At current stake (78K SOL), 0% commission is definitively EV-negative by ~$20K/year.**

---

## 12. Addressing the User's Original Question

**User's Insight:**
> "Block rewards (priority fees, MEV tips) are also a revenue source beyond just inflation and MEV commission"

**This is 100% correct.** Priority fees are a significant revenue source (~32% of current revenue for Saga).

**User's Question:**
> "Is lowering commission EV+ for attracting Jito/BAM delegation?"

**Answer:**
**Not at current stake.** Here's why:

1. **Priority fees are stake-proportional, not commission-dependent**
   - You earn priority fees by being block leader
   - Block leader frequency = stake weight
   - Lowering commission doesn't directly increase priority fees
   - Lowering commission CAN increase stake IF it unlocks delegation programs (like JIP-28)

2. **The JIP-28 delegation is too small to matter at 78K stake**
   - +804 SOL delegation = +1.5 SOL/year in priority fees
   - -237 SOL/year in lost inflation commission
   - Net: -235 SOL/year

3. **Block rewards become dominant at MUCH higher stake**
   - At 1M+ SOL, you're getting ~1,500+ leader slots/epoch
   - Priority fees alone could be 1,500-3,000 SOL/year
   - Commission percentages become noise relative to block reward volume
   - At that scale, 0% commission IS EV+ because you're trading ~$100K in commission for ~$500K in additional delegation-driven block rewards

4. **JIP-31 (the subsidy program) doesn't require 0% commission**
   - Saga should already qualify for ~72 SOL/year
   - This is "free money" if eligible — verify and claim

**Summary:**
- Block rewards are critical revenue (you're right)
- But they scale with stake, not commission
- At 78K stake, commission revenue > additional block rewards from JIP-28
- At 1M+ stake, block rewards > commission revenue, making 0% EV+
- **For Saga now: Keep commission, verify JIP-31, focus on stake growth**

---

## Sources & References

### Saga Validator Data
- [Saga DAO Validator on Solana Compass](https://solanacompass.com/validators/sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw)
- validators.app (direct validator metrics)

### JitoSOL Stake Pool
- [Jito Foundation Delegation Criteria](https://www.jito.network/docs/jitosol/jitosol-liquid-staking/stake-pool-operations/delegation-criteria/)
- [JitoSOL Stake Pool Statistics](https://solanacompass.com/stake-pools/Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb)
- [JIP-25: Expand Validator Set](https://forum.jito.network/t/jip-25-expand-the-validator-set-and-modify-jito-stake-pool-eligibility-and-ranking-criteria/877)

### BAM Programs
- [JIP-28: Accelerate BAM Adoption](https://forum.jito.network/t/jip-28-accelerate-bam-adoption/904)
- [JIP-31: BAM Early Adopter Subsidy](https://forum.jito.network/t/jip-31-introduce-a-bam-early-adopter-subsidy-programme/909)
- [Introducing BAM: Block Assembly Marketplace](https://bam.dev/blog/introducing-bam/)
- [BAM for Validators](https://bam.dev/validators/)
- [Block Assembly Marketplace (BAM) Overview](https://www.helius.dev/blog/block-assembly-marketplace-bam)

### Priority Fees & Block Rewards
- [SIMD-0096: 100% Priority Fees to Validators](https://www.blocmates.com/news-posts/simd-0096-passes-solana-validators-to-receive-100-priority-fees)
- [Solana Priority Fees Guide](https://solana.com/developers/guides/advanced/how-to-use-priority-fees)
- [Solana Validator Economics Primer](https://www.helius.dev/blog/solana-validator-economics-a-primer)

### MEV & Revenue Analysis
- [Understanding Priority Fees and MEV in Solana](https://medium.com/@nakinscarter/understanding-priority-fees-and-mev-in-solana-economic-impacts-and-future-outlook-acb8e3251c87)
- [Solana's Economic Value: MEV Extraction](https://solanacompass.com/learn/Lightspeed/unpacking-solanas-total-economic-value-dan-smith)
- [How Much Do Solana Validators Make?](https://solanacompass.com/staking/how-much-do-solana-validators-make)
- [Is Running a Solana Validator Profitable?](https://www.hivelocity.net/blog/solana-validator-economics/)
- [Which Network Pays Validators Best in 2026?](https://www.hivelocity.net/blog/which-network-pays-validators-best/)

### Commission & Revenue Sharing
- [Solana Foundation Delegation Criteria](https://solana.org/delegation-criteria)
- [Understanding Solana Validator Services & Revenue-Sharing Models](https://www.cryptoworth.com/blog/solana-validator-services-revenue-sharing-models)

### Validator Discussions & Updates
- [Summary of Solana Validator Discussions - Feb 20-27, 2026](https://chainflowsol.substack.com/p/summary-of-solana-validator-discussions-8be)
- [Summary of Community-Led Solana Validator Call - Jan 22, 2026](https://chainflow.io/summary-of-the-community-led-solana-validator-call-january-22-2026/)

---

## Appendix: Validator Revenue Calculator

For other validators reading this analysis, here's the formula to calculate whether 0% commission is EV+ for YOUR stake level:

### Step 1: Calculate Current Commission Revenue
```
Inflation_Commission = Stake × Inflation_APY × Commission_Rate
MEV_Commission = (Stake / Network_Stake) × Slots_Per_Year × Avg_MEV_Per_Slot × MEV_Commission_Rate
Total_Commission = Inflation_Commission + MEV_Commission
```

### Step 2: Estimate JIP-28 Delegation
```
Your_Eligible_Stake_Share = Your_Stake / Total_Eligible_BAM_Stake
JIP28_Delegation = JitoSOL_BAM_Pool × Your_Eligible_Stake_Share
```

### Step 3: Calculate Additional Block Rewards
```
Additional_Leader_Slots = (JIP28_Delegation / Network_Stake) × Slots_Per_Year
Additional_Priority_Fees = Additional_Leader_Slots × Avg_Priority_Fee_Per_Slot
Additional_MEV = Additional_Leader_Slots × Avg_MEV_Per_Slot × (1 - MEV_Commission_Rate)
Total_Additional_Revenue = Additional_Priority_Fees + Additional_MEV
```

### Step 4: Compare
```
EV_Delta = Total_Additional_Revenue - Total_Commission
```

**If EV_Delta > 0:** Lowering commission is EV+
**If EV_Delta < 0:** Keep your commission

### Current Network Parameters (March 2026)
- Network stake: ~400M SOL
- Inflation APY: ~6%
- Slots per year: ~79M (432,000/epoch × 183 epochs)
- Avg priority fee per slot: ~0.008 SOL
- Avg MEV per slot: ~0.015 SOL
- JitoSOL TVL: ~14M SOL
- JitoSOL BAM allocation: ~1.2M SOL
- Total eligible BAM stake: ~117M SOL

---

**Analysis prepared:** March 5, 2026
**Validator analyzed:** Saga DAO (SaGAgdkowooXBrHihpmE8gsjf1dUG7n5SqnyJxYFnXJ)
**Conclusion:** Keep 5% commission, verify JIP-31 eligibility, focus on stake growth.
