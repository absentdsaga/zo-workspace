# 30-40¢ Strategy Implementation Plan

## 📊 STRATEGY OVERVIEW

**Based on Real Blockchain Data (10,735 resolved markets):**
- Target: Markets priced 30-40¢
- Expected win rate: 27.4% (market expects 35%)
- Edge: **WAIT - THIS IS NEGATIVE!** 🚨

## 🔴 CRITICAL ISSUE DISCOVERED

Looking at `price_calibration.json`:

```
"30-40%": {
  "expected": 35.0,
  "actual": 27.424138717773218,
  "edge": -7.575861282226781  ← NEGATIVE EDGE!
}
```

**This means:**
- When market prices something at 30-40¢, it actually wins only 27.4% of the time
- We're OVERESTIMATING by 7.6%
- The Monte Carlo used 49% win rate - **this is wrong!**

## ✅ THE ACTUAL GOLDEN RANGE

Looking at the calibration data, the **POSITIVE edges** are:

### 1. **40-50% Range** (BEST EDGE)
- Expected: 45%
- Actual: **52.9%**
- Edge: **+7.9%** ✅
- Sample size: 2,755 markets

### 2. **80-90% Range** (GOOD EDGE)
- Expected: 85%
- Actual: **92.4%**
- Edge: **+7.4%** ✅
- Sample size: 3,497 markets

### 3. **70-80% Range** (SMALL EDGE)
- Expected: 75%
- Actual: **78.1%**
- Edge: **+3.1%** ✅
- Sample size: 3,093 markets

## 📈 CORRECTED STRATEGY

### Option A: 40-50¢ Range (Moderate Risk)
**Why this works:**
- Markets systematically UNDERESTIMATE outcomes in this range
- When market says 45%, it actually happens 53% of the time
- Best balance of edge (+7.9%) and price

**Implementation:**
```python
TARGET_PRICE_MIN = 0.40
TARGET_PRICE_MAX = 0.50
EXPECTED_WIN_RATE = 0.529  # 52.9%
AVERAGE_PRICE = 0.45
EXPECTED_EDGE = 0.079  # +7.9%
```

### Option B: 80-90¢ Range (Low Risk)
**Why this works:**
- High-confidence outcomes that still have edge
- When market says 85%, it actually happens 92% of the time
- Lower risk, similar edge

**Implementation:**
```python
TARGET_PRICE_MIN = 0.80
TARGET_PRICE_MAX = 0.90
EXPECTED_WIN_RATE = 0.924  # 92.4%
AVERAGE_PRICE = 0.85
EXPECTED_EDGE = 0.074  # +7.4%
```

### Option C: Dual-Range Strategy
**Combine both ranges for diversification:**
- 60% allocation: 40-50¢ range
- 40% allocation: 80-90¢ range
- Balanced risk/reward

## 🎯 RECOMMENDED: 40-50¢ STRATEGY

### Why 40-50¢ over 80-90¢?

**Better Economics:**
- 40-50¢ range: Pay 45¢, win $1 → 122% return per win
- 80-90¢ range: Pay 85¢, win $1 → 18% return per win

**Similar Edge:**
- 40-50¢: +7.9% edge
- 80-90¢: +7.4% edge

**Math:**
```
40-50¢ Strategy:
- 52.9% × $1.00 (win) + 47.1% × -$0.45 (loss) = +$0.32 EV per bet
- Return on risk: +71% ROI

80-90¢ Strategy:
- 92.4% × $1.00 (win) + 7.6% × -$0.85 (loss) = +$0.86 EV per bet
- Return on risk: +101% ROI ← Actually better!
```

**WAIT - 80-90¢ IS BETTER!**

## 🔄 REVISED RECOMMENDATION: 80-90¢ STRATEGY

### Monte Carlo Recalculation Needed
```python
# Correct parameters:
PRICE_RANGE = (0.80, 0.90)
AVERAGE_PRICE = 0.85
WIN_RATE = 0.924
EDGE = 0.074
SAMPLE_SIZE = 3497
```

## 📋 IMPLEMENTATION STEPS

### Phase 1: Validate Strategy (1-2 hours)
1. ✅ Re-run Monte Carlo with CORRECT calibration (80-90¢ range)
2. ✅ Verify positive expected value
3. ✅ Calculate Kelly bet sizing
4. ✅ Set risk parameters

### Phase 2: Build Paper Trading Bot (2-3 hours)
1. **Market Scanner:**
   - Fetch active markets from Polymarket API
   - Filter for 80-90¢ price range
   - Check minimum volume ($50k+)
   - Verify market resolution date

2. **EV Calculator:**
   - Calculate expected value per market
   - Apply Kelly criterion (use quarter-Kelly for safety)
   - Cap max bet at 5% of bankroll

3. **Paper Trading Logger:**
   - Track all "bets" in JSON file
   - Record: market ID, price, size, timestamp
   - Calculate live P&L
   - Track win rate vs expected

4. **Position Monitor:**
   - Check market resolutions via API
   - Update P&L when markets resolve
   - Calculate running statistics

### Phase 3: Monitoring Dashboard (1-2 hours)
1. **Real-time Stats:**
   - Current bankroll
   - Open positions (count, total exposure)
   - Closed positions (win rate, avg return)
   - Expected vs actual performance

2. **Alerts:**
   - Win rate < 90% (expected 92.4%)
   - Drawdown > 15%
   - Edge degradation

3. **Visualizations:**
   - Bankroll curve over time
   - Win rate by market category
   - Price distribution of bets

## 🎲 RISK MANAGEMENT

### Kelly Criterion
```python
# Kelly formula: f = (p * b - q) / b
# Where:
#   p = win probability (0.924)
#   q = loss probability (0.076)
#   b = odds received (1/0.85 - 1 = 0.176)

kelly_fraction = (0.924 * 0.176 - 0.076) / 0.176
kelly_fraction ≈ 0.49  # 49% of bankroll!

# Use quarter-Kelly for safety:
bet_size = bankroll * 0.49 * 0.25  # ~12% per bet
```

### Safeguards
- Max bet: 5% of bankroll (conservative)
- Min volume: $50,000 (liquid markets only)
- Max open positions: 20
- Stop-loss: Pause if down 20%

## 📊 SUCCESS METRICS

### Week 1 (Paper Trading)
- Target: 20+ paper trades
- Expected win rate: 92.4% ± 5%
- Expected ROI: ~100%+ on risked capital

### Week 2-4
- Target: 100+ paper trades
- Validate edge holds across market types
- Refine bet sizing
- Test live with $100 if paper successful

## ⚠️ POTENTIAL PITFALLS

1. **Market Efficiency:** 80-90¢ markets might be "too obvious"
2. **Liquidity:** High-probability markets may have lower volume
3. **Selection Bias:** Data might not represent current market state
4. **Category Variance:** Edge might exist in specific categories only

## 🚀 NEXT ACTIONS

1. Run corrected Monte Carlo (80-90¢ range)
2. If results positive → Build paper trading bot
3. Run 1 week of paper trading
4. Analyze results vs expected
5. Decide on live trading with small capital

## 📝 NOTES

- The original 30-40¢ range has a **NEGATIVE** edge (-7.6%)
- Markets are actually well-calibrated in most ranges
- The two exploitable ranges are 40-50¢ and 80-90¢
- 80-90¢ offers better risk-adjusted returns despite lower edge
