# Paper Trading Bot - Trailing Stop Update

## 🚀 Major Upgrade: Dual-Loop + Trailing Stop System

### What Changed (2026-02-11)

#### 1. **Dual-Loop Architecture** ⚡
**Problem:** Single 30s loop was too slow for volatile meme coins
- Missed peak prices between scans
- Late exits on dumps
- Slow reaction time

**Solution:** Separate scanner and monitor loops
- **Scanner loop**: Every 15 seconds (find new opportunities)
- **Monitor loop**: Every 5 seconds (check positions for exits)
- Both run concurrently for maximum responsiveness

#### 2. **Tiered Exit Strategy** 💎

##### Before TP1 (+100%):
```
Regular stop-loss: -30%
Max hold time: 60 minutes
```

##### After TP1 (+100%):
```
Trailing stop: 20% drop from peak
- Entry: $100
- Hits $200 (+100%) → TP1 triggered! 🎯
- Continues to $300 → Peak = $300
- Drops to $240 → SELL! (20% below peak)
- Result: +140% instead of just +100%
```

#### 3. **Peak Price Tracking** 📈
The bot now tracks:
- `entryPrice`: Where you bought
- `currentPrice`: Current market price
- `peakPrice`: Highest price seen since entry
- `tp1Hit`: Whether +100% was reached

**Display:**
```
📊 PEPE [both]:
   Entry: $0.00001000 | Current: $0.00001800
   Peak: $0.00002000 (+100.00%)
   P&L: +80.00% (+0.0032 SOL)
   Hold time: 12.5 min
   Status: 🔥 TRAILING STOP ACTIVE
```

#### 4. **Scanner Optimization**
- Reduced from 30s → 15s interval
- More opportunities caught earlier
- Still sustainable for API rate limits

#### 5. **Enhanced Logging**
Now shows:
- Scanner source for each token
- Peak price achieved
- Trailing stop status
- Drop from peak percentage

---

## Exit Logic Flow

### Scenario A: Token Never Reaches TP1
```
Entry: $100
Peak: $180 (+80%)
Drops to $70 (-30%)
→ EXIT: Regular stop-loss triggered
```

### Scenario B: Token Hits TP1, Then Dumps
```
Entry: $100
Hits $200 (+100%) → 🎯 TP1! Trailing stop activates
Continues to $250 → Peak = $250
Drops to $200 → Hold (only 20% below peak)
Drops to $200 (exactly 20% below $250)
→ EXIT: Trailing stop triggered at +100%
```

### Scenario C: Token Moons
```
Entry: $100
Hits $200 (+100%) → 🎯 TP1! Trailing stop activates
Continues to $500 → Peak = $500
Drops to $400 (20% below $500)
→ EXIT: Trailing stop triggered at +300%
```

### Scenario D: Token Rugs
```
Entry: $100
Hits $200 (+100%) → 🎯 TP1! Trailing stop activates
Continues to $300 → Peak = $300
Jupiter reports: "No sell route available"
→ EXIT: Total loss, token rugged
```

---

## Code Changes

### TradeLog Interface
```typescript
interface TradeLog {
  // ... existing fields
  peakPrice?: number;      // NEW: Highest price seen
  tp1Hit?: boolean;        // NEW: Did we hit +100%?
  source?: 'pumpfun' | 'dexscreener' | 'both'; // NEW: Scanner source
}
```

### Constants
```typescript
private readonly MAX_CONCURRENT_POSITIONS = 10;
private readonly TRAILING_STOP_PERCENT = 0.20; // NEW
private readonly SCAN_INTERVAL_MS = 15000; // Changed from 30000
private readonly MONITOR_INTERVAL_MS = 5000; // NEW
```

### Architecture
```typescript
async run() {
  await Promise.all([
    this.scannerLoop(),  // Find opportunities (15s)
    this.monitorLoop()   // Check positions (5s)
  ]);
}
```

---

## Benefits

### 1. **Catch More Runners**
- 5s monitoring catches peak prices between scans
- Lock in profits as token climbs
- Don't miss the 20% extra from peaks

### 2. **Faster Exits**
- React within 5 seconds instead of 30
- Critical for volatile meme coins
- Avoid holding through dumps

### 3. **Better Risk Management**
- Protect gains after hitting TP1
- Still use hard stop-loss before TP1
- Worst case: -30% loss
- Best case: Unlimited upside with 20% cushion

### 4. **More Data**
- Track which scanner finds best tokens
- See peak vs exit prices
- Analyze if trailing stop is optimal

---

## Example Trade Walkthrough

```
00:00 - Entry at $0.00001000 (0.04 SOL position)
        Peak: $0.00001000 | Status: Pre-TP1

00:15 - Current: $0.00001200 (+20%)
        Peak: $0.00001200 | Status: Pre-TP1

00:30 - Current: $0.00001500 (+50%)
        Peak: $0.00001500 | Status: Pre-TP1

00:45 - Current: $0.00002000 (+100%)
        Peak: $0.00002000 | Status: 🎯 TP1 HIT! TRAILING STOP ACTIVE

01:00 - Current: $0.00002800 (+180%)
        Peak: $0.00002800 | Trailing stop at $0.00002240 (20% below)

01:15 - Current: $0.00003500 (+250%)
        Peak: $0.00003500 | Trailing stop at $0.00002800 (20% below)

01:30 - Current: $0.00002800 (-20% from peak)
        EXIT: Trailing stop triggered
        Result: +180% gain (0.072 SOL profit)
```

**Without trailing stop:**
You might have:
- Sold at exactly +100% = 0.04 SOL profit
- Held to +250%, then crashed to -30% = -0.012 SOL loss

**With trailing stop:**
You got +180% = 0.072 SOL profit ✅

---

## Files Modified
- `/home/workspace/Projects/survival-agent/testing/paper-trade-master-fixed.ts`

## Testing
```bash
cd /home/workspace/Projects/survival-agent
bash start-paper-master-fixed.sh
```

## Monitoring
Watch for:
- "🎯 TP1 HIT! Trailing stop activated" messages
- Peak prices vs exit prices
- How often trailing stop triggers vs regular stop-loss
- Scanner source performance (pumpfun vs dexscreener vs both)

---

## Next Steps

After paper trading data:
1. Analyze peak vs exit prices to optimize 20% trailing percentage
2. Review scanner source performance
3. Consider adding TP2/TP3 levels with tighter trailing stops
4. Tune monitor interval (5s vs 3s vs 10s)
