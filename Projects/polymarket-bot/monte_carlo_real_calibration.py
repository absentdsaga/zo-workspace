#!/usr/local/bin/python3
"""
MONTE CARLO SIMULATION - Using Real Blockchain Calibration

Tests the 30-40¢ strategy with ACTUAL win rates from blockchain data
"""
import numpy as np
import json

print("=" * 80)
print("🎲 MONTE CARLO: Real Calibration (30-40¢ Strategy)")
print("=" * 80)
print()

# Real calibration from per-market analysis
CALIBRATION = {
    '30-40%': {
        'n_markets': 96,
        'expected': 0.35,  # Market prices it at 35%
        'actual': 0.49,    # Actually wins 49% of time
        'edge': 0.14       # +14% edge
    }
}

def simulate_strategy(n_bets=100, n_sims=10000, bankroll=1000,
                     kelly_fraction=0.25, bet_cap=0.05):
    """
    Monte Carlo simulation of 30-40¢ strategy

    n_bets: number of bets per simulation
    n_sims: number of simulations
    bankroll: starting capital
    kelly_fraction: fraction of Kelly to use (0.25 = quarter Kelly)
    bet_cap: max % of bankroll per bet
    """

    print(f"⚙️  Simulation Parameters:")
    print(f"   Bets per session: {n_bets}")
    print(f"   Simulations: {n_sims:,}")
    print(f"   Starting bankroll: ${bankroll}")
    print(f"   Kelly fraction: {kelly_fraction} (quarter Kelly)")
    print(f"   Max bet: {bet_cap*100}% of bankroll")
    print()

    # Get calibration
    market_price = CALIBRATION['30-40%']['expected']
    true_prob = CALIBRATION['30-40%']['actual']

    print(f"📊 Strategy Edge:")
    print(f"   Market prices range at: {market_price*100:.0f}%")
    print(f"   Actual win rate: {true_prob*100:.1f}%")
    print(f"   Edge: +{(true_prob - market_price)*100:.1f}%")
    print()

    final_bankrolls = []

    print("🎲 Running simulations...")

    for sim in range(n_sims):
        current = bankroll

        for bet_num in range(n_bets):
            if current <= 0.01:
                break

            # Sample random price in 30-40¢ range
            price = np.random.uniform(0.30, 0.40)

            # Kelly criterion: f = (bp - q) / b
            # where b = odds, p = true probability, q = 1-p
            odds = (1 - price) / price
            kelly = (odds * true_prob - (1 - true_prob)) / odds
            kelly = max(0, kelly)

            # Bet sizing
            bet_size = current * kelly * kelly_fraction
            bet_size = min(bet_size, current * bet_cap)

            if bet_size < 0.01:
                continue

            # Simulate outcome using ACTUAL win rate
            won = np.random.random() < true_prob

            if won:
                # Win: get back bet + profit
                profit = bet_size * odds
                current += profit
            else:
                # Lose: lose the bet
                current -= bet_size

        final_bankrolls.append(current)

        if (sim + 1) % 1000 == 0:
            print(f"   Completed {sim + 1:,} simulations...")

    print()

    # Calculate statistics
    finals = np.array(final_bankrolls)

    results = {
        'mean': np.mean(finals),
        'median': np.median(finals),
        'std': np.std(finals),
        'min': np.min(finals),
        'max': np.max(finals),
        'prob_profit': np.sum(finals > bankroll) / n_sims,
        'prob_double': np.sum(finals > bankroll * 2) / n_sims,
        'prob_ruin': np.sum(finals < bankroll * 0.1) / n_sims,
        'sharpe': (np.mean(finals) - bankroll) / np.std(finals) if np.std(finals) > 0 else 0,
        'p5': np.percentile(finals, 5),
        'p95': np.percentile(finals, 95),
        'expected_return': np.mean(finals) - bankroll,
        'expected_return_pct': ((np.mean(finals) / bankroll) - 1) * 100
    }

    return results, finals

# Run simulation
results, distribution = simulate_strategy(
    n_bets=100,
    n_sims=10000,
    bankroll=1000,
    kelly_fraction=0.25,
    bet_cap=0.05
)

print("=" * 80)
print("📊 RESULTS")
print("=" * 80)
print()

print(f"💰 Expected Outcomes:")
print(f"   Mean final bankroll: ${results['mean']:.2f}")
print(f"   Median final bankroll: ${results['median']:.2f}")
print(f"   Expected return: ${results['expected_return']:+.2f} ({results['expected_return_pct']:+.1f}%)")
print()

print(f"📈 Probabilities:")
print(f"   Profit (any amount): {results['prob_profit']*100:.1f}%")
print(f"   Double bankroll: {results['prob_double']*100:.1f}%")
print(f"   Lose 90%+ (ruin): {results['prob_ruin']*100:.1f}%")
print()

print(f"📊 Risk Metrics:")
print(f"   Sharpe ratio: {results['sharpe']:.2f}")
print(f"   5th percentile: ${results['p5']:.2f}")
print(f"   95th percentile: ${results['p95']:.2f}")
print(f"   Min: ${results['min']:.2f}")
print(f"   Max: ${results['max']:.2f}")
print()

# Compare to research-based simulation
print("=" * 80)
print("🔬 COMPARISON: Blockchain Data vs Research Papers")
print("=" * 80)
print()

print("Research papers (90k wallets) suggested:")
print("   20-40¢ range: +2% edge, +$20.92 expected return")
print()

print("Blockchain data (10,735 markets) shows:")
print(f"   30-40¢ range: +14% edge, ${results['expected_return']:+.2f} expected return")
print()

if results['expected_return'] > 20:
    print("✅ Blockchain data shows HIGHER expected value than research!")
else:
    print("⚠️  Blockchain data shows LOWER expected value than research")

print()

# Verdict
print("=" * 80)
print("🎯 VERDICT")
print("=" * 80)
print()

if results['prob_profit'] > 0.55 and results['sharpe'] > 0.3 and results['prob_ruin'] < 0.05:
    print("✅ STRATEGY VIABLE:")
    print(f"   - {results['prob_profit']*100:.0f}% chance of profit")
    print(f"   - Sharpe ratio {results['sharpe']:.2f} (decent risk-adjusted returns)")
    print(f"   - Only {results['prob_ruin']*100:.1f}% risk of ruin")
    print()
    print("   RECOMMENDATION: Start paper trading 30-40¢ strategy")
elif results['prob_profit'] > 0.50:
    print("⚠️  STRATEGY MARGINAL:")
    print(f"   - Only {results['prob_profit']*100:.0f}% chance of profit")
    print(f"   - Sharpe ratio {results['sharpe']:.2f}")
    print()
    print("   RECOMMENDATION: More data needed or adjust parameters")
else:
    print("❌ STRATEGY NOT VIABLE:")
    print(f"   - {results['prob_profit']*100:.0f}% chance of profit (not good enough)")
    print()
    print("   RECOMMENDATION: Do not trade this strategy")

# Save results
with open('monte_carlo_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print()
print("💾 Results saved to: monte_carlo_results.json")
print()
print("=" * 80)
