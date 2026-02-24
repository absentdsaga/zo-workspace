# Age Filter Decision: 60 min vs 1440 min (24h)

**Your Question:** Should we use 60 minutes or keep 1440 minutes (24h) for age filter?

---

## Critical Discovery

**The Archive Master run (626% profit) had NO age data!**

All trades show `ageMinutes: undefined`, which means:
- The age filter didn't actually filter anything
- All tokens passed through regardless of age
- The old broken logic `if (ageMinutes < 999 && ageMinutes > 1440)` only filtered tokens WITH KNOWN age >24h
- Since all ages were `undefined`, nothing was filtered

**This means Archive Master's success was NOT because of age filtering.**

---

## Your Current Situation

**Your recent runs DO have age data:**
- Tokens showing actual ages (6,095+ minutes in some cases)
- The broken filter was letting 4-6 day old tokens through
- This is why your win rate dropped to 26%

---

## The Question: 60 min vs 1440 min?

### Option 1: 60 Minutes (What I Implemented)
```typescript
if (ageMinutes > 60) {
  continue; // Only fresh 0-60 min launches
}
```

**Pros:**
- Focuses on VERY fresh launches
- Meme coins pump hardest in first hour
- Avoids stale/old tokens completely

**Cons:**
- May filter out tokens that pump later
- Smaller pool of opportunities
- Archive Master didn't use this (had no age filter)

**Expected impact:**
- Higher quality tokens
- Fewer trades
- Higher win rate

---

### Option 2: 1440 Minutes / 24 Hours (Your Suggestion)
```typescript
if (ageMinutes === 999 || ageMinutes > 1440) {
  continue; // Skip unknown age OR >24h old
}
```

**Pros:**
- Matches the ORIGINAL intent of the broken code
- Larger pool of opportunities
- Still filters out multi-day old tokens
- Closer to Archive Master behavior (which had no filter)

**Cons:**
- Allows tokens up to 24h old
- May include tokens past their pump phase

**Expected impact:**
- More trades
- Lower win rate than 60 min
- But more opportunities

---

## Data-Driven Analysis

**Archive Master (no age filter):**
- 295 trades
- 38.9% win rate
- +626% return

**Your current (broken filter letting 4-6 day tokens):**
- 46 trades
- 26.1% win rate
- -22% return

**Key insight:** Archive Master succeeded WITHOUT age filtering. The win rate came from:
1. Simple sources (no subagent/shocked)
2. Good confidence scoring
3. No repeat losers

---

## My Recommendation

**Use 1440 minutes (24h), NOT 60 minutes.**

**Reasoning:**
1. **Archive Master had no age filter and won +626%**
   - The success came from source quality, not age filtering

2. **60 min is too restrictive**
   - You're trying to replicate Archive Master
   - Archive had no age filter at all
   - 60 min is STRICTER than what worked

3. **1440 min is the right balance**
   - Filters out truly stale tokens (4-6 days old)
   - Keeps more opportunities (0-24h)
   - Matches original code intent
   - Still avoids the obvious trash

4. **Unknown ages (999) should be ALLOWED**
   - Archive Master had all undefined ages
   - Those won +626%
   - Don't filter unknown ages!

---

## Recommended Code

```typescript
// Filter: Skip very old tokens (>24h) if age is known
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue; // Skip tokens older than 24 hours (if age is known)
}
```

**This allows:**
- ✅ Unknown age (999) - like Archive Master
- ✅ 0-1440 min (0-24h) - fresh enough
- ❌ >1440 min - too stale

---

## Alternative: No Age Filter At All

**Most conservative option:**
```typescript
// Don't filter by age at all - replicate Archive Master exactly
// (Archive Master had undefined ages for all tokens)
```

**This would:**
- Exactly match Archive Master behavior
- Rely on confidence scoring instead of age
- Maximum opportunity pool

---

## My Final Answer

**Change the age filter to 1440 minutes (24h), not 60:**

```typescript
// Filter: Skip very old tokens (>24h) if age is known
if (ageMinutes !== 999 && ageMinutes > 1440) {
  continue;
}
```

**Why:**
1. Archive Master (626%) had NO age filtering (all undefined)
2. 60 min is TOO restrictive vs what worked
3. 1440 min filters obvious trash (4-6 day tokens) while keeping fresh opportunities
4. Unknown ages should be allowed (like Archive Master)

**The win rate problem is from subagent source (6.7% win rate, -1.59 SOL loss), NOT from age filtering.**

**Focus on removing subagent, not over-restricting age.**
