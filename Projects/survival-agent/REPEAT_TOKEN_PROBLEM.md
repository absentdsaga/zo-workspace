# Why Same Tokens Keep Appearing + Always Max Positions

## The Problem

**You're seeing:**
1. Same tokens traded repeatedly (3x CvVncV..., 3x 3vgJGb...)
2. Always 7/7 positions full (max capacity)
3. Both are connected issues

---

## Root Cause Analysis

### Issue #1: Nameless Tokens Show Up As Different

**The tokens with "‎" symbol (invisible character):**
- Token 1: `3vgJGbBDaBtLkca2cyfCRusFsqYoGC8mhTMaUaxhpump` (traded 3x, all losses)
- Token 2: `CvVncVMrKpMJ4m5h3nLr84k6n7STmsQMYuJUJpioQNgS` (traded 3x, 1 win 1 loss 1 open)

**Why this happens:**
```typescript
// Current check (line 304):
.filter(opp => !this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address))
```

This ONLY checks if you have an **OPEN** position. Once closed, it can trade the same token again!

**The symbols are actually invisible Unicode characters** - DexScreener returns empty/blank symbols for some tokens, making them look like "‎" in logs.

---

### Issue #2: Why Always 7/7 Full?

**Current bot behavior:**
1. Scans every 15 seconds for new opportunities
2. If positions < 7, tries to fill slots
3. Positions take 60 minutes max to close (MAX_HOLD_TIME_MS)
4. Most positions stop out at -30% in ~5-30 minutes
5. As soon as one closes, bot fills the slot again

**Math:**
- Scan interval: 15s
- Avg time to stop loss: ~15-30 min
- New opportunities: Always available from DexScreener
- Result: **Bot constantly refills to 7/7**

**This is working as designed**, but may not be optimal.

---

## Why Repeats Happen Despite The Filter

### The Filter IS Working (for open positions)

**Line 304 in paper-trade-bot.ts:**
```typescript
const availableOpps = qualified
  .filter(opp => !this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address))
  .sort((a, b) => b.score - a.score);
```

This correctly filters out tokens you **currently hold**.

### But It Doesn't Check Closed Trades

**Missing logic:**
```typescript
// NOT IMPLEMENTED: Check if we already traded this token (win or loss)
// NOT IMPLEMENTED: Check if this token is on blacklist (until 3 losses)
```

**Result:**
- Token appears → trade → lose -30% → close position
- 15 minutes later, token still pumping on DexScreener → appears again
- Bot sees: "Not in open positions? Buy it!"
- Trade again → lose again
- Repeat until 3 losses → blacklist

---

## Current State (Your Run)

### Repeat Tokens Breakdown

**Token `3vgJGbBD...` (now blacklisted):**
1. Trade 1: -0.0258 SOL (conf 60)
2. Trade 2: -0.0379 SOL (conf 60)
3. Trade 3: -0.0085 SOL (conf 60)
4. **BLACKLISTED** ✅ (3-loss rule worked!)

**Token `CvVncV...` (still tradeable):**
1. Trade 1: -0.0105 SOL (conf 50) - LOSS
2. Trade 2: +0.0324 SOL (conf 70) - WIN!
3. Trade 3: OPEN (conf 70) - currently holding

**Why token 2 wasn't blacklisted:**
- Loss → Win → current trade is only 2 closed (not 3 consecutive losses)
- Blacklist requires 3 **consecutive losses**

---

## What Changed vs Archive Master?

### Archive Master (626% profit)
- **No repeat token data available** (files deleted)
- Possibly had similar issue but with better token selection (higher avg confidence?)
- 295 trades total, unknown how many were repeats

### Current v2.1
- **Same filter logic** (only checks open positions)
- **Added 3-loss blacklist** (prevents 4th, 5th, 6th trades on losers)
- Repeats still happen for 1st and 2nd trades on same token

---

## Solutions

### Option A: Prevent ALL Repeats (Aggressive)

```typescript
// In paper-trade-bot.ts line ~304
const availableOpps = qualified
  .filter(opp => {
    // Skip if currently holding
    const isOpen = this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address);
    // Skip if EVER traded before (win or loss)
    const everTraded = this.trades.some(t => t.tokenAddress === opp.address);
    // Skip if blacklisted
    const isBlacklisted = this.ruggedTokens.has(opp.address);

    return !isOpen && !everTraded && !isBlacklisted;
  })
  .sort((a, b) => b.score - a.score);
```

**Pros:**
- Never trade same token twice
- Cleaner data for analysis

**Cons:**
- May miss good re-entry opportunities
- Example: CvVncV lost first trade, then WON second trade (+128%!)

---

### Option B: Prevent Repeat Losers Only (Conservative)

```typescript
// Only skip tokens that previously LOST
const availableOpps = qualified
  .filter(opp => {
    const isOpen = this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address);
    const isBlacklisted = this.ruggedTokens.has(opp.address);

    // Skip if previously lost
    const previouslyLost = this.trades.some(t =>
      t.tokenAddress === opp.address &&
      t.status === 'closed_loss'
    );

    return !isOpen && !isBlacklisted && !previouslyLost;
  })
```

**Pros:**
- Allows re-entry after wins
- Prevents repeat losses after first loss (stricter than 3-loss blacklist)

**Cons:**
- Still allows trading after losing once (blacklist is at 3 losses)

---

### Option C: Keep Current (Let 3-Loss Blacklist Handle It)

**Current behavior:**
- Token can be traded up to 3 times (if all losses)
- After 3 losses → blacklist
- Allows tokens to "prove themselves" with 3 chances

**Pros:**
- Already implemented and working
- Saved ~0.05-0.10 SOL by preventing trades 4-6 on bad token

**Cons:**
- Still wastes 2 trades on proven losers (trades 2 and 3)

---

## Why Always 7/7 Positions?

### This Is By Design

**Current settings:**
```typescript
private readonly MAX_CONCURRENT_POSITIONS = 7;
private readonly SCAN_INTERVAL_MS = 15000; // 15s
```

**Bot logic:**
1. Every 15s: "Do I have < 7 positions?"
2. If yes: "Scan for opportunities and fill slots"
3. Opportunities always available (DexScreener has hundreds of tokens)
4. Result: Slots fill immediately after closures

### Is 7 Too Many?

**Archive Master (626% profit):**
- Unknown max concurrent positions
- Possibly lower (fewer concurrent = more selective?)

**Current v2.1:**
- Max 7 concurrent
- ~0.03-0.06 SOL per position
- If all 7 lose: -0.21-0.42 SOL drawdown possible

### Alternative: Reduce Max Positions

**Option:** Lower from 7 → **3-5 concurrent**

**Benefits:**
- More selective (only best opportunities)
- Lower capital at risk
- Less likely to hit max capacity
- Better risk management

**Trade-off:**
- Fewer trades total
- May miss some opportunities

---

## Recommendations

### Immediate (v2.2):
1. **Raise min confidence 45 → 70** (filters out 60% conf death zone)
2. **Keep 3-loss blacklist** (already working)
3. **Add "skip previous losers" filter** (Option B above)

### Future (v2.3):
1. **Reduce max positions 7 → 5** (more selective)
2. **Add "too late" filter** (use priceChange5m to avoid already-pumped tokens)

---

**Created:** Feb 16, 2026
**Issue:** Repeat tokens + always max positions
**Root Cause:** Filter only checks open positions, bot constantly refills slots
