# Saga DAO Validator — Commission Optimization Analysis
**Date:** March 15, 2026 | **Epoch:** 940 | **Current Commission:** 5% inflation / 10% MEV

## Data Sources
- Actual epoch profitability data from Trillium API (epochs 935-940)
- Pool delegation criteria from official docs (Jito, JPool, Marinade, Vault, BlazeStake, etc.)
- Live Marinade PSR auction data
- Coefficient dashboard pool memberships

## Current State
- **Active stake:** 80K SOL (41K base + 39K from 7 pools)
- **Marinade status:** SAM Target = 0, being destaked (currently 9K → 0)
- **Net income:** ~3.47 SOL/epoch (avg excl. outlier E939)
- **After Marinade loss:** ~2.88 SOL/epoch = 525 SOL/year

## The Core Math

Every 10K SOL of additional stake generates:
- 11.1 more leader slots per epoch
- 0.533 SOL/epoch in block rewards + priority fees
- = **97 SOL/year**

Every 1% of inflation commission on 80K SOL = **46.3 SOL/year**
Every 1% of MEV commission = **1.12 SOL/year** (negligible)

**Break-even:** You only need 4.8K more stake per 1% of inflation dropped.
Dropping all 5% inflation costs 231.5 SOL/year but unlocks ~95K more stake = 921.7 SOL/year.
**Net gain: ~690 SOL/year.**

## Scenario Comparison

| Scenario | Total Stake | Pools | Net/Epoch | Annual SOL | vs Current |
|---|---|---|---|---|---|
| **5/10 (after Marinade loss)** | 72K | 6 | 2.88 | 525 | baseline |
| **4/10** | 104K | 7 (+Jito) | 4.81 | 875 | **+67%** |
| **3/8** | 115K | 8 (+Jito, STKE) | 5.17 | 941 | **+79%** |
| **1/5** | 131K | 9 (+Jito, STKE, Marinade) | 5.32 | 968 | **+84%** |
| **0/10** | 147K | 9 (+Jito, STKE, Marinade) | 5.82 | 1,059 | **+102%** |
| **0/5** | 162K | 9 | 6.57 | 1,196 | **+128%** |
| **0/0** | 166K | 9 (+Vault perf pool) | 6.75 | 1,228 | **+134%** |

## Pool-by-Pool Impact

| Pool | At 5/10 | At 4/10 | At 0/0 | What unlocks it |
|---|---|---|---|---|
| Marinade | 9K→0 | 0 | 45K | 0% inflation for competitive Max APY |
| Jito | 0 | 31.7K | 31.7K | ≤4% inflation to rank above 5% validators |
| STKE | 0 | 0 | 9.6K | ≤3% inflation improves WizScore |
| BlazeStake | 500 | 500 | 4K | 0/0 required for >50K SOL validators |
| Vault | 5K | 5K | 7.5K | 0/0 unlocks performance pool tier |
| JPool | 3K | 3.5K | 5.5K | Lower commission = higher APY ranking |
| Phase | 9K | 9K | 9K | Already maxed (5% threshold) |
| dynoSOL | 8K | 8K | 8K | Already maxed (5% threshold) |
| DoubleZero | 5K | 5K | 5K | Already in via DZ multicast |
| **Edgevana** | 0 | 0 | 0 | Requires Edgevana hosting |
| **SharkPool** | 0 | 0 | 0 | University validators only |
| **JagPool** | 0 | 0 | 0 | LATAM/Singapore/S.Africa only |
| **Shinobi** | 0 | 0 | 0 | Pure vote credits, top 54 only |

## Pools You Cannot Access (Regardless of Commission)
- **Edgevana (16K/validator):** Must host on Edgevana infrastructure
- **SharkPool (20K/validator):** US/Canadian university validators only
- **JagPool (10K/validator):** Geographic restriction (LATAM/Singapore/South Africa)
- **Definity (10K/validator):** APAC region + winding down
- **Shinobi/xSHIN (18.5K/validator):** Need top-54 vote credits performance

## Revenue Breakdown at Each Level

At current 80K SOL:
- Inflation commission (5%): 1.27 SOL/epoch = 231 SOL/year
- Block rewards: 2.29 SOL/epoch = 417 SOL/year
- Priority fees: 1.97 SOL/epoch = 358 SOL/year
- MEV commission (10%): 0.06 SOL/epoch = 11 SOL/year
- Voting costs: -2.12 SOL/epoch = -386 SOL/year

At 0/0 with 166K SOL:
- Inflation commission: 0
- Block rewards: 4.77 SOL/epoch = 868 SOL/year
- Priority fees: 4.10 SOL/epoch = 746 SOL/year
- MEV commission: 0
- Voting costs: -2.12 SOL/epoch = -386 SOL/year

## Methodology Notes
- Per-slot revenue calculated from 5 non-outlier epochs (935-938, 940)
- E939 excluded from baseline (spike epoch: 11.53 SOL Jito tips vs normal ~0.35)
- Pool delegation estimates are conservative based on official criteria docs
- Leader slots scale linearly with stake (confirmed in Solana source code)
- Total active network stake: 389M SOL (Rated.network)
