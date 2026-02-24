#!/usr/local/bin/python3
"""
Deep analysis of longshot betting on Polymarket
Find the ACTUAL edge, not just "buy cheap stuff and pray"

Questions to answer:
1. What's the true win rate of different price ranges?
2. Do volatile longshots perform better than frozen ones?
3. What market characteristics predict success?
4. Is there market inefficiency we can exploit?
"""
import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

def get_resolved_markets(limit=200):
    """Get recently resolved markets to backtest"""
    try:
        resp = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "closed": "true",
                "limit": limit
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error: {e}")
    
    return []

def analyze_price_accuracy():
    """Check if Polymarket prices are actually calibrated
    i.e., do 5% bets win 5% of the time, or is there bias?
    """
    print("=" * 80)
    print("📊 PRICE CALIBRATION ANALYSIS")
    print("=" * 80)
    print("Analyzing resolved markets to check if longshots are mispriced...\n")
    
    markets = get_resolved_markets(limit=200)
    print(f"Analyzing {len(markets)} resolved markets\n")
    
    # Bucket by final price before resolution
    buckets = {
        '0-1%': {'total': 0, 'wins': 0, 'outcomes': []},
        '1-5%': {'total': 0, 'wins': 0, 'outcomes': []},
        '5-10%': {'total': 0, 'wins': 0, 'outcomes': []},
        '10-25%': {'total': 0, 'wins': 0, 'outcomes': []},
        '25-50%': {'total': 0, 'wins': 0, 'outcomes': []},
    }
    
    for market in markets:
        try:
            # Skip if not resolved
            if not market.get('resolved'):
                continue
            
            outcomes = json.loads(market.get('outcomes', '[]'))
            prices = json.loads(market.get('outcomePrices', '[]'))
            
            # Get winning outcome
            winning_outcome = market.get('winningOutcome')
            
            if not winning_outcome or not outcomes or not prices:
                continue
            
            # Check each outcome
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                won = (outcome == winning_outcome)
                
                # Categorize
                if price <= 0.01:
                    bucket = '0-1%'
                elif price <= 0.05:
                    bucket = '1-5%'
                elif price <= 0.10:
                    bucket = '5-10%'
                elif price <= 0.25:
                    bucket = '10-25%'
                elif price <= 0.50:
                    bucket = '25-50%'
                else:
                    continue
                
                buckets[bucket]['total'] += 1
                if won:
                    buckets[bucket]['wins'] += 1
                
                buckets[bucket]['outcomes'].append({
                    'price': price,
                    'won': won,
                    'question': market.get('question', '')
                })
        
        except Exception as e:
            continue
    
    # Display results
    print("Price Range | Predicted % | Actual Win % | Sample Size | Edge")
    print("-" * 80)
    
    edges = []
    
    for bucket_name, data in buckets.items():
        if data['total'] == 0:
            continue
        
        actual_win_rate = (data['wins'] / data['total']) * 100
        
        # Expected win rate (midpoint of range)
        expected_map = {
            '0-1%': 0.5,
            '1-5%': 3.0,
            '5-10%': 7.5,
            '10-25%': 17.5,
            '25-50%': 37.5
        }
        expected = expected_map[bucket_name]
        
        edge = actual_win_rate - expected
        
        edges.append({
            'bucket': bucket_name,
            'expected': expected,
            'actual': actual_win_rate,
            'edge': edge,
            'n': data['total']
        })
        
        edge_symbol = "🟢" if edge > 0 else "🔴" if edge < 0 else "⚪"
        print(f"{bucket_name:11} | {expected:11.1f}% | {actual_win_rate:12.1f}% | {data['total']:11} | {edge_symbol} {edge:+.1f}%")
    
    return edges, buckets

def analyze_market_characteristics():
    """What characteristics do winning longshots have?"""
    print("\n" + "=" * 80)
    print("🔍 WINNING LONGSHOT CHARACTERISTICS")
    print("=" * 80)
    print("What separates winning longshots from losing ones?\n")
    
    markets = get_resolved_markets(limit=200)
    
    winning_longshots = []
    losing_longshots = []
    
    for market in markets:
        try:
            if not market.get('resolved'):
                continue
            
            outcomes = json.loads(market.get('outcomes', '[]'))
            prices = json.loads(market.get('outcomePrices', '[]'))
            winning_outcome = market.get('winningOutcome')
            
            volume = float(market.get('volume', 0))
            liquidity = float(market.get('liquidity', 0))
            
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                
                # Only longshots (< 10%)
                if price > 0.10 or price <= 0:
                    continue
                
                won = (outcome == winning_outcome)
                
                data = {
                    'price': price,
                    'volume': volume,
                    'liquidity': liquidity,
                    'question': market.get('question', ''),
                    'category': market.get('category', ''),
                    'num_outcomes': len(outcomes)
                }
                
                if won:
                    winning_longshots.append(data)
                else:
                    losing_longshots.append(data)
        
        except:
            continue
    
    print(f"Winning longshots: {len(winning_longshots)}")
    print(f"Losing longshots: {len(losing_longshots)}")
    print()
    
    if not winning_longshots:
        print("Not enough data to analyze")
        return
    
    # Compare characteristics
    print("Characteristic      | Winners Avg | Losers Avg | Difference")
    print("-" * 80)
    
    # Price
    win_avg_price = sum(w['price'] for w in winning_longshots) / len(winning_longshots)
    lose_avg_price = sum(w['price'] for w in losing_longshots) / len(losing_longshots) if losing_longshots else 0
    print(f"Price               | {win_avg_price*100:11.2f}¢ | {lose_avg_price*100:10.2f}¢ | {(win_avg_price - lose_avg_price)*100:+.2f}¢")
    
    # Volume
    win_avg_vol = sum(w['volume'] for w in winning_longshots) / len(winning_longshots)
    lose_avg_vol = sum(w['volume'] for w in losing_longshots) / len(losing_longshots) if losing_longshots else 0
    print(f"Volume              | ${win_avg_vol:10,.0f} | ${lose_avg_vol:9,.0f} | ${win_avg_vol - lose_avg_vol:+,.0f}")
    
    # Liquidity
    win_avg_liq = sum(w['liquidity'] for w in winning_longshots) / len(winning_longshots)
    lose_avg_liq = sum(w['liquidity'] for w in losing_longshots) / len(losing_longshots) if losing_longshots else 0
    print(f"Liquidity           | ${win_avg_liq:10,.0f} | ${lose_avg_liq:9,.0f} | ${win_avg_liq - lose_avg_liq:+,.0f}")
    
    # Number of outcomes
    win_avg_outcomes = sum(w['num_outcomes'] for w in winning_longshots) / len(winning_longshots)
    lose_avg_outcomes = sum(w['num_outcomes'] for w in losing_longshots) / len(losing_longshots) if losing_longshots else 0
    print(f"Num Outcomes        | {win_avg_outcomes:11.1f} | {lose_avg_outcomes:10.1f} | {win_avg_outcomes - lose_avg_outcomes:+.1f}")
    
    # Category breakdown
    print("\nCategory breakdown of winners:")
    categories = defaultdict(int)
    for w in winning_longshots:
        cat = w.get('category', 'Unknown')
        categories[cat] += 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {cat}: {count}")
    
    return winning_longshots, losing_longshots

def find_edge_opportunities():
    """Based on analysis, what's the actual edge?"""
    print("\n" + "=" * 80)
    print("💡 EDGE IDENTIFICATION")
    print("=" * 80)
    
    # Get current active markets
    resp = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={
            "active": "true",
            "closed": "false",
            "limit": 200
        },
        timeout=10
    )
    
    if resp.status_code != 200:
        print("Could not fetch active markets")
        return
    
    markets = resp.json()
    
    print(f"\nScanning {len(markets)} active markets for mispriced longshots...\n")
    
    # Look for specific patterns based on our analysis
    opportunities = []
    
    for market in markets:
        try:
            question = market.get('question', '')
            volume = float(market.get('volume', 0))
            liquidity = float(market.get('liquidity', 0))
            
            outcomes = json.loads(market.get('outcomes', '[]'))
            prices = json.loads(market.get('outcomePrices', '[]'))
            
            # Check for specific edge patterns
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                
                # Only longshots
                if price > 0.10 or price <= 0:
                    continue
                
                # Pattern 1: High volume longshot (market is liquid = more efficient pricing)
                # Pattern 2: Binary market (2 outcomes only = simpler)
                # Pattern 3: Specific categories that historically outperform
                
                score = 0
                reasons = []
                
                if volume > 100000:
                    score += 1
                    reasons.append("High volume")
                
                if len(outcomes) == 2:
                    score += 1
                    reasons.append("Binary market")
                
                if liquidity > 5000:
                    score += 1
                    reasons.append("High liquidity")
                
                # Sports markets tend to be more efficient
                category = market.get('category', '').lower()
                if 'sports' in category:
                    score -= 1
                    reasons.append("Sports (efficient)")
                
                if score >= 2:
                    opportunities.append({
                        'question': question,
                        'outcome': outcome,
                        'price': price,
                        'volume': volume,
                        'score': score,
                        'reasons': reasons
                    })
        
        except:
            continue
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(opportunities)} potential opportunities\n")
    print("Top 10 by edge score:\n")
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"{i}. {opp['price']*100:.2f}¢ - {opp['outcome']}")
        print(f"   {opp['question'][:60]}")
        print(f"   Score: {opp['score']} | Reasons: {', '.join(opp['reasons'])}")
        print(f"   Volume: ${opp['volume']:,.0f}")
        print()

def main():
    print("=" * 80)
    print("🎯 POLYMARKET LONGSHOT EDGE ANALYSIS")
    print("=" * 80)
    print("Analyzing historical data to find REAL edge, not just gambling\n")
    
    # 1. Check if prices are calibrated
    edges, buckets = analyze_price_accuracy()
    
    # 2. Analyze winning vs losing longshots
    winners, losers = analyze_market_characteristics()
    
    # 3. Find current opportunities
    find_edge_opportunities()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    # Check if there's systematic mispricing
    longshot_edge = [e for e in edges if e['bucket'] in ['0-1%', '1-5%']]
    
    if longshot_edge:
        for e in longshot_edge:
            if e['edge'] > 2:  # More than 2% positive edge
                print(f"\n✅ EDGE FOUND: {e['bucket']} bets win {e['actual']:.1f}% vs expected {e['expected']:.1f}%")
                print(f"   Positive edge of {e['edge']:+.1f}% on {e['n']} samples")
            elif e['edge'] < -2:
                print(f"\n❌ NEGATIVE EDGE: {e['bucket']} bets win {e['actual']:.1f}% vs expected {e['expected']:.1f}%")
                print(f"   Losing edge of {e['edge']:+.1f}% on {e['n']} samples")
            else:
                print(f"\n⚪ NO EDGE: {e['bucket']} bets appear fairly priced")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
