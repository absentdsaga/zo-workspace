#!/usr/bin/env python3
"""
Monte Carlo Simulation: 80-90¢ Strategy (CORRECTED)
Based on real blockchain data from 10,735 resolved markets
"""

import json
import random
import statistics

# Real calibration data from price_calibration.json
PRICE_MIN = 0.80
PRICE_MAX = 0.90
AVERAGE_PRICE = 0.85
WIN_RATE = 0.924  # Actual win rate from blockchain data
EDGE = 0.074  # +7.4% edge
SAMPLE_SIZE = 3497  # Markets in this range

# Simulation parameters
NUM_BETS = 100
NUM_SIMULATIONS = 10000
STARTING_BANKROLL = 1000
KELLY_FRACTION = 0.25  # Quarter Kelly for safety
MAX_BET_PCT = 0.05  # Max 5% per bet

def calculate_kelly():
    """Calculate Kelly criterion bet size"""
    # Kelly: f = (p*b - q) / b
    # b = odds received = (1/price - 1)
    b = (1 / AVERAGE_PRICE) - 1
    p = WIN_RATE
    q = 1 - WIN_RATE

    kelly = (p * b - q) / b
    return kelly

def simulate_one_session():
    """Run one complete betting session"""
    bankroll = STARTING_BANKROLL
    kelly = calculate_kelly()

    for _ in range(NUM_BETS):
        if bankroll <= 0:
            break

        # Calculate bet size using quarter-Kelly
        optimal_bet = bankroll * kelly * KELLY_FRACTION
        max_bet = bankroll * MAX_BET_PCT
        bet_size = min(optimal_bet, max_bet)

        # Random price in range
        price = random.uniform(PRICE_MIN, PRICE_MAX)

        # Place bet
        cost = bet_size * price

        # Simulate outcome
        wins = random.random() < WIN_RATE

        if wins:
            bankroll += bet_size * (1 - price)  # Profit
        else:
            bankroll -= cost  # Loss

    return bankroll

def main():
    print("=" * 80)
    print("🎲 MONTE CARLO: 80-90¢ Strategy (CORRECTED)")
    print("=" * 80)
    print()

    print("⚙️  Simulation Parameters:")
    print(f"   Bets per session: {NUM_BETS}")
    print(f"   Simulations: {NUM_SIMULATIONS:,}")
    print(f"   Starting bankroll: ${STARTING_BANKROLL}")
    print(f"   Kelly fraction: {KELLY_FRACTION} (quarter Kelly)")
    print(f"   Max bet: {MAX_BET_PCT*100}% of bankroll")
    print()

    kelly = calculate_kelly()
    print("📊 Kelly Criterion:")
    print(f"   Full Kelly: {kelly*100:.1f}% of bankroll")
    print(f"   Quarter Kelly: {kelly*KELLY_FRACTION*100:.1f}% of bankroll")
    print(f"   Capped at: {MAX_BET_PCT*100}% of bankroll")
    print()

    print("📊 Strategy Edge:")
    print(f"   Market price range: {AVERAGE_PRICE*100:.0f}¢")
    print(f"   Actual win rate: {WIN_RATE*100:.1f}%")
    print(f"   Edge: +{EDGE*100:.1f}%")
    print(f"   Sample size: {SAMPLE_SIZE:,} markets")
    print()

    # Expected value per bet
    avg_cost = AVERAGE_PRICE
    avg_win = 1.0
    avg_loss = -AVERAGE_PRICE
    ev = WIN_RATE * (avg_win - avg_cost) + (1 - WIN_RATE) * avg_loss
    roi = ev / avg_cost * 100

    print("💰 Per-Bet Economics:")
    print(f"   Average cost: {avg_cost*100:.0f}¢")
    print(f"   Win payout: $1.00")
    print(f"   Expected value: ${ev:+.4f} per $1 bet")
    print(f"   ROI: {roi:+.1f}%")
    print()

    print("🎲 Running simulations...")
    results = []
    for i in range(NUM_SIMULATIONS):
        final_bankroll = simulate_one_session()
        results.append(final_bankroll)

        if (i + 1) % 1000 == 0:
            print(f"   Completed {i+1:,} simulations...")

    print()
    print("=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    print()

    # Calculate statistics
    mean = statistics.mean(results)
    median = statistics.median(results)
    stdev = statistics.stdev(results)
    min_val = min(results)
    max_val = max(results)

    # Probabilities
    prob_profit = sum(1 for r in results if r > STARTING_BANKROLL) / len(results)
    prob_double = sum(1 for r in results if r >= STARTING_BANKROLL * 2) / len(results)
    prob_ruin = sum(1 for r in results if r <= STARTING_BANKROLL * 0.1) / len(results)

    # Risk metrics
    returns = [(r - STARTING_BANKROLL) / STARTING_BANKROLL for r in results]
    mean_return = statistics.mean(returns)
    sharpe = mean_return / statistics.stdev(returns) if statistics.stdev(returns) > 0 else 0

    results_sorted = sorted(results)
    p5 = results_sorted[int(len(results) * 0.05)]
    p95 = results_sorted[int(len(results) * 0.95)]

    print("💰 Expected Outcomes:")
    print(f"   Mean final bankroll: ${mean:.2f}")
    print(f"   Median final bankroll: ${median:.2f}")
    print(f"   Expected return: ${mean - STARTING_BANKROLL:+.2f} ({(mean/STARTING_BANKROLL - 1)*100:+.1f}%)")
    print()

    print("📈 Probabilities:")
    print(f"   Profit (any amount): {prob_profit*100:.1f}%")
    print(f"   Double bankroll: {prob_double*100:.1f}%")
    print(f"   Lose 90%+ (ruin): {prob_ruin*100:.1f}%")
    print()

    print("📊 Risk Metrics:")
    print(f"   Sharpe ratio: {sharpe:.2f}")
    print(f"   5th percentile: ${p5:.2f}")
    print(f"   95th percentile: ${p95:.2f}")
    print(f"   Min: ${min_val:.2f}")
    print(f"   Max: ${max_val:.2f}")
    print()

    print("=" * 80)
    print("🔬 COMPARISON WITH OTHER RANGES")
    print("=" * 80)
    print()

    print("30-40¢ range (from previous analysis):")
    print("   Edge: -7.6% (NEGATIVE) ❌")
    print("   Conclusion: AVOID")
    print()

    print("40-50¢ range:")
    print("   Edge: +7.9% (POSITIVE) ✅")
    print("   Win rate: 52.9%")
    print("   Alternative strategy option")
    print()

    print("80-90¢ range (THIS STRATEGY):")
    print(f"   Edge: +{EDGE*100:.1f}% (POSITIVE) ✅")
    print(f"   Win rate: {WIN_RATE*100:.1f}%")
    print(f"   Expected return: {(mean/STARTING_BANKROLL - 1)*100:+.1f}%")
    print()

    print("=" * 80)
    print("🎯 VERDICT")
    print("=" * 80)
    print()

    if prob_profit > 0.95 and sharpe > 1.0 and prob_ruin < 0.05:
        print("✅ STRATEGY HIGHLY VIABLE:")
        print(f"   - {prob_profit*100:.1f}% chance of profit")
        print(f"   - Sharpe ratio {sharpe:.2f} (excellent risk-adjusted returns)")
        print(f"   - Only {prob_ruin*100:.1f}% risk of ruin")
        print()
        print("   RECOMMENDATION: Proceed to paper trading")
    elif prob_profit > 0.80 and sharpe > 0.5:
        print("⚠️  STRATEGY VIABLE BUT RISKY:")
        print(f"   - {prob_profit*100:.1f}% chance of profit")
        print(f"   - Sharpe ratio {sharpe:.2f}")
        print(f"   - {prob_ruin*100:.1f}% risk of ruin")
        print()
        print("   RECOMMENDATION: Paper trade cautiously, consider lower Kelly fraction")
    else:
        print("❌ STRATEGY NOT VIABLE:")
        print(f"   - Only {prob_profit*100:.1f}% chance of profit")
        print(f"   - Sharpe ratio {sharpe:.2f} (poor risk-adjusted returns)")
        print(f"   - {prob_ruin*100:.1f}% risk of ruin")
        print()
        print("   RECOMMENDATION: Do not trade")

    # Save results
    output = {
        "strategy": "80-90¢ range",
        "mean": mean,
        "median": median,
        "std": stdev,
        "min": min_val,
        "max": max_val,
        "prob_profit": prob_profit,
        "prob_double": prob_double,
        "prob_ruin": prob_ruin,
        "sharpe": sharpe,
        "p5": p5,
        "p95": p95,
        "expected_return": mean - STARTING_BANKROLL,
        "expected_return_pct": (mean / STARTING_BANKROLL - 1) * 100,
        "kelly_full": kelly,
        "kelly_used": kelly * KELLY_FRACTION,
        "edge": EDGE,
        "win_rate": WIN_RATE,
        "sample_size": SAMPLE_SIZE
    }

    with open("monte_carlo_80_90_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"💾 Results saved to: monte_carlo_80_90_results.json")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
