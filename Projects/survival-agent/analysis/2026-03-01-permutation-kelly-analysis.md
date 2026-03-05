# Survival-Agent: Permutation Test + Kelly Analysis
**Date:** 2026-03-01  
**Datasets:** Feb 15 archive (288 closed trades), Recent paper (20), Mainnet (16)

---

## Key Findings

### 1. The Edge IS Real (Feb 15 data)
- **Sign-flip test p-value: 0.0107** (significant at α=0.05)
- Z-score: 2.27 — your win rate + win magnitude beat random chance
- Profit factor: 1.60 | Win rate: 38.9% | Avg win: +68.4% | Avg loss: -28.3%
- This is a statistically validated edge over 288 trades

### 2. Confidence Scoring is USELESS
- Correlation between confidence score and PnL: 0.014 (p=0.82)
- Low-confidence trades actually outperformed high-confidence trades
- The 45-100 scoring system adds zero predictive value
- **Action: either rebuild the scoring model or remove the filter entirely**

### 3. You're Over-Betting (12% → 6.8%)
- Classic Kelly: 13.6% | Half-Kelly: **6.8%** | Quarter-Kelly: 3.4%
- Bootstrap 95% CI: [3.6%, 22.6%]
- Current 12% is nearly full Kelly — too aggressive for a volatile meme coin strategy
- **Sizing down to 6.8% reduces ruin risk while preserving ~75% of growth rate**

### 4. Recent Performance Has Collapsed
| Dataset | Trades | Win% | Total PnL | Kelly | Edge Real? |
|---|---|---|---|---|---|
| Feb 15 archive | 288 | 38.9% | +3.13 SOL | +13.6% | YES (p=0.01) |
| Recent paper | 20 | 30.0% | -0.02 SOL | -16.0% | NO (p=0.57) |
| Mainnet | 16 | 6.2% | -0.06 SOL | -72.4% | NO (p=0.99) |

Both recent datasets show **negative Kelly** — the strategy currently has negative expected value.

### 5. Trailing Stops Are the Profit Engine
| Exit Reason | Count | Win% | Total PnL |
|---|---|---|---|
| Trailing stop | 69 | 92.8% | +7.38 SOL |
| Max hold time | 48 | 54.2% | +0.38 SOL |
| Stop loss | 170 | 12.9% | -4.59 SOL |

Almost all profit comes from trailing stop exits. Stop losses are the cost of doing business (170 trades, -4.59 SOL). The strategy works when it catches runners.

---

## Recommendations

1. **DO NOT go back to mainnet** until the edge is re-validated on paper
2. **Reduce position size** from 12% to 6.8% (half-Kelly)
3. **Rebuild or remove confidence scoring** — it's random noise
4. **Investigate the degradation** — what changed between Feb 15 (profitable) and now (losing)?
   - Market regime change? Pump.fun meta shift?
   - Code changes that broke signal quality?
   - DexScreener data quality issues?
5. **Run 100+ paper trades** at new sizing, then re-run this permutation test before mainnet
