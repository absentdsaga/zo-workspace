# Winner Rotation System - Priority Queue for Opportunities

**Date:** Feb 16, 2026
**Concept:** Keep winners in rotation, push losers to back of queue

---

## The Problem We're Solving

**Current v2.1 behavior:**
```
Scan finds 13 opportunities:
[Token A, Token B, Token C, Token D, Token E, Token F, Token G, ...]

Bot picks: First 7 alphabetically/chronologically
- No preference for previous winners
- No penalty for previous losers
- Random selection from qualified pool
```

**Archive Master's secret (discovered):**
- Repeated WINNERS: OrbEye (10x, 60% WR), TRUMP2 (5x, 100% WR), HALF (10x, 60% WR)
- Total from repeating winners: +3.32 SOL (106% of profit!)

**Current v2.1's problem:**
- Repeated LOSERS: CvVncV (5x, 20% WR), 3vgJGbBD (3x, 0% WR)
- Total from repeating losers: -0.06 SOL (113% of losses!)

---

## Priority Queue Solution

### Concept: Weighted Opportunity Pool

Instead of picking first 7 from flat list, rank opportunities by:

1. **Previous success history** (boost winners)
2. **Confidence score** (base quality signal)
3. **Previous failure history** (penalize losers)

```typescript
// Priority Score Formula
priorityScore = baseConfidence + historyBonus - historyPenalty

// History Bonus (for previous winners)
if (token won before):
  historyBonus = +30 * numWins

// History Penalty (for previous losers)
if (token lost before):
  historyPenalty = +20 * numLosses

// Then sort by priorityScore descending
```

---

## Implementation Design

### Step 1: Track Token History

```typescript
interface TokenHistory {
  address: string;
  symbol: string;
  trades: number;        // Total times traded
  wins: number;          // Total wins
  losses: number;        // Total losses
  winRate: number;       // wins / trades
  totalPnl: number;      // Cumulative P&L
  lastTraded: number;    // Timestamp of last trade
}

// Store in memory (rebuild from trades on startup)
private tokenHistory: Map<string, TokenHistory> = new Map();
```

### Step 2: Calculate Priority Score

```typescript
private calculatePriorityScore(
  opp: Opportunity,
  baseConfidence: number
): { score: number; reason: string } {

  let score = baseConfidence; // Start with confidence (45-100)
  let reasons: string[] = [];

  const history = this.tokenHistory.get(opp.address);

  if (!history) {
    // New token - no bonus/penalty
    reasons.push('New token (no history)');
    return { score, reason: reasons.join(', ') };
  }

  // BOOST for previous winners
  if (history.wins > 0) {
    const winBonus = 30 * history.wins;
    score += winBonus;
    reasons.push(`+${winBonus} (${history.wins} previous wins)`);
  }

  // PENALTY for previous losers
  if (history.losses > 0) {
    const lossPenalty = 20 * history.losses;
    score -= lossPenalty;
    reasons.push(`-${lossPenalty} (${history.losses} previous losses)`);
  }

  // MEGA BOOST for high win rate tokens (3+ trades)
  if (history.trades >= 3 && history.winRate >= 0.6) {
    score += 50;
    reasons.push(`+50 (${(history.winRate * 100).toFixed(0)}% WR on ${history.trades} trades)`);
  }

  // MEGA PENALTY for consistently losing tokens
  if (history.trades >= 3 && history.winRate < 0.3) {
    score -= 50;
    reasons.push(`-50 (${(history.winRate * 100).toFixed(0)}% WR on ${history.trades} trades)`);
  }

  return { score, reason: reasons.join(', ') };
}
```

### Step 3: Sort Opportunities by Priority

```typescript
// In main scanning loop, after getting qualified opportunities

const opportunitiesWithPriority = [];

for (const opp of qualified) {
  // Skip if already holding
  const isOpen = this.trades.some(t => t.status === 'open' && t.tokenAddress === opp.address);
  if (isOpen) continue;

  // Skip if blacklisted
  if (this.ruggedTokens.has(opp.address)) continue;

  // Get confidence score
  const { confidence } = await this.smartMoneyTracker.analyzeToken(opp);

  // Skip confidence 80
  if (confidence === 80) {
    console.log(`   ⏭️  SKIPPED: ${opp.symbol} (Conf 80 - proven loser)`);
    continue;
  }

  // Skip low confidence
  if (confidence < 60) {
    console.log(`   ⏭️  SKIPPED: ${opp.symbol} (Conf ${confidence} < 60)`);
    continue;
  }

  // Calculate priority score (confidence + history bonus/penalty)
  const { score: priorityScore, reason } = this.calculatePriorityScore(opp, confidence);

  opportunitiesWithPriority.push({
    ...opp,
    baseConfidence: confidence,
    priorityScore,
    priorityReason: reason
  });
}

// SORT BY PRIORITY SCORE (highest first)
opportunitiesWithPriority.sort((a, b) => b.priorityScore - a.priorityScore);

// Take top N based on available positions
const slotsAvailable = this.MAX_CONCURRENT_POSITIONS - openPositions.length;
const topOpportunities = opportunitiesWithPriority.slice(0, slotsAvailable);

console.log(`\n📊 PRIORITY QUEUE (Top ${slotsAvailable} of ${opportunitiesWithPriority.length}):`);
for (const opp of topOpportunities) {
  console.log(`   ${opp.symbol}: Priority ${opp.priorityScore} (Conf ${opp.baseConfidence}, ${opp.priorityReason})`);
}
```

### Step 4: Update History After Each Trade

```typescript
private updateTokenHistory(trade: Trade) {
  const history = this.tokenHistory.get(trade.tokenAddress) || {
    address: trade.tokenAddress,
    symbol: trade.tokenSymbol,
    trades: 0,
    wins: 0,
    losses: 0,
    winRate: 0,
    totalPnl: 0,
    lastTraded: 0
  };

  history.trades++;
  history.totalPnl += trade.pnl || 0;
  history.lastTraded = trade.exitTimestamp || Date.now();

  if (trade.status === 'closed_profit') {
    history.wins++;
  } else if (trade.status === 'closed_loss') {
    history.losses++;
  }

  history.winRate = history.wins / history.trades;

  this.tokenHistory.set(trade.tokenAddress, history);
}

// Call this in both exit paths (rugged + normal)
```

---

## Example Scenarios

### Scenario 1: Fresh Scan with Mixed History

**Opportunities found:**
1. Token A: Conf 70, no history → Priority: 70
2. Token B: Conf 60, previously won 1x → Priority: 60 + 30 = **90**
3. Token C: Conf 80, no history → Priority: SKIP (conf 80 filter)
4. Token D: Conf 70, previously lost 1x → Priority: 70 - 20 = **50**
5. Token E: Conf 65, previously won 2x → Priority: 65 + 60 = **125**
6. Token F: Conf 60, previously lost 2x → Priority: 60 - 40 = **20**

**Sorted by priority:**
1. Token E: 125 (previous 2x winner!)
2. Token B: 90 (previous winner)
3. Token A: 70 (new, decent conf)
4. Token D: 50 (previous loser, penalized)
5. Token F: 20 (2x loser, heavily penalized)

**If 3 slots available:** Bot takes E, B, A (winners rotated to front!)

---

### Scenario 2: TRUMP2-like Repeat Winner

**Trade 1:** TRUMP2 appears (Conf 70), wins (+0.05 SOL)
- Next scan: TRUMP2 reappears (Conf 70)
- Priority: 70 + 30 = **100** (boosted to front!)

**Trade 2:** TRUMP2 wins again (+0.06 SOL)
- Next scan: TRUMP2 reappears (Conf 70)
- Priority: 70 + 60 = **130** (boosted even higher!)

**Trade 3:** TRUMP2 wins again (+0.05 SOL)
- Next scan: TRUMP2 reappears (Conf 70)
- Priority: 70 + 90 = **160** (top priority!)
- Win rate: 3/3 = 100%
- **Mega boost:** +50 for high WR
- Final priority: **210**

**Result:** TRUMP2 stays at top of queue as long as it keeps winning!

---

### Scenario 3: CvVncV-like Repeat Loser

**Trade 1:** CvVncV appears (Conf 50), loses (-0.01 SOL)
- Next scan: CvVncV reappears (Conf 70)
- Priority: 70 - 20 = **50** (pushed down!)

**Trade 2:** CvVncV loses again (-0.01 SOL)
- Next scan: CvVncV reappears (Conf 70)
- Priority: 70 - 40 = **30** (pushed further down!)

**Trade 3:** CvVncV loses again (-0.01 SOL)
- **3-loss blacklist triggers** → never traded again ✅

**Result:** Losers naturally sink to bottom of queue after each loss!

---

## Benefits of This System

### 1. Mimics Archive Master's Strategy
✅ Repeats winners (OrbEye 10x, TRUMP2 5x, HALF 10x)
✅ Deprioritizes losers (but doesn't fully skip them yet)
✅ Creates natural "milk the winners" rotation

### 2. Combines Multiple Signals
- Base quality: Confidence score (60-100)
- Proven track record: Previous wins boost priority
- Risk aversion: Previous losses lower priority
- Pattern recognition: High WR tokens get mega boost

### 3. Self-Correcting
- Winners keep appearing at top → more trades
- Losers sink to bottom → fewer trades
- After 3 losses → blacklisted → never traded
- New tokens start neutral → fair chance

### 4. Transparent
Every opportunity shows:
```
MOG: Priority 125 (Conf 70, +60 (2 previous wins))
TRUMP2: Priority 210 (Conf 70, +90 (3 previous wins), +50 (100% WR on 3 trades))
CvVncV: Priority 30 (Conf 70, -40 (2 previous losses))
```

---

## Alternative: Strict "Winners Only" Mode

**More aggressive version:**

```typescript
// OPTION: Skip ALL previous losers (not just penalize)
const previouslyLost = this.trades.some(t =>
  t.tokenAddress === opp.address &&
  t.status === 'closed_loss'
);

if (previouslyLost) {
  console.log(`   ⏭️  SKIPPED: ${opp.symbol} (Previously lost - winners only mode)`);
  continue;
}

// Only trade: new tokens OR previous winners
```

**Pros:**
- Saved 0.09 SOL in current v2.1 run
- Prevents repeat losses entirely

**Cons:**
- Archive Master's LEO won on trade 3 after losing trades 1-2
- Blocks comeback opportunities
- Less flexible

---

## Recommendation: Hybrid Approach

**Combine priority queue + hard filters:**

1. ✅ **Hard skip:** Confidence 80 (proven loser)
2. ✅ **Hard skip:** Confidence < 60 (too low)
3. ✅ **Hard skip:** Nameless tokens (sketchy)
4. ✅ **Hard skip:** Blacklisted (3+ consecutive losses)
5. ✅ **Soft penalty:** Previous losers (-20 per loss)
6. ✅ **Soft boost:** Previous winners (+30 per win)
7. ✅ **Mega boost:** High WR tokens 60%+ (+50)

**Result:** Winners naturally rotate to front, losers to back, but both get chances!

---

## Implementation Checklist

### Phase 1: Add Token History Tracking
- [ ] Create TokenHistory interface
- [ ] Add tokenHistory Map to bot class
- [ ] Rebuild history from trades on startup
- [ ] Update history after each trade close

### Phase 2: Priority Scoring
- [ ] Implement calculatePriorityScore() method
- [ ] Add history bonus/penalty logic
- [ ] Add mega boost/penalty for WR

### Phase 3: Sort by Priority
- [ ] Modify opportunity selection to use priority scores
- [ ] Sort opportunities by priorityScore descending
- [ ] Take top N based on available slots

### Phase 4: Logging
- [ ] Show priority scores in scan output
- [ ] Show priority reasons (history bonus/penalty)
- [ ] Track how often winners are re-traded

---

**Created:** Feb 16, 2026
**Status:** Design ready for implementation
**Next:** Implement in v2.2 alongside other filters
