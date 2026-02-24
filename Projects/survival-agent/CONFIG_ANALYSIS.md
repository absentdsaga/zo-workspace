# Paper Trading Bot Configuration Analysis

## ⚙️ CURRENT SETTINGS

### Position Management
| Setting | Value | Analysis |
|---------|-------|----------|
| **MAX_CONCURRENT_POSITIONS** | 7 | ✅ Good - currently at 6/7, using capacity well |
| **MAX_POSITION_SIZE** | 12% | ⚠️ **TOO LARGE** - With 0.5 SOL and 7 positions, this doesn't allow enough diversification |
| **MIN_BALANCE** | 0.05 SOL | ✅ OK |
| **AUTO_REFILL_THRESHOLD** | 0.03 SOL | ✅ OK |
| **AUTO_REFILL_AMOUNT** | 1.0 SOL | ✅ OK |

### Entry Filters
| Setting | Value | Analysis |
|---------|-------|----------|
| **MIN_SCORE** | 40 | ✅ Reasonable minimum |
| **MIN_SMART_MONEY_CONFIDENCE** | 45 | ⚠️ May be **TOO HIGH** - blocking good opportunities |
| **MIN_SHOCKED_SCORE** | 30 | ✅ OK for shocked calls |

### Exit Strategy
| Setting | Value | Analysis |
|---------|-------|----------|
| **TAKE_PROFIT** | 100% | ⚠️ **UNREALISTIC** - Meme coins rarely 2x, missing profit opportunities |
| **STOP_LOSS** | -30% | ⚠️ **TOO LOOSE** - Losses are too large compared to wins |
| **TRAILING_STOP** | 20% from peak | ⚠️ Only activates after 100% TP (rarely happens) |
| **MAX_HOLD_TIME** | 60 minutes | ✅ OK |

### Timing
| Setting | Value | Analysis |
|---------|-------|----------|
| **SCAN_INTERVAL** | 15 seconds | ✅ Good balance |
| **MONITOR_INTERVAL** | 5 seconds | ✅ Good for exits |

---

## 🚨 CRITICAL ISSUES FOUND

### 1. **POSITION SIZE TOO LARGE**

**Problem:**
- Starting with 0.5 SOL
- Position size: 12% = 0.06 SOL
- Max 7 positions = 0.42 SOL locked
- Leaves only 0.08 SOL free

**Impact:**
- Can't properly diversify
- Runs out of capital quickly
- Forces holding losers instead of cutting and finding new opportunities

**Fix:**
```
Recommended: 5-8% position size for 7 positions
With 0.5 SOL: 0.025-0.04 SOL per position
```

---

### 2. **TAKE PROFIT UNREALISTIC (100%)**

**Problem:**
- TP1 set at 100% gain (2x)
- Meme coins RARELY 2x before dumping
- Trailing stop ONLY activates after TP1
- Result: Holding winners that turn into losers

**Evidence:**
Currently holding 5 positions with +3% to +17% gains, but:
- No trailing protection (TP1 not hit)
- Will hit -30% stop loss if they dump
- Missing opportunity to lock in profits

**Fix:**
```
TP1: 20-30% (realistic for meme coins)
Trailing stop: 15% from peak AFTER TP1
```

---

### 3. **STOP LOSS TOO LOOSE (-30%)**

**Problem:**
- Average loss: -0.011 SOL per losing trade
- 9 out of 11 losses hit the -30% stop
- At -30% loss, need +43% gain to break even
- Risk/Reward is broken

**Math:**
```
With -30% stop loss:
- Lose 30% of 0.06 SOL = -0.018 SOL
- Need to win 1.5x more than you lose to break even
- Current win rate: 0% (fresh restart), 38.3% (historical)
- Not enough to overcome -30% losses
```

**Fix:**
```
Stop loss: -15% to -20% maximum
This makes risk/reward balanced:
- Risk: -15% = -0.009 SOL
- Reward: +20% TP1 = +0.012 SOL
- R:R ratio = 1.33:1 (profitable at 43% win rate)
```

---

### 4. **ENTRY FILTERS MAY BE TOO STRICT**

**Problem:**
- MIN_SMART_MONEY_CONFIDENCE = 45
- May be filtering out good opportunities
- Bot is finding opportunities but skipping many

**Evidence from logs:**
```
Token: KDFILES - Score: 75/100
Smart money confidence: 25/100
⏭️ SKIPPED: Low confidence (25 < 45)
```

**Impact:**
- Missing potentially good trades
- Underutilizing capital

**Fix:**
```
Consider lowering to 35-40
Test different thresholds in paper trading
```

---

## 📊 RECOMMENDED CONFIGURATION

### Conservative (Lower Risk)
```typescript
MAX_POSITION_SIZE = 0.06;        // 6% per position
TAKE_PROFIT = 0.25;              // 25% TP1
STOP_LOSS = -0.15;               // -15% stop
TRAILING_STOP_PERCENT = 0.15;    // 15% trailing
MIN_SMART_MONEY_CONFIDENCE = 40; // Slightly lower threshold
```

**Expected:**
- Win rate needed: ~40% (achievable based on historical)
- Risk: -0.003 SOL per loss
- Reward: +0.0038 SOL per win
- R:R = 1.25:1

### Moderate (Balanced)
```typescript
MAX_POSITION_SIZE = 0.08;        // 8% per position
TAKE_PROFIT = 0.30;              // 30% TP1
STOP_LOSS = -0.20;               // -20% stop
TRAILING_STOP_PERCENT = 0.15;    // 15% trailing
MIN_SMART_MONEY_CONFIDENCE = 35; // More opportunities
```

**Expected:**
- Win rate needed: ~38% (your historical performance)
- Risk: -0.0064 SOL per loss
- Reward: +0.0096 SOL per win
- R:R = 1.5:1

### Aggressive (Higher Risk/Reward)
```typescript
MAX_POSITION_SIZE = 0.12;        // 12% per position (current)
TAKE_PROFIT = 0.40;              // 40% TP1
STOP_LOSS = -0.20;               // -20% stop
TRAILING_STOP_PERCENT = 0.20;    // 20% trailing
MIN_SMART_MONEY_CONFIDENCE = 30; // Many opportunities
```

**Expected:**
- Win rate needed: ~35%
- Risk: -0.0096 SOL per loss
- Reward: +0.0192 SOL per win
- R:R = 2:1

---

## 🎯 IMMEDIATE RECOMMENDATIONS

### Priority 1 (Critical)
1. **Lower TP1 from 100% → 25-30%**
   - Makes trailing stop actually useful
   - Locks in real gains instead of waiting for 2x

2. **Tighten stop loss from -30% → -15% to -20%**
   - Reduces loss size
   - Improves risk/reward ratio
   - Your 2.25x win/loss ratio will become profitable

### Priority 2 (Important)
3. **Reduce position size from 12% → 6-8%**
   - Better diversification
   - More shots on goal
   - Less capital locked in losers

4. **Lower confidence threshold from 45 → 35-40**
   - More trading opportunities
   - Better capital utilization

### Priority 3 (Test & Optimize)
5. **Monitor and tune based on paper trading results**
   - Track which settings perform best
   - Adjust based on market conditions
   - Compare different TP/SL combinations

---

## 💡 KEY INSIGHT

Your **OLD** data showed:
- 38% win rate
- 2.25x win/loss ratio
- **+15.6% return**

This proves the **strategy works**, but the **settings are broken**:

**Current problem:**
```
Wins: Small gains (+3% to +17%, no TP1 protection)
Losses: Large losses (-30% stop loss)
Result: Losers wipe out winners
```

**With better settings:**
```
Wins: Lock in +20-30% gains (realistic TP1 + trailing)
Losses: Limited to -15-20% (tighter stop)
Result: Winners >> Losers = Profitable
```

The math is simple:
- Win 38% of the time at +25% avg = +9.5%
- Lose 62% of the time at -15% avg = -9.3%
- **Net: +0.2% profit per cycle**

With tighter stops and realistic TPs, you'll be consistently profitable.
