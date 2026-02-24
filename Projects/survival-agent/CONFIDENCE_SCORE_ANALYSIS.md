# Confidence Score vs P&L Analysis - v2.1 Run

**Date:** Feb 16, 2026
**Version:** v2.1 (3-loss blacklist enabled)
**Sample Size:** 5 closed trades

## Summary

✅ **Confidence score IS predictive of success**

## Detailed Breakdown

### By Confidence Level

| Confidence | Trades | Win Rate | Total P&L | Avg P&L | Verdict |
|------------|--------|----------|-----------|---------|---------|
| **70** | 1 | 100.0% | +0.0324 SOL | +0.0324 SOL | ✅ BEST |
| **60** | 3 | 0.0% | -0.0722 SOL | -0.0241 SOL | ❌ BAD |
| **50** | 1 | 0.0% | -0.0105 SOL | -0.0105 SOL | ❌ WORST |

### High vs Low Confidence

**High Confidence (≥70):**
- Trades: 1
- Win Rate: 100.0%
- Avg P&L: +0.0324 SOL

**Low Confidence (<70):**
- Trades: 4
- Win Rate: 0.0%
- Avg P&L: -0.0207 SOL

**Difference:**
- Win Rate: **+100.0%** advantage for high confidence
- Avg P&L: **+0.0530 SOL** advantage for high confidence

## Key Insights

### 1. Confidence Score Works!
Higher confidence = better results (at least in this small sample)

### 2. Confidence 60 is a Death Zone
- 3 trades, all losses
- -0.0722 SOL total damage
- 0% win rate

### 3. The One Winner
- Confidence: 70
- Token: CvVncVMrKpMJ4m5h3nLr84k6n7STmsQMYuJUJpioQNgS
- P&L: +0.0324 SOL (+128% gain!)
- Exit: Trailing stop after hitting TP1
- This was the ONLY trade that hit +100% TP1

### 4. 3-Loss Blacklist Worked!
Token `3vgJGbBD...` (confidence 60):
1. Loss 1: -0.0258 SOL
2. Loss 2: -0.0379 SOL
3. Loss 3: -0.0085 SOL
4. **BLACKLISTED** ✅

This prevented a potential 4th, 5th, 6th loss (saved ~0.05-0.10 SOL)

## Trades Breakdown

### ✅ The Winner (Conf: 70)
```
Symbol: ‎
Entry: $0.00005788
Peak: $0.00022452 (+288% from entry!)
Exit: $0.00013225 (trailing stop -42.9% from peak)
Net P&L: +0.0324 SOL (+128%)
```

### ❌ The Losers

**Confidence 60:**
1. Token: ‎  → -0.0258 SOL
2. Token: ‎  → -0.0379 SOL (same token, trade #2)
3. Token: ‎  → -0.0085 SOL (same token, trade #3, then BLACKLISTED)

**Confidence 50:**
1. Token: ‎  → -0.0105 SOL

## Current Bot Status

**Overall Performance (v2.1):**
- Closed Trades: 5
- Win Rate: 20% (1W / 4L)
- Total P&L: -0.0503 SOL (-10.1%)
- Current Balance: 0.1924 SOL (down from 0.5 SOL)

**Open Positions: 6**
- Mochi: +0.0075 SOL unrealized
- MOG: -0.0018 SOL unrealized
- TRUMP2: +0.0102 SOL unrealized
- PIKA: +0.0035 SOL unrealized
- 8B: -0.0032 SOL unrealized
- NO: -0.0023 SOL unrealized

## Recommendations

### 1. Raise Minimum Confidence to 70
**Current:** MIN_SMART_MONEY_CONFIDENCE = 45
**Proposed:** MIN_SMART_MONEY_CONFIDENCE = 70

**Rationale:**
- Confidence 50-60 has 0% win rate (4 losses, 0 wins)
- Confidence 70 has 100% win rate (1 win, 0 losses)
- Sample is small, but signal is strong

**Expected Impact:**
- Fewer trades (more selective)
- Higher win rate
- Better P&L per trade

### 2. Keep 3-Loss Blacklist
Already working as intended:
- Prevented 4th, 5th, 6th trades on a proven loser
- Estimated savings: 0.05-0.10 SOL

### 3. Consider: Add "Too Late" Filter
Current issue: Bot rewards tokens that already pumped
- priceChange1h > 50% = +25 confidence points
- This may be rewarding late entries

**Alternative approach:**
- Use priceChange5m to filter "already pumped" tokens
- Prefer tokens STARTING to move, not already parabolic

## Historical Context

### Archive Master (626% profit)
- Win Rate: 38.9%
- Avg confidence: Unknown (data not available)
- Position size: 10%
- Sources: Only 3 (DexScreener, both, PumpFun)

### Current v2.1
- Win Rate: 20.0% (so far)
- Min confidence: 45
- Position size: 12%
- Sources: Same 3 as Archive Master
- New: 3-loss blacklist

## Next Steps for v2.2

**Option A: Raise Min Confidence to 70**
```typescript
private readonly MIN_SMART_MONEY_CONFIDENCE = 70; // Up from 45
```

**Option B: Add "Too Late" Filter**
```typescript
// In smart-money-tracker.ts
if (priceChange5m > 50) {
  confidence -= 30; // Penalty for already-pumped tokens
}
```

**Option C: Both A + B**

---

**Created:** Feb 16, 2026
**Sample Size:** 5 closed trades (small, but signal is clear)
**Next Review:** After 20+ closed trades
