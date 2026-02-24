# Winners vs Losers Analysis
**Paper Trading Bot - 189 Trades Total**

## 📊 Overall Stats
- **Total P&L:** -0.266 SOL (-70% from starting balance)
- **Win Rate:** 34.6% (63 wins / 119 losses)
- **Winners:** 63 trades
- **Losers:** 119 trades (+ 7 currently open)

---

## 🏆 WINNERS - Key Characteristics

### Exit Behavior (Most Important)
**Winners hold MUCH longer:**
- **Avg hold time:** 39.5 minutes
- **Hold time range:** 0.1 - 60 minutes
- **Median:** ~30 minutes

**Exit strategy breakdown:**
1. **Trailing stops (30 trades):** Best performers
   - Avg P&L: **+0.021 SOL** per trade
   - Avg hold time: 26.7 min
   - These hit +100% TP1 and got captured on pullback

2. **Max hold time (28 trades):** Slow grinders
   - Avg P&L: +0.0055 SOL per trade
   - Hold time: exactly 60 min
   - Never hit +100%, just slowly climbed

3. **"Stop loss" winners (5 trades):** Quick bounces
   - Avg P&L: +0.0009 SOL per trade
   - Hold time: ~1 min
   - Bought dip, caught bounce, got out fast

### Price Action Patterns
- **49% hit +100% TP1** (31 out of 63)
- **Avg peak gain:** +3,177% (massive outlier pumps)
- **Peak gain range:** 0% to +108,183%
- **Best winners pumped HARD early:** 100-300% gains in 5-20 min

### Entry Characteristics
- **Avg entry price:** $0.00143
- **37% were micro-caps** (< $0.0001)
- **Confidence score:** 59.8 (almost same as losers!)

### Timing Signature
Winners show immediate strength:
- 0-5 min: Some already hit +100%
- 5-20 min: Prime trailing stop capture window
- 20-60 min: Slow grinders that never dumped

---

## 💀 LOSERS - Key Characteristics

### Exit Behavior (The Killer)
**Losers die FAST:**
- **Avg hold time:** 17.3 minutes (44% shorter than winners!)
- **Hold time range:** 0.07 - 60 minutes
- **Median:** ~5 minutes

**Exit strategy breakdown:**
1. **Stop loss -30% (105 trades):** The death spiral
   - Avg P&L: -0.0088 SOL per trade
   - **87.5% of all losses**
   - Most died in 0-10 minutes

2. **Max hold time (15 trades):** Slow bleed
   - Held full 60 min but never recovered
   - Never went positive enough to matter

### Price Action Patterns
- **70% briefly went green** (peaked above entry)
- **But avg peak was only +16%** (vs +3,177% for winners!)
- **Peak gain range:** 0% to +91%
- **Never had explosive momentum** - just small bounces then -30%

### Entry Characteristics
- **Avg entry price:** $0.00233 (60% higher than winners!)
- **51% were micro-caps** (vs 37% for winners)
- **Confidence score:** 61.5 (slightly HIGHER than winners!)

### Timing Signature
Losers show weakness immediately:
- 0-1 min: Many already hit -30% stop loss
- 1-10 min: Most stop losses triggered
- 10-60 min: Slow bleed to -30% or time out

---

## 🔍 Critical Insights

### 1. **Confidence Score is USELESS**
- Winners: 59.8 confidence
- Losers: 61.5 confidence
- **Losers actually had HIGHER confidence!**
- Current filtering (45+ min confidence) catches both good and bad

### 2. **Time to -30% is the Real Signal**
- **Winners rarely hit -30% (only 5 out of 63 = 8%)**
- **Losers almost all hit -30% (105 out of 120 = 87.5%)**
- If a token drops -30%, it's almost certainly a loser
- Winners show strength immediately (don't drop that much)

### 3. **Peak Gain Magnitude Separates Them**
- Winners avg peak: **+3,177%** (explosive pumps)
- Losers avg peak: **+16%** (weak bounces)
- **200x difference in peak momentum!**

### 4. **Hold Time is Outcome, Not Predictor**
- Winners hold longer because they're winning (trailing stops)
- Losers exit faster because they hit -30% stop
- But: early exit prevents sitting in dead coins

### 5. **Entry Price Pattern**
- Winners: Lower entry price ($0.00143)
- Losers: Higher entry price ($0.00233)
- **Earlier entry = better chance of catching pump**
- Micro-caps more common in losers (51% vs 37%)

### 6. **Best Winners Share This Pattern:**
```
Entry → Immediate pump +100-300% in 5-20min → Trailing stop captures
```

### 7. **Typical Loser Pattern:**
```
Entry → Small bounce +10-20% → Drop to -30% in <10min
```

---

## 🎯 What Actually Works

### Trailing Stops (The Real Edge)
- Only 30 trades (16% of total)
- **Generated 47% of total winner P&L**
- Avg: +0.021 SOL per trade
- These are the trades that hit +100% and got properly captured

### The Problem
- **Only 16% of trades become trailing stop winners**
- **63% hit -30% stop loss immediately**
- Current entry filtering cannot distinguish them!

---

## 💡 Recommendations

### 1. **Entry Timing Matters More Than Confidence**
- Get in EARLIER (lower entry price)
- Confidence 45+ catches both winners and losers equally
- Need a different signal

### 2. **Add "Early Momentum" Filter**
- Track price action in first 1-3 minutes after entry
- If not showing +20% within 3 min → exit early
- Don't wait for -30% stop loss

### 3. **Micro-caps Are Riskier**
- 51% of losers were micro-caps
- 37% of winners were micro-caps
- Consider requiring higher confidence for < $0.0001 tokens

### 4. **The Real Edge is Speed**
- Best winners pump IMMEDIATELY (100-300% in 5-20min)
- Losers never show this explosive momentum
- Need to detect "pump speed" in real-time

### 5. **Current Exit Strategy is Good**
- Trailing stops working perfectly (30 trades = best performance)
- -30% stop loss is correct (prevents bigger losses)
- Max hold time at 60min is fine

### 6. **Source Analysis**
- All trades from dexscreener
- Need to compare against pumpfun/shocked sources
- Currently not differentiating sources

---

## 🚨 The Core Problem

**We cannot predict winners at entry time using current signals.**

- Confidence score: 59.8 (winners) vs 61.5 (losers) ❌
- Source: All dexscreener ❌
- Entry price: Slightly different but overlapping ❌

**The only reliable signals appear AFTER entry:**
- Does it pump +100% in first 10 min? ✅ (winner pattern)
- Does it drop -30% in first 10 min? ✅ (loser pattern)

**Solution:** Need faster exit on weak tokens (don't wait for -30%)
- Exit if not +20% within 3 min?
- Exit if showing -15% momentum downward?
- Need real-time momentum scoring vs waiting for -30%
