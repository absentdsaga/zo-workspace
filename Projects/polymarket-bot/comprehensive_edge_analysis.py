#!/usr/bin/env python3
"""
COMPREHENSIVE POLYMARKET EDGE ANALYSIS
Analyzes multiple price ranges using actual calibration data
"""

import json
from collections import defaultdict

print("=" * 100)
print("🎯 COMPREHENSIVE POLYMARKET EDGE ANALYSIS")
print("=" * 100)

# Load the calibration data that has actual prices
print("\n📂 Loading price calibration data...")
with open('price_calibration.json', 'r') as f:
    calib = json.load(f)

print(f"✅ Loaded {len(calib)} calibration price points\n")

# Define ranges to analyze
ranges_to_analyze = [
    (0.01, 0.05, "1-5¢"),
    (0.05, 0.10, "5-10¢"),
    (0.10, 0.20, "10-20¢"),
    (0.20, 0.30, "20-30¢"),
    (0.30, 0.40, "30-40¢"),
    (0.40, 0.50, "40-50¢"),
]

results = {}

for price_min, price_max, range_name in ranges_to_analyze:
    # Find all markets in this range
    markets_in_range = []
    
    for price_str, data in calib.items():
        try:
            price = float(price_str)
            if price_min <= price < price_max:
                markets_in_range.append({
                    'price': price,
                    'actual_win_rate': data['actual_win_rate'],
                    'expected_win_rate': data['expected_win_rate'],
                    'sample_size': data['sample_size'],
                    'edge': data['edge']
                })
        except:
            continue
    
    if not markets_in_range:
        results[range_name] = {
            'sample_size': 0,
            'edge': 0,
            'actual_win_rate': 0,
            'expected_win_rate': 0,
            'status': 'NO_DATA'
        }
        continue
    
    # Aggregate statistics
    total_samples = sum(m['sample_size'] for m in markets_in_range)
    
    # Weight by sample size
    weighted_actual = sum(m['actual_win_rate'] * m['sample_size'] for m in markets_in_range) / total_samples
    weighted_expected = sum(m['expected_win_rate'] * m['sample_size'] for m in markets_in_range) / total_samples
    weighted_edge = weighted_actual - weighted_expected
    
    # Statistical significance (simplified)
    # Rule of thumb: need ~30 samples minimum for reliability
    reliability = "HIGH" if total_samples >= 50 else "MEDIUM" if total_samples >= 30 else "LOW"
    
    results[range_name] = {
        'sample_size': total_samples,
        'actual_win_rate': weighted_actual,
        'expected_win_rate': weighted_expected,
        'edge': weighted_edge,
        'reliability': reliability,
        'price_points': len(markets_in_range),
        'status': 'ANALYZED'
    }

# Print results
print("=" * 100)
print("📊 EDGE ANALYSIS RESULTS")
print("=" * 100)

print(f"\n{'Range':<12} | {'Samples':<8} | {'Expected':<10} | {'Actual':<10} | {'Edge':<12} | {'Reliability':<12} | Status")
print("-" * 100)

for range_name in ["1-5¢", "5-10¢", "10-20¢", "20-30¢", "30-40¢", "40-50¢"]:
    r = results[range_name]
    
    if r['status'] == 'NO_DATA':
        print(f"{range_name:<12} | {'N/A':<8} | {'N/A':<10} | {'N/A':<10} | {'N/A':<12} | {'N/A':<12} | ❌ No Data")
    else:
        edge_str = f"{r['edge']:+.1%}"
        edge_symbol = "✅" if r['edge'] > 0.05 else "⚠️" if r['edge'] > 0 else "❌"
        
        print(f"{range_name:<12} | {r['sample_size']:<8} | {r['expected_win_rate']:<10.1%} | "
              f"{r['actual_win_rate']:<10.1%} | {edge_str:<12} | {r['reliability']:<12} | {edge_symbol}")

print("\n" + "=" * 100)
print("🔍 DETAILED ANALYSIS")
print("=" * 100)

# Deep dive on each range
for range_name in ["1-5¢", "5-10¢", "10-20¢", "20-30¢", "30-40¢", "40-50¢"]:
    r = results[range_name]
    
    if r['status'] == 'NO_DATA':
        continue
    
    print(f"\n📈 {range_name} RANGE:")
    print("-" * 80)
    print(f"   Sample Size: {r['sample_size']} markets")
    print(f"   Price Points Analyzed: {r['price_points']}")
    print(f"   Expected Win Rate: {r['expected_win_rate']:.1%} (market-implied)")
    print(f"   Actual Win Rate: {r['actual_win_rate']:.1%} (realized)")
    print(f"   Edge: {r['edge']:+.1%}")
    print(f"   Reliability: {r['reliability']}")
    
    # Interpretation
    if r['edge'] > 0.10:
        print(f"   \n   🎯 STRONG EDGE DETECTED (+{r['edge']:.1%})")
        print(f"      → Markets consistently resolve higher than implied")
        print(f"      → This range appears systematically mispriced")
        if r['reliability'] == 'HIGH':
            print(f"      → ✅ High confidence (50+ samples)")
            print(f"      → RECOMMENDED for deployment")
        else:
            print(f"      → ⚠️  Limited samples - use caution")
    
    elif r['edge'] > 0.05:
        print(f"   \n   ⚠️  MODERATE EDGE (+{r['edge']:.1%})")
        print(f"      → Slight mispricing detected")
        if r['reliability'] == 'HIGH':
            print(f"      → Worth considering with proper position sizing")
        else:
            print(f"      → Sample size too small - need more data")
    
    elif r['edge'] > 0:
        print(f"   \n   ⚪ MARGINAL EDGE (+{r['edge']:.1%})")
        print(f"      → Edge exists but may not overcome fees/slippage")
        print(f"      → Not recommended for deployment")
    
    else:
        print(f"   \n   ❌ NO EDGE ({r['edge']:.1%})")
        print(f"      → Markets are efficiently priced or negative edge")
        print(f"      → AVOID this range")

print("\n" + "=" * 100)
print("💡 RECOMMENDATIONS")
print("=" * 100)

# Rank by edge (with reliability weighting)
scored_ranges = []
for range_name, r in results.items():
    if r['status'] == 'NO_DATA':
        continue
    
    # Score = edge * reliability_multiplier
    reliability_mult = 1.0 if r['reliability'] == 'HIGH' else 0.7 if r['reliability'] == 'MEDIUM' else 0.4
    score = r['edge'] * reliability_mult
    
    scored_ranges.append((range_name, r, score))

scored_ranges.sort(key=lambda x: x[2], reverse=True)

print("\n🏆 RANGES RANKED BY EDGE (Reliability-Weighted):")
print("-" * 80)

for i, (range_name, r, score) in enumerate(scored_ranges, 1):
    edge_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
    print(f"{edge_emoji} #{i} {range_name:<12} | Edge: {r['edge']:+.2%} | "
          f"Samples: {r['sample_size']:<4} | Reliability: {r['reliability']}")

# Top recommendation
if scored_ranges:
    best_range, best_stats, best_score = scored_ranges[0]
    
    print(f"\n✅ TOP RECOMMENDATION: {best_range}")
    print("-" * 80)
    print(f"   Edge: {best_stats['edge']:+.1%}")
    print(f"   Sample Size: {best_stats['sample_size']} markets")
    print(f"   Reliability: {best_stats['reliability']}")
    print(f"   Actual vs Expected: {best_stats['actual_win_rate']:.1%} vs {best_stats['expected_win_rate']:.1%}")
    
    if best_stats['edge'] > 0.10 and best_stats['reliability'] == 'HIGH':
        print(f"\n   🎯 DEPLOY IMMEDIATELY")
        print(f"      This range shows strong, reliable mispricing")
        print(f"      Use Kelly criterion with {best_stats['actual_win_rate']:.1%} win rate")
    elif best_stats['edge'] > 0.05:
        print(f"\n   ⚠️  DEPLOY WITH CAUTION")
        print(f"      Edge exists but may be marginal after costs")
        print(f"      Consider smaller position sizes")
    else:
        print(f"\n   ⚠️  WEAK EDGE")
        print(f"      May not be worth deployment costs")

print("\n" + "=" * 100)
print("📋 DEPLOYMENT CHECKLIST")
print("=" * 100)

if scored_ranges and scored_ranges[0][1]['edge'] > 0.05:
    best_range, best_stats, _ = scored_ranges[0]
    
    print(f"\nTo deploy to {best_range}:")
    print(f"  1. ✅ Update paper_bot_30_40.py price range:")
    print(f"     PRICE_MIN = {best_range.split('-')[0].replace('¢','')}")
    print(f"     PRICE_MAX = {best_range.split('-')[1].replace('¢','')}")
    print(f"  2. ✅ Update WIN_RATE:")
    print(f"     WIN_RATE = {best_stats['actual_win_rate']:.4f}")
    print(f"  3. ✅ Update EDGE:")
    print(f"     EDGE = {best_stats['edge']:.4f}")
    print(f"  4. ✅ Keep TIER 1 filters (14 days, $5k/day)")
    print(f"  5. ✅ Restart bot and monitor for 24 hours")
else:
    print("\n⚠️  NO STRONG EDGES FOUND")
    print("   Consider:")
    print("   • Waiting for better market conditions")
    print("   • Exploring event-driven strategies")
    print("   • Analyzing different data sources")

print("\n" + "=" * 100)

# Save results
with open('edge_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("💾 Results saved to edge_analysis_results.json")
print("=" * 100)
