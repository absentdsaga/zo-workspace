# Critical Bugs in Refactored Bot - Awaiting Fix Approval

## What I Broke

I removed **5 critical features** during refactoring that make the bot unsafe to run:

### 1. ❌ Dynamic Check Intervals (CRITICAL FOR STOP-LOSS)
**Lines 449-458 in refactored vs 479-491 in original**

**Current (BROKEN):**
```typescript
// Fixed 4s check interval
if (now - lastCheck < 4000) {
  return;
}
```

**Should be:**
```typescript
// DYNAMIC based on risk
if (pnlPercent <= -25) {
  checkInterval = 2000;  // Near stop-loss: check every 2s
} else if (pnlPercent <= -15) {
  checkInterval = 3000;  // Getting close: 3s
} else if (trade.tp1Hit) {
  checkInterval = 3000;  // Trailing stop: 3s
} else if (pnlPercent > 50) {
  checkInterval = 5000;  // Big gains: 5s
} else {
  checkInterval = 10000; // Safe: 10s
}

if (now - lastCheck < checkInterval) {
  return;
}
```

**Impact:** Positions near -30% stop-loss checked 2x slower → Miss critical exit points

---

### 2. ❌ Last Known Price Fallback (MARKS GOOD TOKENS AS RUGGED)
**Lines 467-495 in refactored vs 538-543 in original**

**Current (BROKEN):**
```typescript
// Only 2-tier fallback
if (quote && quote.canSell) {
  currentPrice = quote.sellPrice;
} else {
  currentPrice = await this.getDexScreenerPrice(...);
}

if (!currentPrice) {
  // Mark as rugged immediately
}
```

**Should be (3-tier):**
```typescript
// Try Jupiter
if (realPrice) currentPrice = realPrice;

// FALLBACK #1: DexScreener
if (!currentPrice) {
  currentPrice = await this.getDexScreenerPrice(...);
}

// FALLBACK #2: Last known price
if (!currentPrice && trade.currentPrice > 0) {
  currentPrice = trade.currentPrice;
  console.log('Using last known price');
}

// ONLY mark as rugged if all 3 failed
```

**Impact:** API glitches mark profitable positions as rugged

---

### 3. ❌ unrealizedPnl Tracking (MISSING DATA)
**Missing from TradeLog interface and checkPosition**

**Current:** Field doesn't exist

**Should be:**
```typescript
interface TradeLog {
  // ... existing fields
  unrealizedPnl?: number; // <-- ADD THIS
}

// In checkPosition:
trade.unrealizedPnl = pnlSol; // Track it
```

**Impact:** Can't see real-time P&L per position

---

### 4. ❌ Detailed Position Logging (CAN'T SEE WHAT'S HAPPENING)
**Missing from checkPosition**

**Current:** Just "Monitoring N positions"

**Should be:**
```typescript
console.log(`   📊 ${trade.tokenSymbol} [${trade.source}]:`);
console.log(`      Entry: $${entryPrice} | Current: $${currentPrice}`);
if (trade.peakPrice > entryPrice) {
  console.log(`      Peak: $${peakPrice} (+${peakGain}%)`);
}
console.log(`      P&L: ${pnlPercent}% (${pnlSol} SOL)`);
console.log(`      Hold time: ${holdMinutes} min`);
if (trade.tp1Hit) {
  console.log(`      Status: 🔥 TRAILING STOP ACTIVE`);
}
```

**Impact:** Blind trading - can't see position details

---

### 5. ❌ Proper Exit Reason Messages (HARD TO DEBUG)
**Lines 512-535 in refactored vs 592-613 in original**

**Current:** Generic "Stop loss", "Max hold time"

**Should be:**
```typescript
exitReason = `Stop loss hit (${config.stopLoss * 100}%)`;
exitReason = `Trailing stop: ${dropPercent}% drop from peak $${peakPrice}`;
exitReason = `Max hold time (${config.maxHoldTimeMs / 60000} min)`;
```

**Impact:** Can't tell why positions were closed

---

## How I'll Fix It

**Option 1: Manual line-by-line replacement** (safer but tedious)
- Read original lines 461-660 (checkExitsWithTrailingStop)
- Manually adapt each section to refactored version
- Replace current checkPosition method

**Option 2: Copy entire working method** (faster but risky)
- Extract original's for loop body (lines 470-642)
- Remove for loop wrapper
- Replace this.CONSTANT with config.constant
- Replace entire checkPosition method

## What I Need From You

1. **Do you want me to proceed with the fix?**
2. **Which approach? (I recommend Option 1 - safer)**
3. **Do you want to review the fixed code before I restart the bot?**

I will NOT restart the bot until you explicitly approve.

---

## Why This Happened (Learning)

**Root cause:** I got overconfident during refactoring
- Focused on "improvements" (sub-agents, circuit breakers)
- Assumed I could "simplify" the exit logic
- Didn't do line-by-line comparison
- Trusted my memory instead of the code

**What I should have done:**
1. ✅ Read original line 461-660 completely
2. ✅ Copy to new file
3. ✅ Adapt ONLY what's needed (this.X → config.X)
4. ✅ Compare output side-by-side
5. ✅ Test before deploying

**Never again:**
- ❌ Don't "simplify" working code
- ❌ Don't trust memory over source
- ❌ Don't skip line-by-line verification
- ❌ Don't be confident without proof

I'm sorry. This was unacceptable.
