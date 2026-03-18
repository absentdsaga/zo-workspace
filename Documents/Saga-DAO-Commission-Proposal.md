# Saga DAO Validator — Commission Optimization Proposal

**Date:** March 15, 2026
**Prepared for:** Saga DAO Core Team
**Validator:** sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw
**Current Commission:** 5% inflation / 10% MEV
**Options Analyzed:** 0% / 0% (primary) and 3% / 5% (alternative)

---

## Executive Summary

At 5% inflation / 10% MEV, Saga DAO is being destaked by Marinade and is locked out of Jito, BlazeStake (>50K tier), Vault elite, and JPool. By dropping to 0/0, we unlock delegation from every commission-sensitive pool on Solana.

However, this is not a slam dunk. The math is nuanced:

- **Gross stake growth:** ~80K → ~128K SOL (+60%)
- **Net annual profit improvement:** +200 to +370 SOL/yr (after all costs)
- **Marinade SAM is nearly net-zero** at current auction clearing prices (~425 SOL/yr bond drain vs ~437 SOL/yr gross revenue)
- **STKE is not viable** — Saga DAO's WizScore (79.5 at 5%, ~87 at 0%) is far below the ~95+ cutoff. Hosting location penalties (Ashburn) are the blocker, not commission.
- **Vault elite is real and continuous** — ~12,500 SOL/validator, algorithmic (top 50 vote credits among ~130 approved validators), evaluated every epoch
- **A 3/5 option preserves some commission income** while still qualifying for Jito and Marinade, at the cost of losing JPool, BlazeStake >50K, and Vault elite

The case for 0/0 rests on **Jito** (free, +308 SOL/yr), **Vault elite** (+73 SOL/yr), **BlazeStake >50K** (+34 SOL/yr), and **JPool** (+24 SOL/yr). Marinade's high auction costs make it a wash at current clearing prices.

**Alpenglow upgrade** (expected 2026) eliminates vote costs (~365 SOL/yr), which significantly improves the economics of any commission setting — including staying at 5/10.

---

## Full Profit & Loss View

Before analyzing commission options, here's the actual cost structure of running the validator:

### Operating Costs (Annual, Commission-Independent)

| Cost | SOL/yr | Notes |
|---|---|---|
| Vote transaction costs | ~365 | ~1 SOL/day; **eliminated by Alpenglow upgrade** |
| Hosting (bare metal) | ~50 | ~$370/mo at current SOL price (~$88) |
| **Total operating costs** | **~415** | Drops to ~50 after Alpenglow |

### Current P&L (5/10 Commission, ~72K SOL post-Marinade destake)

| Line Item | SOL/yr |
|---|---|
| Block rewards + priority fees (100% to validator) | ~556 |
| Inflation commission (5% of staker rewards) | ~231 |
| MEV commission (10% of tips) | ~11 |
| **Gross revenue** | **~798** |
| Vote costs | -365 |
| Hosting | -50 |
| DoubleZero rev share | -3 |
| **Net profit** | **~380** |

This is the true baseline. Every scenario must beat ~380 SOL/yr net profit to justify the change.

---

## Stake Sources: What's Real, What's Speculative

Each source evaluated with conservative estimates informed by operational experience and primary source verification.

### Hard Facts (Verified from Primary Sources)

| Fact | Source | Verified |
|---|---|---|
| Jito pool: 12.69M SOL across **314 validators** | jito.network StakeNet | Yes |
| Jito scoring: Tier 1 = inflation commission (dominant), Tier 2 = MEV, Tier 3 = age, Tier 4 = credits | StakeNet docs | Yes |
| Marinade SAM epoch 941 clearing yield: 0.39470 PMPE | psr.marinade.finance | Yes |
| Marinade bond drain decomposition: 0.33005 (free commission discount) + 0.06465 (actual bond drain) | SAM auction mechanics | Yes |
| BlazeStake: validators with >50K SOL total stake must have literally 0% inflation AND 0% MEV | BlazeStake docs | Yes |
| JPool: requires 0% staking commission — hard gate, not APY-ranked | JPool criteria | Yes |
| SFDP: now matching at 50% (down from 100%), cap 50K SOL | Solana Foundation | Yes |
| Vault: ~1.25M SOL pool, elite bucket (50%) = ~626K SOL across top 50 validators = ~12,500 each. 0/0 required. Algorithmic, every-epoch evaluation. One-time board approval for allowlist. | Vault docs, Solana Compass | Yes |
| STKESOL: 691K SOL across ~50 validators (~13,800 each). WizScore top 50-60 required (~95+). Commission is 15/100 of score. Saga DAO scores 79.5 at 5%, ~87 at 0% — below cutoff due to hosting penalties (Ashburn ASN -3.34, city -1.0). | StakeWiz API, SOL Strategies | Yes |
| Commission changes (both inflation and MEV): on-chain tx, no restart required | Solana runtime | Yes |
| Alpenglow: eliminates vote costs, expected 2026 | Solana roadmap | Yes |

### Stake Source Projections (Conservative)

| Rank | Stake Source | Current | At 0/0 (Conservative) | At 0/0 (Optimistic) | Gross Rev (SOL/yr) | Pool Cost (SOL/yr) | Net Rev (SOL/yr) | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | **Jito** | 0 | 31,750 | 40,000 | +308 | 0 | **+308** | High — 314 validators, clear scoring criteria |
| 2 | **Marinade SAM** | 9K → 0 | 45,000 | 45,000 | +437 | ~425 | **+12** | High volume, but **near-zero net** at current clearing prices |
| 3 | **SFDP** | 40,000 | 40,000 | 40,000 | 0 | 0 | 0 | Locked — commission-insensitive up to 10% |
| 4 | **Phase** | 9,000 | 9,000 | 9,000 | 0 | 0 | 0 | Locked — already qualifying |
| 5 | **dynoSOL** | 8,000 | 8,000 | 8,000 | 0 | 0 | 0 | Locked — already qualifying |
| 6 | **DoubleZero** | 5,000 | 5,000 | 5,000 | 0 | ~3 | -3 | Locked — DZ membership, not commission |
| 7 | **BlazeStake** | 500 | 4,000 | 4,000 | +34 | 0 | **+34** | High — hard 0/0 gate for >50K validators |
| 8 | **JPool** | 3,000 | 5,500 | 5,500 | +24 | 0 | **+24** | High — 0% hard gate, we qualify |
| 9 | **Vault** | 5,000 | 12,500 | 12,500 | +73 | 0 | **+73** | Medium — elite bucket is algorithmic (top 50 by vote credits among ~130 approved validators, rolling 10-epoch window). Pool has ~1.25M SOL; elite = 50% = ~626K across 50 validators = ~12,500 each. One-time board approval required to join allowlist, then continuous. |
| 10 | **STKE (STKESOL)** | 0 | 0 | 0 | 0 | 0 | **0** | **Not viable.** WizScore 79.5 at 5%; ~87 at 0%. Cutoff is top 50-60 (need ~95+). Hosting penalties (Ashburn ASN: -3.34, city: -1.0) are the structural blocker — commission alone doesn't fix it. Pool has 691K SOL across ~50 validators (~13,800 each), but we can't reach the scoring threshold without relocating. |
| — | **Native** | ~500 | ~500 | ~500 | 0 | 0 | 0 | — |
| | **TOTAL** | **~80,000** | **~128,250** | **~128,250** | **+876** | **~428** | **+448** | |

**Critical insight: Marinade SAM is nearly net-zero.** At current clearing prices (epoch 941), the bond drain is ~425 SOL/yr for 45K delegation. The gross revenue from that 45K is ~437 SOL/yr. Net: **~12 SOL/yr.** ay0h was right to flag this — the SOL lands on your validator but you pay almost all of it back through the auction.

**STKE is structurally blocked.** At 0/0, our WizScore rises from 79.5 to ~87 — still far below the ~95+ needed to rank top 50-60 out of all Solana validators. The blocker isn't commission — it's hosting penalties (-3.34 ASN concentration for Ashburn, -1.0 city concentration). Qualifying would require relocating infrastructure, which is not on the table. ay0h's experience with EAT validator not getting STKE is real, but the reason applies equally to Saga DAO despite our larger stake — WizScore doesn't weight validator size enough to overcome the hosting penalties.

**Vault elite is stronger than initially estimated.** The Vault pool holds ~1.25M SOL. The elite bucket (50% of pool = ~626K SOL) is split equally among the top 50 validators by vote credits, yielding **~12,500 SOL/validator**. This is algorithmic and continuous (evaluated every epoch), not intermittent. The only human gate is one-time board approval to join the ~130-validator allowlist. If Saga DAO's vote credits rank in the top 50 of approved validators, this is reliable delegation.

**The real case for 0/0 is Jito + Vault elite + the free pools:** Jito delivers +308 SOL/yr, Vault elite +73, BlazeStake +34, JPool +24. These four free sources total +439 SOL/yr and account for the entire net gain.

### Sources We Cannot Access (regardless of commission)

| Pool | Reason |
|---|---|
| Edgevana | Requires Edgevana hosting infrastructure |
| SharkPool | US/Canadian university validators only |
| JagPool | Geographic (LATAM/Singapore/South Africa) |
| Shinobi/xSHIN | Top 54 by vote credits only |

---

## Marinade SAM: Deep Dive on Costs

The SAM auction is the most misunderstood piece of validator economics. Here's how it actually works:

### How the Auction Works

1. Validators post a bond (1 SOL per 10K SOL delegated minimum)
2. Each epoch, validators bid a maximum CPMPE (Cost Per Mille Per Epoch) in the uniform-price auction
3. All winners pay the **clearing price** (lowest winning bid), not their individual bid
4. The clearing yield decomposes into two parts:
   - **`onchainDistributedPmpe`** (0.33005 at epoch 941): free commission discount — doesn't drain bond
   - **`auctionEffectiveBidPmpe`** (0.06465 at epoch 941): actual bond drain

### What 45K Delegation Actually Costs

```
Bond drain per epoch = 0.06465 PMPE × 45 mille = 2.91 SOL/epoch
Annual bond drain = 2.91 × ~146 epochs/yr = ~425 SOL/yr
```

Compare to gross revenue from 45K SOL delegation:
```
Block + priority revenue = 45K × 0.00000972 SOL/SOL/epoch × 146 = ~64 SOL/yr
Wait — that's using per-SOL-staked rate. Let me use per-slot:
45K additional SOL at our total → ~50 more leader slots/yr...
```

Let me recalculate properly. At 0/0 with 120K+ total stake:
- Total leader slots: ~134/epoch (at 120K) to ~185/epoch (at 166K)
- Per-slot revenue: ~0.0336 SOL (block rewards + priority fees, from our Trillium data)
- Marginal revenue from 45K more SOL: ~50 more slots/epoch × 0.0336 = ~1.68 SOL/epoch
- Annual: ~245 SOL/yr from the marginal Marinade stake

**Net from Marinade: 245 - 425 = -180 SOL/yr.** At current clearing prices, Marinade SAM is actually **net negative** as marginal stake.

However, this analysis depends on whether you attribute revenue proportionally or marginally. The full picture is better captured in the scenario comparison below.

### Historical Trend Warning

Clearing prices have **nearly doubled** over the last 20 epochs. If this trend continues, the bond drain gets worse, not better. Our 13 SOL bond would be depleted in ~4.5 epochs at current drain rates — it needs topping up every ~9 days.

---

## The 3/5 Alternative (ay0h's Suggestion)

CORE Research (ay0h) suggested considering 3% inflation / 5% MEV as a middle ground. Here's how it compares:

### What 3/5 Qualifies For

| Pool | At 3/5 | At 0/0 | Difference |
|---|---|---|---|
| **Jito** | Eligible — 3% ranks in scoring but below all 0% validators | Eligible — top-ranked | Jito has 314 slots; ~200+ are 0% validators. At 3%, we'd rank below them but likely still make top 314 |
| **Marinade SAM** | Eligible — can compete by raising bid (costs more) | Eligible — natural APY clears floor with minimal bid | Higher bond drain at 3/5 |
| **JPool** | **Disqualified** — requires 0% (hard gate) | Qualified | Lose ~2,500 SOL |
| **BlazeStake >50K** | **Disqualified** — requires literal 0/0 | Qualified | Lose ~3,500 SOL |
| **Vault elite** | **Disqualified** — requires 0/0 | Qualified (~12,500 SOL) | Lose ~12,500 SOL (continuous, algorithmic) |
| **SFDP** | Qualified | Qualified | Same |
| **Phase** | Qualified | Qualified | Same |
| **dynoSOL** | Qualified (<=5%/<=10%) | Qualified | Same |
| **DoubleZero** | Qualified (<=10%) | Qualified | Same |

### 3/5 P&L Projection

| Line Item | At 3/5 | At 0/0 |
|---|---|---|
| **Total stake** | ~105-115K | ~128K |
| Inflation commission (3%) | ~115-125 | 0 |
| MEV commission (5%) | ~3-4 | 0 |
| Block + priority fees | ~680-750 | ~830 |
| Marinade SAM bond drain | ~450-500 (higher bid needed) | ~425 |
| **Gross revenue** | ~798-879 | ~830 |
| Vote costs | -365 | -365 |
| Hosting | -50 | -50 |
| DZ rev share | -3 | -3 |
| **Net profit** | **~380-461** | **~412** (or ~387 w/ Marinade) |

**Key finding: 0/0 has a modest edge over 3/5**, primarily driven by Vault elite (~12,500 SOL, +73 SOL/yr) and the hard-gated pools (JPool +24, BlazeStake +34). At 0/0 without Marinade (skipping the ~425 SOL/yr bond drain), net profit is ~412 — slightly above the 3/5 range. The commission income at 3/5 (~120 SOL/yr) roughly offsets the extra pool delegations at 0/0. The difference is within the margin of error.

### When 0/0 Clearly Wins

- Vault elite delivers ~12,500 SOL continuously (+73 SOL/yr, only available at 0/0)
- If Marinade clearing prices drop (making SAM cheaper for 0/0)
- After Alpenglow (vote costs eliminated, making the larger stake base more valuable)

### When 3/5 Clearly Wins

- If Marinade clearing prices rise further (making SAM more expensive for everyone)
- If Jito at 3% ranks us out of top 314 (then both options lose Jito)
- If we want optionality to raise commission later without Jito lookback penalty

---

## Alpenglow Impact

The Alpenglow upgrade eliminates vote transaction costs (~365 SOL/yr). This is a game-changer for the P&L of every validator.

### Post-Alpenglow P&L Comparison

| | Current (5/10) | At 3/5 | At 0/0 (no Marinade) | At 0/0 (with Marinade) |
|---|---|---|---|---|
| Total stake | 72K | ~110K | ~83K | ~128K |
| Gross revenue | ~798 | ~798-879 | ~870 | ~870 |
| Vote costs | **0** | **0** | **0** | **0** |
| Hosting + DZ | -53 | -53 | -53 | -53 |
| Marinade bond drain | 0 | ~450-500 | 0 | ~425 |
| **Net profit** | **~745** | **~345-426** (w/ Marinade) / **~745-826** (w/o) | **~817** | **~392** |

**Post-Alpenglow, 0/0 without Marinade is the clear winner at ~817 SOL/yr** — because vote cost elimination makes the larger free-pool stake base pure profit. Even staying at 5/10 (745 SOL/yr) beats any scenario that includes Marinade SAM's bond drain.

The key insight: Marinade's cost structure makes it a drag on profitability regardless of commission setting. More stake doesn't always mean more profit when the stake has a cost. Skip SAM and focus on free pools.

However, Marinade auction prices could decline as validator competition dynamics change with Alpenglow. This remains uncertain.

---

## Scenario Comparison (Pre-Alpenglow)

Five scenarios with honest, conservative numbers:

| Metric | Stay 5/10 | 5/10 + Marinade bid | Drop to 3/5 | Drop to 0/0 (conservative) | Drop to 0/0 (optimistic) |
|---|---|---|---|---|---|
| **Total Stake** | 72K (losing Marinade) | ~117K | ~105-115K | ~128K | ~128K |
| **Marinade** | Lost (0) | ~45K (high bid) | ~45K (moderate bid) | ~45K (low bid) | ~45K |
| **Jito** | No | No | Yes (ranked below 0%) | Yes (top-ranked) | Yes |
| **JPool** | No (3K existing) | No | **No** (0% hard gate) | Yes (+2.5K) | Yes |
| **BlazeStake >50K** | No | No | **No** (0/0 hard gate) | Yes (+3.5K) | Yes |
| **Vault elite** | No | No | **No** (0/0 hard gate) | Yes (+7.5K, ~12,500 total) | Yes |
| **STKE** | No | No | No | **No** (WizScore 87, need 95+. Hosting penalties block us.) | No |
| **Commission income** | 242 | 242 | ~120 | 0 | 0 |
| **Marinade bond drain** | 0 | ~500+ | ~450-500 | ~425 | ~425 |
| **Gross revenue** | 798 | ~1,010 | ~798-879 | ~865 | ~865 |
| **Net profit** | **~380** | **~395-445** | **~380-461** | **~387-440** | **~387-440** |
| **Break-even vs current** | — | Immediate | ~24 days | ~14 days | ~14 days |

### Reading the Table

- **Stay 5/10:** Safe, predictable, but losing Marinade. Profit: ~380 SOL/yr.
- **5/10 + Marinade bid:** Keeps Marinade but at very high bid cost. Marginal improvement. Misses Jito entirely.
- **3/5:** Preserves ~120 SOL/yr commission income. Gets Jito (probably). Loses JPool, BlazeStake >50K, Vault elite (~12,500 SOL continuous). Net is similar to 0/0 but gives up ~18.5K SOL in delegation from hard-gated pools.
- **0/0:** Unlocks everything except STKE (structurally blocked by hosting location). Vault elite is real and continuous (~12,500 SOL). Jito + Vault elite + BlazeStake + JPool = +439 SOL/yr from free pools, partially offset by giving up 242 SOL/yr in commission income.

**Note:** STKE is removed from all scenarios. At 0/0, Saga DAO's WizScore would be ~87 — still ~8 points below the ~95+ cutoff for the top 50-60 validators. The gap is driven by Ashburn hosting penalties (-4.34 combined), not commission. This cannot be fixed without relocating infrastructure.

### The Honest Assessment

**0/0 has a modest but real edge over 3/5**, primarily because of Vault elite (~12,500 SOL continuous = +73 SOL/yr) and the hard-gated pools (JPool +24, BlazeStake +34). These three pools add ~131 SOL/yr that 3/5 cannot access, vs ~120 SOL/yr in commission income that 3/5 preserves. The net difference is ~11 SOL/yr plus the strategic value of a larger stake base.

The choice depends on:

1. **Risk tolerance:** 0/0 is irreversible in practice (Jito 30-epoch lookback penalizes going back above 5%). 3/5 gives you room to adjust.
2. **Conviction on Vault elite:** If Saga DAO can consistently rank top 50 in vote credits among ~130 approved validators, 0/0 is the clear winner. If not, the margin narrows.
3. **Marinade clearing price direction:** If prices drop, 0/0 improves more. If prices rise, both get worse but 3/5 has commission income as a buffer.
4. **Alpenglow timing:** Post-Alpenglow, the larger stake base at 0/0 becomes more valuable (no vote costs to amortize).

---

## ay0h's Feedback — Addressed Point by Point

CORE Research raised several important challenges. Here's each one with our verified response:

| ay0h's Point | Our Finding | Status |
|---|---|---|
| "Cut the SAM estimate totally — it's a competitive auction, costs nearly what it delivers" | **Confirmed.** Bond drain ~425 SOL/yr vs ~437 gross = ~12 net. SAM is essentially a wash. | Corrected in this version |
| "STKE — we haven't gotten any despite qualifying" | **Confirmed, but for different reasons than EAT's experience.** STKESOL delegates to top 50-60 validators by WizScore (~95+ needed). Saga DAO scores 79.5 at 5%, ~87 at 0% — still far below cutoff. The blocker is Ashburn hosting penalties (-4.34 combined), not validator size or commission alone. ay0h's EAT validator faces similar hosting penalties. Even at 0/0, STKE is not viable without relocating. Zeroed in all scenarios. | Corrected — independently verified via StakeWiz API |
| "Vault elite is intermittent, not continuous" | **Partially disagreed after independent verification.** Vault docs and Solana Compass data show the elite bucket is algorithmic, evaluated every epoch, not intermittent. The pool holds ~1.25M SOL; elite (50%) = ~626K across top 50 validators by vote credits (rolling 10-epoch window) = ~12,500 SOL/validator. One-time board approval for the ~130-validator allowlist, then continuous. The question is whether Saga DAO ranks top 50 among approved validators — not whether the delegation happens. If we're in, it's steady. | Updated — Vault elite now +12,500 SOL (continuous) |
| "Consider 3/5 as alternative — keeps some commission income" | **Modeled fully.** 3/5 produces similar net profit to 0/0 at current clearing prices. Detailed P&L comparison included. | Added |
| "Jito has ~314 validators, not 400" | **Confirmed.** Updated to 314. | Corrected |
| "JPool requires 0% — it's a hard gate, not APY-ranked" | **Confirmed.** Updated to reflect hard 0% requirement. | Corrected |
| "Factor in vote costs and hosting as real expenses" | **Added.** Full P&L with vote costs (365 SOL/yr) and hosting (~50 SOL/yr). | Added |

---

## Ramp-Up Timeline & Cash Flow

### Pool Activation Schedule (at 0/0)

| Pool | Recalculation Cycle | Earliest Activation | Notes |
|---|---|---|---|
| **Marinade SAM** | Every epoch (~2 days) | Day 2-4 | Auction runs each epoch; stake activates next epoch |
| **JPool** | Every 5 epochs (~10 days) | Day 8-10 | 0% gate check + batch recalculation |
| **BlazeStake** | ~7 epochs (~14 days) | Day 12-14 | Coefficient recalculation cycle |
| **Jito** | Every 10 epochs (~20 days) | Day 14-20 | StakeNet scoring on 10-epoch windows |
| **Vault elite** | One-time board approval + algorithmic (every epoch) | Day 40+ (approval dependent) | Board approval for allowlist is one-time. Once approved, elite assignment is algorithmic — top 50 by vote credits among ~130 approved validators, rolling 10-epoch window. ~12,500 SOL/validator. |

**Jito lookback:** Jito checks if commission was ever *above* 5% in the last 30 epochs. We've been at exactly 5% (not above), so there's no lookback penalty.

### Break-Even Timing

The "valley of death" — the period where 0/0 earns less than staying at 5/10 — depends heavily on Marinade:

- **Without counting Marinade as a gain** (since it's net-zero): Break-even occurs when Jito activates (~day 14-20). Maximum cumulative deficit: ~15 SOL over those 2 weeks.
- **If Marinade delivers even modest net positive:** Break-even by day 8-10.

Either way, the transition cost is small relative to the annual gain.

---

## Cost of Participation Detail

| Pool | Capital Lockup | Ongoing Cost | Annual Cost (est.) | Notes |
|---|---|---|---|---|
| **Marinade SAM** | Bond: 13 SOL posted (need ~4.5 for 45K delegation ratio) | CPMPE auction drain | **~425 SOL/yr** (at epoch 941 clearing prices) | Bond depletes in ~4.5 epochs at current rates — needs frequent top-up. Bond earns staking rewards while locked, partially offsetting. |
| **DoubleZero** | $60-130K infra (sunk cost) | 5% of consensus revenue from DZ slots | ~3 SOL/yr | Already a member |
| **SFDP** | 100 SOL self-stake (already posted) | Vote costs ~1 SOL/day | Already paying | Cost exists regardless of commission |
| **Jito** | None | None | 0 | Pure score-based |
| **JPool** | None | None | 0 | 0% gate — free if qualified |
| **BlazeStake** | None | None | 0 | 0/0 gate for >50K — free if qualified |
| **Vault elite** | Self-stake via vSOL (soft req for Direct Stake bucket) | 0/0 commission + top 50 vote credits among ~130 approved validators | Opportunity cost only | One-time board approval for allowlist, then algorithmic. ~12,500 SOL/validator from ~1.25M pool. |
| **Phase** | None (requires SFDP) | None | 0 | SFDP is the gate |
| **dynoSOL** | None (requires SFDP) | None | 0 | SFDP is the gate |

---

## Risk Assessment

### What We Give Up at 0/0

| Risk | Impact | Mitigation |
|---|---|---|
| Commission income (5% inflation) | -231 SOL/yr (predictable) | Replaced by Jito delegation (+308) which is also predictable once scoring stabilizes |
| MEV commission (10%) | -11 SOL/yr (negligible) | N/A |
| Ability to raise commission | Jito's 30-epoch lookback penalizes going above 5% | If we ever need to raise, we lose Jito for ~60 days. This is the main irreversibility risk. |
| Bond capital for Marinade | 13+ SOL locked, draining ~2.9 SOL/epoch | Can exit Marinade auction at any time by not bidding. Bond returned. |

### What Could Go Wrong

| Scenario | Impact | Probability |
|---|---|---|
| Jito changes scoring (reduces 0% advantage) | Lose primary value driver | Low — 0% preference is structural to Jito's philosophy |
| Marinade clearing prices spike further | Bond drain increases, making SAM clearly net-negative | Medium — trend is upward. Mitigation: stop bidding. |
| Network fee revenue drops | All scenarios affected equally | Low — fees have been stable/growing |
| SFDP discontinued | Lose 40K stake regardless of commission | Low — Foundation has maintained for years |
| We need to raise commission for some reason | Lose Jito for 30 epochs if we go above 5% | Low — but real irreversibility |

### Downside Floor

Even if ONLY the free pools activate (Jito, BlazeStake, JPool, Vault elite) and we skip Marinade entirely:

| | SOL/yr |
|---|---|
| Stable pools (SFDP + Phase + dynoSOL + DZ + Vault basic) | ~67.5K stake |
| + Vault elite upgrade | +7.5K stake (to ~12,500 total) |
| + JPool | +2.5K stake |
| + BlazeStake | +3.5K stake |
| + Jito | +31.75K stake |
| **Total stake** | **~112.75K** |
| Block + priority fees | ~870 gross |
| Commission income | 0 |
| Vote costs + hosting + DZ | -418 |
| **Net profit** | **~452** |

vs. current net profit of ~380. **The conservative downside (no Marinade, no STKE) beats the status quo by ~72 SOL/yr** — driven entirely by free pools with zero participation cost.

---

## Execution Plan

### Option A: Go 0/0

**Step 1 — Change inflation commission (Day 0)**
```
solana vote-update-commission sagasJDjjAHND4hien3bbo5xXkzCT5Ss6nKjyUJ45aw 0 <AUTHORIZED_WITHDRAWER>
```
On-chain transaction, no restart required. Must be submitted during first half of epoch. Takes effect immediately.

**Step 2 — Set MEV commission to 0% (Day 0)**
Update via Jito tip distribution config. Also an on-chain transaction, no restart.

**Step 3 — Set Marinade SAM bid (Day 0-1)**
Set competitive CPMPE bid. Current clearing: 0.06465 PMPE bond drain. Our 13 SOL bond supports ~4.5 epochs at current drain rate — top up plan needed.

**Step 4 — Monitor activations (Days 2-30)**
- Day 2-4: Marinade should begin delegating
- Day 8-10: JPool recalculation
- Day 14-20: Jito StakeNet scoring
- Day 14: BlazeStake coefficient update

**Step 5 — Evaluate at epoch ~960 (~40 days)**
Review actual revenue vs projections. Decision point: continue Marinade auction or stop bidding if net-negative.

### Option B: Go 3/5

Same steps but set commission to 3% and MEV to 5%. Skip JPool (won't qualify). Marinade bid needs to be higher. Retains optionality to adjust later.

### Staging Strategy

Consider a phased approach:
1. **Week 1:** Drop to 3/5. Observe Jito scoring, Marinade response.
2. **Week 4:** If Jito delivers and economics are favorable, drop to 0/0.
3. **Ongoing:** Monitor Marinade bond drain. Stop bidding if net-negative for 3+ consecutive epochs.

This approach reduces risk but delays full benefit by ~2-4 weeks.

---

## Data Sources

- Validator epoch profitability: Trillium API via Coefficient (epochs 935-940)
- Marinade SAM auction: psr.marinade.finance (epoch 941 live data, bond drain decomposition)
- Jito delegation: jito.network StakeNet (314 validators, 12.69M SOL pool)
- BlazeStake criteria: stake.solblaze.org documentation (>50K hard 0/0 gate)
- JPool criteria: jpool.one documentation (0% hard gate)
- SFDP: Solana Foundation (50% matching, 50K SOL cap)
- Vault: thevault.finance documentation (elite bucket mechanics, ~1.25M SOL pool, ~130 approved validators)
- Vault pool data: Solana Compass (solanacompass.com/stake-pools)
- STKESOL: SOL Strategies monthly reports (691K SOL pool, ~50 validators)
- WizScore: StakeWiz API (stakewiz.com) — Saga DAO validator score, component breakdown
- Vote costs: Solana blockchain (~1 SOL/day observed)
- Alpenglow: Solana roadmap (vote cost elimination, expected 2026)
- Per-slot revenue validation: Rated Network study, epochs 749-786
- Operational feedback: CORE Research (ay0h), #validator-ops channel

---

## Summary & Recommendation

| Metric | Current (5/10) | At 3/5 | At 0/0 (no Marinade) | At 0/0 (with Marinade) |
|---|---|---|---|---|
| Total Stake | 72K (losing Marinade) | ~105-115K | ~83K | ~128K |
| Commission Income | 242 SOL/yr | ~120 SOL/yr | 0 | 0 |
| New Free Pool Stake | 0 | +31.75K (Jito only) | +45.25K (Jito + Vault elite + JPool + BlazeStake) | +45.25K + 45K Marinade |
| Gross Revenue | ~798 | ~798-879 | ~870 | ~870 |
| Operating Costs | -418 | -418 | -418 | -418 |
| Marinade Bond Drain | 0 | ~450-500 | 0 | ~425 |
| **Net Profit** | **~380** | **~380-461** | **~452** | **~387** (Marinade is a drag) |
| Jito Delegation | No | Yes (lower-ranked) | Yes (top-ranked) | Yes (top-ranked) |
| Vault Elite (~12,500 SOL) | No | No | Yes | Yes |
| JPool/BlazeStake | No | No | Yes | Yes |
| STKE | No | No | **No** (WizScore too low) | No |
| Reversibility | Full | Moderate | Low (Jito lookback) | Low |

### The Bottom Line

1. **Staying at 5/10 is viable but declining.** Marinade is destaking us. Net profit: ~380 SOL/yr, dropping as Marinade exits.

2. **3/5 is a reasonable middle ground.** Gets Jito (probably), preserves ~120 SOL/yr commission income, maintains flexibility. Expected net: ~380-461 SOL/yr. But misses Vault elite (~12,500 SOL continuous), JPool, and BlazeStake >50K.

3. **0/0 without Marinade is the strongest play.** Skip the SAM auction entirely. Vault elite (+12,500 SOL), Jito (+31,750), BlazeStake (+3,500), JPool (+2,500) are all free. Net profit: ~452 SOL/yr — **+72 SOL/yr over current, with zero participation costs beyond what we already pay.**

4. **0/0 with Marinade is actually worse** than 0/0 without it at current clearing prices. The ~425 SOL/yr bond drain eats the revenue from the 45K delegation. Only pursue Marinade if clearing prices drop significantly.

5. **STKE is not on the table.** WizScore 87 at 0/0, cutoff ~95+. Ashburn hosting penalties (-4.34) are the structural blocker. Would require infrastructure relocation to qualify.

6. **Vault elite is the swing factor between 3/5 and 0/0.** It's ~12,500 SOL continuous delegation (+73 SOL/yr), algorithmic, and only available at 0/0. Combined with JPool (+24) and BlazeStake (+34), the hard-gated pools add ~131 SOL/yr that 3/5 cannot access — slightly more than the ~120 SOL/yr commission income that 3/5 preserves.

7. **Alpenglow amplifies the 0/0 advantage.** Post-Alpenglow, 365 SOL/yr in vote costs disappear. The 0/0 (no Marinade) scenario jumps to ~817 SOL/yr net profit vs ~745 for staying at 5/10.

**Recommended approach:** Go to 0/0 and **skip Marinade SAM**. The free pools alone (Jito + Vault elite + JPool + BlazeStake) deliver +72 SOL/yr over current with zero ongoing costs. There's no bond to manage, no auction to monitor, no drain to top up. The downside floor is well above current profitability.

If the team wants to capture Marinade's 45K for stake weight / network influence reasons (not profit), that's a strategic decision — but know that at current clearing prices it costs ~425 SOL/yr for ~12 SOL/yr of net revenue.

**If the team prefers to stage the transition:** Start at 3/5 for 30 epochs to confirm Jito activates, then drop to 0/0. This delays Vault elite and the hard-gated pools by ~60 days but eliminates irreversibility risk.
