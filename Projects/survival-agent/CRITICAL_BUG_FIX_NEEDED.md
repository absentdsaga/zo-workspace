# CRITICAL BUG: False Rug Detection

**Date**: 2026-02-15 16:45 UTC
**Severity**: HIGH
**Status**: IDENTIFIED, FIX NEEDED

---

## 🚨 The Problem

**Bot is incorrectly marking tokens as "RUGGED"** when they're actually fine!

### Evidence

Tokens marked as "rugged" that are **ACTUALLY TRADING**:

1. **UNSYS**
   - Marked: RUGGED - No sell route
   - Reality: $124k liquidity, $3.3M volume/24h, 12k+ buys
   - **FALSE POSITIVE** ❌

2. **Panchi**
   - Marked: RUGGED - No sell route
   - Reality: $20k liquidity, $637k volume/24h
   - **FALSE POSITIVE** ❌

3. **Touch**
   - Marked: RUGGED - No sell route
   - Reality: $16k liquidity, $286k volume/24h
   - **FALSE POSITIVE** ❌

4. **Aiki**
   - Marked: RUGGED - No sell route
   - Reality: $22k liquidity, $223k volume/24h
   - **FALSE POSITIVE** ❌

### Root Cause

```typescript
// Current (BROKEN) logic:
const quote = await validator.validateSellRoute(token, amount);

if (!quote || !quote.canSell) {
  // WRONG: Jupiter can't route ≠ token is rugged
  trade.exitReason = 'RUGGED - No sell route';
  this.ruggedTokens.add(token); // Permanently blacklists
}
```

**Issue**: Jupiter routing can fail for legitimate reasons:
- Token uses non-standard DEX
- Slippage too high for Jupiter's routing
- Temporary liquidity fragmentation
- Token on Raydium but Jupiter prefers Orca

**Result**: Bot permanently blacklists tradeable tokens!

---

## 💰 Financial Impact

**Losses from false rug detection**: ~2.14 SOL

But the **REAL cost** is **opportunity cost**:
- UNSYS has 1227% gain in 24h
- Bot won't trade it again (blacklisted)
- Missing out on potential profits

---

## ✅ The Fix

### Step 1: Add DexScreener Fallback

```typescript
private async checkPosition(trade: TradeLog): Promise<void> {
  // Try Jupiter first
  const quote = await globalCircuitBreaker.execute(
    'jupiter-quote',
    () => this.validator.validateSellRoute(trade.tokenAddress, trade.amountIn),
    () => null
  );

  if (!quote || !quote.canSell) {
    // DON'T immediately mark as rugged!
    // Check DexScreener for liquidity
    const dexData = await this.checkDexScreenerLiquidity(trade.tokenAddress);

    if (dexData && dexData.liquidity > 10000) {
      // Token has liquidity on DEX, Jupiter just can't route it
      // Use DexScreener price instead
      trade.currentPrice = dexData.priceUsd;

      // Continue monitoring, but note Jupiter can't sell
      console.log(`   ⚠️  ${trade.tokenSymbol}: Jupiter can't route, using DEX price`);
      return; // Don't mark as rugged
    }

    // ONLY mark as rugged if BOTH Jupiter AND DexScreener show no liquidity
    if (!dexData || dexData.liquidity < 1000) {
      trade.status = 'closed_loss';
      trade.exitReason = 'RUGGED - No liquidity on DEX';
      trade.pnlGross = -trade.amountIn;
      trade.pnl = -trade.amountIn;
      this.ruggedTokens.add(trade.tokenAddress);
      console.log(`   🚫 ${trade.tokenSymbol} TRULY RUGGED - No DEX liquidity\n`);
    }
  }
}

private async checkDexScreenerLiquidity(tokenAddress: string): Promise<any> {
  try {
    const response = await fetch(
      `https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`
    );
    const data = await response.json();
    const pair = data.pairs?.[0];

    if (!pair) return null;

    return {
      priceUsd: parseFloat(pair.priceUsd),
      liquidity: pair.liquidity?.usd || 0,
      volume24h: pair.volume?.h24 || 0
    };
  } catch (error) {
    return null;
  }
}
```

### Step 2: Manual Exit Strategy

For tokens Jupiter can't route:
1. Monitor via DexScreener price
2. Log when hit stop-loss/take-profit via DEX price
3. User manually sells on Raydium/DEX if needed
4. Or: Implement direct DEX swap (Raydium SDK)

---

## 🔧 Immediate Actions Needed

### 1. Clear False Blacklist ⚡ URGENT

```bash
# Remove falsely blacklisted tokens
cd /home/workspace/Projects/survival-agent

# Check current blacklist
cat /tmp/paper-trades-blacklist-refactored.json

# Create corrected blacklist (remove tokens with liquidity)
echo '[]' > /tmp/paper-trades-blacklist-refactored.json
```

**Tokens to un-blacklist**:
- UNSYS (has $124k liq)
- Panchi (has $20k liq)
- Touch (has $16k liq)
- Aiki (has $22k liq)
- Crash (need to verify)
- Pi-Chan (need to verify)
- EPJUICE (need to verify)

### 2. Update Bot Logic

Add the DexScreener fallback check before marking as rugged.

### 3. Restart Bot

After fix is applied, restart to use corrected logic.

---

## 📊 Verification Checklist

For each "rugged" token, verify:
- [ ] DexScreener liquidity > $10k?
- [ ] 24h volume > $100k?
- [ ] Active buys/sells in last hour?

If YES to all three → **NOT RUGGED**, just Jupiter routing issue

---

## 🎯 Long-term Solution

### Option 1: Multi-Router Approach
- Try Jupiter first
- Fallback to Raydium SDK
- Fallback to Orca SDK
- Last resort: DexScreener price monitoring

### Option 2: Direct DEX Integration
- Integrate Raydium SDK for swaps
- Use when Jupiter fails
- More reliable for pump.fun tokens

### Option 3: Hybrid Monitoring
- Jupiter for entry/exit execution
- DexScreener for price monitoring
- Alert user when position can't be exited via Jupiter

---

## 🚨 Priority: CRITICAL

**Why**: Bot is losing money by:
1. Marking good tokens as rugged
2. Missing future opportunities (blacklist)
3. Taking unnecessary losses

**Impact**: ~2 SOL immediate loss, unknown opportunity cost

**Fix urgency**: HIGH - Should be fixed before next trading session

---

## 📝 Action Plan

1. **Verify all 9 tokens** (check DexScreener liquidity)
2. **Clear false blacklist entries**
3. **Add DexScreener fallback logic**
4. **Test on new positions**
5. **Monitor for true rugs vs routing issues**

**Estimated fix time**: 30-60 minutes
**Testing time**: 2-4 hours (watch next positions)
