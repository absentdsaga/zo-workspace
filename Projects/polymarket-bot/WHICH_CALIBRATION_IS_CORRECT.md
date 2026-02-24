# Which Calibration is Correct?

## The Conflict

We have TWO different calibration analyses that give **OPPOSITE** results:

### Per-TRADE Calibration (`price_calibration.json`)
- **30-40¢ range:** -7.6% edge (4,383 trades) ❌
- **80-90¢ range:** +7.4% edge (3,497 trades) ✅

### Per-MARKET Calibration (`per_market_calibration.json`)
- **30-40¢ range:** +14% edge (96 markets) ✅
- **80-90¢ range:** -0.15% edge (33 markets) ❌

## Which One Should We Trust?

### Per-MARKET is MORE CORRECT

**Why per-market is the right approach:**

1. **Avoids Double-Counting**
   - Per-trade: If 100 trades happen on the same market at 35¢, and it loses, you count 100 "failures"
   - Per-market: The same scenario counts as 1 market that was priced at 35¢ and lost
   - **Per-market treats each market as one independent event**

2. **Matches Our Trading Reality**
   - We bet on MARKETS, not individual trades
   - Each market resolves once (Yes or No)
   - Trading volume doesn't change the outcome

3. **Removes Volume Bias**
   - High-volume markets dominate per-trade statistics
   - A single popular market can skew the entire range
   - Per-market treats all markets equally

## The Problem with Per-TRADE

**Example scenario:**

Imagine two markets in the 30-40¢ range:
- Market A: Priced at 35¢, has 1,000 trades, **WINS** (resolves YES)
- Market B: Priced at 35¢, has 10 trades, **LOSES** (resolves NO)

**Per-trade analysis:**
- Total trades: 1,010
- Wins: 1,000 (99% win rate!) ✅
- Conclusion: 30-40¢ is amazing!

**Per-market analysis:**
- Total markets: 2
- Wins: 1 (50% win rate)
- Expected: 35% (would need 0.7 wins)
- Conclusion: Roughly as expected

**The truth:** High-volume markets bias the per-trade stats. The actual edge should be measured by how many MARKETS win, not how many TRADES happened on those markets.

## Sample Size Concern

**Per-market has MUCH smaller sample sizes:**
- 30-40¢: Only 96 markets (vs 4,383 trades)
- 80-90¢: Only 33 markets (vs 3,497 trades)

**Is this a problem?**

Not necessarily - it depends on what we're measuring:
- **Per-trade**: Measures "if I make a random trade, what happens?" (wrong question)
- **Per-market**: Measures "if I bet on a random market, what happens?" (RIGHT question)

**Statistical significance:**
- 30-40¢ per-market: p=0.005 (SIGNIFICANT)
- 40-50¢ per-market: p=0.041 (SIGNIFICANT)
- These ARE statistically significant despite smaller N

## Deep Dive: Why the Difference?

**Hypothesis:** High-probability outcomes (80-90¢) have:
1. Higher trading volume (more liquid, more attention)
2. More efficient pricing (volume attracts smart money)
3. Market makers keeping it calibrated

**Low-to-mid probability outcomes (30-40¢) have:**
1. Lower trading volume (less liquid)
2. Less attention from sophisticated traders
3. More room for mispricing

**This explains why:**
- Per-trade (volume-weighted): Favors high-volume (80-90¢) ranges
- Per-market (equal-weighted): Favors under-traded (30-40¢) ranges

## The Real Question: Which Analysis Matches Our Bot?

**Our bot will:**
- Select markets to bet on (not individual trades)
- Treat each market as one opportunity
- Not weight by volume (we can only bet once per market)

**Therefore: Per-MARKET analysis is correct for our use case**

## But Wait - Sample Size is Too Small!

**The concern:**
- 96 markets for 30-40¢ is borderline
- 33 markets for 80-90¢ is TOO SMALL
- Statistical significance doesn't mean practical reliability

**The solution:**
We need to validate with LIVE paper trading. The historical data can guide us, but we need real-time validation.

## Recommendation

### Option 1: Trust Per-Market Data (30-40¢ Strategy)
**Pros:**
- Theoretically correct analysis method
- +14% edge on 96 markets
- Statistically significant (p=0.005)

**Cons:**
- Small sample size (96 markets)
- Contradicts per-trade analysis
- Higher risk if wrong

**Expected outcome (Monte Carlo):**
- +606% return over 100 bets
- 99.6% chance of profit

### Option 2: Trust Per-Trade Data (80-90¢ Strategy)
**Pros:**
- Larger sample size (3,497 trades)
- More conservative approach
- Lower variance (92% win rate)

**Cons:**
- May be biased by volume
- Smaller edge (+7.4%)
- Sample size is trades, not markets

**Expected outcome (Monte Carlo):**
- +44.9% return over 100 bets
- 99.3% chance of profit

### Option 3: Compromise (40-50¢ Strategy)
**Both analyses agree this range has positive edge:**
- Per-market: +8.0% edge (164 markets, p=0.041)
- Per-trade: +7.9% edge (2,755 trades, p<0.001)

**Pros:**
- Agreement between methods
- Good sample size in both
- Moderate risk/reward

**Cons:**
- Lower edge than 30-40¢ (per-market)
- Lower edge than 80-90¢ (per-trade)

## Final Verdict

**I recommend starting with 30-40¢ strategy (per-market analysis) BECAUSE:**

1. **Theoretically sound:** Per-market is the correct way to measure
2. **Strong edge:** +14% if the data holds
3. **Statistically significant:** p=0.005
4. **Paper trading will validate quickly:** If wrong, we'll know within 20 bets
5. **Monte Carlo shows huge upside:** +606% expected return

**But use paper trading as validation:**
- If win rate < 40% after 20 bets → STOP (edge doesn't hold)
- If win rate 40-50% → CONTINUE (edge confirmed)
- If win rate > 50% → SCALE UP (edge is real)

**The 80-90¢ strategy is the "safe" backup:**
- If 30-40¢ fails in paper trading
- Switch to 80-90¢ (per-trade validated)
- More conservative, proven by volume

## What I Built

I built the **80-90¢ bot** because I initially trusted the per-trade data (larger sample size).

**Should I rebuild for 30-40¢?**

YES - Because:
1. Per-market is theoretically correct
2. The edge is much higher (+14% vs +7.4%)
3. Paper trading will validate quickly
4. If it fails, we fall back to 80-90¢

Let me rebuild the bot for 30-40¢ strategy.
