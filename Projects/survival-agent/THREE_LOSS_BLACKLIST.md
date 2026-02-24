# Three-Loss Blacklist Feature

## Feature Overview

**New Rule**: If a token loses 3 times in a row, it gets automatically blacklisted and will never be traded again.

## Implementation Details

### Location
- **File**: `/home/workspace/Projects/survival-agent/testing/paper-trade-bot.ts`
- **Method**: `checkAndBlacklistLosers(tokenAddress: string)`

### How It Works

1. **After Every Trade Close** (loss or profit):
   - If the trade closed as a loss, the system checks the token's history
   - Gets all closed trades for that token, sorted by most recent first
   - Checks if the 3 most recent trades are ALL losses

2. **If 3 Consecutive Losses Found**:
   - Token is added to the blacklist
   - Blacklist is saved to `/tmp/paper-trades-blacklist.json`
   - Console message shows:
     ```
     🚫 BLACKLISTING TRUMP2 (BySPuRz3gNh4WYWWH8KxFzKcEc73YuubHKMPzHrppump)
        Reason: 3 consecutive losses (-0.1150 SOL)
        This token will no longer be traded
     ```

3. **Blacklist Enforcement**:
   - Scanner checks blacklist before entering any new trade
   - If token is blacklisted, it's skipped with message:
     ```
     🚫 SKIPPED: TRUMP2 is blacklisted (previously rugged)
     ```

### Example Scenario

**TRUMP2 Token History:**
1. Trade 1: -0.0384 SOL (loss)
2. Trade 2: -0.0382 SOL (loss)
3. Trade 3: -0.0384 SOL (loss) ← **BLACKLISTED after this**
4. Future scans: TRUMP2 appears as opportunity → **SKIPPED** ✅

**Total saved**: 3+ more potential losses

## Why This Helps

### Problem Solved
In previous runs, TRUMP2 lost 6 times in a row, costing -0.115 SOL (23% of total losses). The bot kept trading it because it passed all filters each time.

### Previous Behavior
- TRUMP2 appears → passes filters → trade → loss
- TRUMP2 appears again → passes filters → trade → loss
- TRUMP2 appears again → passes filters → trade → loss
- (repeats 6 times)

### New Behavior
- TRUMP2 appears → passes filters → trade → loss
- TRUMP2 appears again → passes filters → trade → loss
- TRUMP2 appears again → passes filters → trade → loss
- **TRUMP2 blacklisted**
- TRUMP2 appears again → **BLOCKED** → no trade ✅

## Blacklist Persistence

- **File**: `/tmp/paper-trades-blacklist.json`
- **Format**:
  ```json
  {
    "ruggedTokens": [
      "BySPuRz3gNh4WYWWH8KxFzKcEc73YuubHKMPzHrppump",
      "8yyBAFFfCA4fKw1Ai1SExtSf6DmVckGGDT8XgHUopump"
    ],
    "lastUpdated": 1771217175000
  }
  ```
- **Persists across bot restarts**: Blacklist survives crashes/restarts
- **Manual reset**: Delete `/tmp/paper-trades-blacklist.json` to clear

## Integration Points

The `checkAndBlacklistLosers()` method is called in 2 places:

1. **After Stop Loss Exit** (line ~690):
   ```typescript
   if (trade.status === 'closed_loss') {
     await this.checkAndBlacklistLosers(trade.tokenAddress);
   }
   ```

2. **After Rugged Token Detection** (line ~640):
   ```typescript
   // Add to blacklist
   this.ruggedTokens.add(trade.tokenAddress);
   await this.saveBlacklist();
   await this.checkAndBlacklistLosers(trade.tokenAddress);
   ```

## Expected Impact

### Conservative Estimate
- **Prevents**: 3+ additional losses per repeat-loser token
- **Example**: TRUMP2 had 6 losses total
  - First 3 losses: -0.0575 SOL (unavoidable, needed to learn)
  - Last 3 losses: -0.0575 SOL (**prevented with this feature**)
  - **Savings**: ~-0.06 SOL per bad token

### Realistic Scenario (50 trades)
- Assume 2 tokens become repeat losers
- Each loses 6 times without blacklist
- With blacklist: Stop after 3 losses each
- **Total prevention**: 6 avoided trades × ~0.019 SOL avg loss = ~0.11 SOL saved

### Win Rate Impact
- **Old**: Win rate diluted by repeat losers (TRUMP2: 0/6 = 0%)
- **New**: Bad tokens removed from sample after 3 strikes
- **Expected**: Win rate improves by 2-5% points

## Current Status

✅ **Feature Deployed**: Feb 16, 2026 04:46 AM
✅ **Bot Running**: Fresh start with 0.5 SOL
✅ **Blacklist Active**: Empty (clean slate)
✅ **Archive Master Replication**: No age filter + 3-loss blacklist

## Testing the Feature

To manually test:
1. Watch `/tmp/paper-bot.log` for consecutive losses
2. After 3rd loss, you should see:
   ```
   🚫 BLACKLISTING [SYMBOL] ([ADDRESS])
      Reason: 3 consecutive losses (-X.XXXX SOL)
   ```
3. Check `/tmp/paper-trades-blacklist.json` to confirm token added
4. Watch subsequent scans skip the blacklisted token

---

**Next Evolution**: Track win/loss streaks per token and adjust position sizing dynamically (future enhancement).
