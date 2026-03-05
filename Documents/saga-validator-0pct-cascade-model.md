# Saga DAO Validator — 0% Commission Cascade Model
**Date:** March 5, 2026 | **SOL Price:** ~$85

## Scenario: 0% Inflation / 8% MEV + 100K SOL Marinade Bond

### Pool-by-Pool Delegation Projection

| Pool | Current (5%/10%) | At 0%/8% + 100K Marinade | Requirement Met |
|------|-----------------|--------------------------|-----------------|
| Self/Community | ~39K | ~39K | — |
| SFDP | ~40K | ~40K | ≤5% ✅ |
| Marinade Auction | 0 | **100K** | Bond funded |
| Jito StakeNet | ~0 | **~40K** | 0% inflation ✅, ≤10% MEV ✅ |
| JIP-28 BAM | 0 | **~1K** | 0% inflation ✅, BAM ✅ |
| JPool | ~2.7K | **~6K** | 0% recommended, SVT running |
| Shinobi | ~0 | **~10K** | Performance-based, 0% skip ✅ |
| BlazeStake | 0 | **0** | Needs 0% MEV for >50K stake |
| STKESOL | 0 | **0** | Needs ~96+ Wiz Score |
| **TOTAL** | **~82K** | **~236K** | **3x increase** |

### Revenue Comparison

| Revenue Stream | Current (456 SOL/yr) | Optimized (499 SOL/yr) |
|---|---|---|
| Inflation commission | 237 SOL (5%) | 0 SOL (0%) |
| MEV commission | 23 SOL (10%) | 55 SOL (8% on 3x slots) |
| Priority fees (100%) | 124 SOL | 372 SOL (3x leader slots) |
| JIP-31 subsidy | 72 SOL | 72 SOL |
| **TOTAL** | **456 SOL** | **499 SOL** |
| **Delta** | — | **+43 SOL/yr (+$3,600)** |

### Wiz Score Impact

| Component | At 78K / 5% | At 236K / 0% | Change |
|-----------|------------|-------------|--------|
| Commission (15%) | 7.5 | 15.0 | +7.5 |
| Stake weight (15%) | ~8.5 | ~14.2 | +5.7 |
| Other | ~64.3 | ~64.3 | 0 |
| **Total** | **~80.3** | **~93.5** | **+13.2** |

### Key Insight
0% commission alone at 78K was EV- by $20K/year. But 0% + funded Marinade bond creates a cascade where Jito StakeNet (~40K), improved JPool allocation, and Shinobi stack on top of Marinade, pushing total to ~236K SOL where block rewards dominate.

### Optimal Configuration
- **Inflation:** 0%
- **MEV:** 8% (Jito default, slight ranking edge over 10%)
- **Marinade:** Fund 100K SOL bond
- **BAM:** Keep running
- **SVT:** Keep running

### Path to 300K+
At 93.5 Wiz Score, STKESOL eligibility (~96) is 2.5 points away. Fix any concentration penalty or gain a few more epochs of history → +8-12K STKESOL delegation → organic growth flywheel.
