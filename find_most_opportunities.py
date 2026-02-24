#!/usr/bin/env python3
"""
Find which range has the MOST opportunities right now
"""

import json
import urllib.request
from datetime import datetime, timezone

print("🔍 FINDING RANGES WITH MOST OPPORTUNITIES")
print("=" * 80)

# Fetch markets
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

MIN_VOLUME = 50000
MIN_24HR = 1000  # Lower this to see more opportunities
MAX_DAYS = 14

# Test many ranges
ranges = {
    '1-10%': (0.01, 0.10),
    '5-15%': (0.05, 0.15),
    '10-20%': (0.10, 0.20),
    '15-25%': (0.15, 0.25),
    '20-30%': (0.20, 0.30),
    '25-35%': (0.25, 0.35),
    '30-40%': (0.30, 0.40),
    '35-45%': (0.35, 0.45),
    '40-50%': (0.40, 0.50),
    '45-55%': (0.45, 0.55),
    '50-60%': (0.50, 0.60),
    '55-65%': (0.55, 0.65),
    '60-70%': (0.60, 0.70),
    '65-75%': (0.65, 0.75),
    '70-80%': (0.70, 0.80),
    '75-85%': (0.75, 0.85),
    '80-90%': (0.80, 0.90),
    '85-95%': (0.85, 0.95),
    '90-100%': (0.90, 1.00),
}

results = {}

for range_name, (price_min, price_max) in ranges.items():
    opportunities = []
    
    for market in markets:
        try:
            outcomes = json.loads(market.get("outcomes", "[]")) if isinstance(market.get("outcomes"), str) else market.get("outcomes", [])
            prices = json.loads(market.get("outcomePrices", "[]")) if isinstance(market.get("outcomePrices"), str) else market.get("outcomePrices", [])
            
            volume = float(market.get("volume", 0))
            volume_24hr = float(market.get("volume24hr", 0))
            question = market.get("question", "")
            
            # Apply filters
            if volume < MIN_VOLUME or volume_24hr < MIN_24HR:
                continue
            
            end_date_str = market.get("endDate")
            days = None
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days = (end_date - datetime.now(timezone.utc)).days
                    if days > MAX_DAYS:
                        continue
                except:
                    pass
            
            if not outcomes or len(outcomes) < 2:
                continue
            
            # Check price range
            for i, price in enumerate(prices):
                price = float(price)
                if price_min <= price < price_max:
                    opportunities.append({
                        'question': question,
                        'outcome': outcomes[i] if i < len(outcomes) else "?",
                        'price': price,
                        'volume_24hr': volume_24hr,
                        'days': days
                    })
                    break
        except:
            continue
    
    results[range_name] = opportunities

# Sort by number of opportunities
sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)

print("\n📊 OPPORTUNITIES BY RANGE (14-day filter + $1k/day liquidity):")
print("-" * 80)
print(f"{'Range':<12} | {'Count':<6} | Status")
print("-" * 80)

for range_name, opps in sorted_results[:15]:
    count = len(opps)
    if count > 0:
        emoji = "🔥" if count >= 5 else "✅" if count >= 3 else "⚠️"
        print(f"{range_name:<12} | {count:<6} | {emoji}")

print("\n" + "=" * 80)
print("🔥 TOP 3 RANGES WITH MOST OPPORTUNITIES:")
print("=" * 80)

for i, (range_name, opps) in enumerate(sorted_results[:3], 1):
    if len(opps) == 0:
        continue
        
    print(f"\n#{i} {range_name}: {len(opps)} opportunities")
    print("-" * 80)
    
    for j, opp in enumerate(opps[:5], 1):
        days_str = f"{opp['days']}d" if opp['days'] else "?"
        print(f"   {j}. {opp['question'][:60]}...")
        print(f"      {opp['outcome']} @ {opp['price']*100:.1f}% | ${opp['volume_24hr']:,.0f}/day | {days_str}")
    
    if len(opps) > 5:
        print(f"      ... and {len(opps) - 5} more")

print("\n" + "=" * 80)
print("💡 NOW CHECK EDGES FOR TOP RANGES:")
print("=" * 80)

# Load edge data
with open('/home/workspace/Projects/polymarket-bot/price_calibration.json', 'r') as f:
    calib = json.load(f)

print("\nEdge analysis for ranges with opportunities:")
print("-" * 80)

for range_name, opps in sorted_results[:5]:
    if len(opps) == 0:
        continue
    
    # Map to calibration data
    # This is approximate - calibration uses different bucket names
    edge_key = None
    if '1-10' in range_name or '5-15' in range_name:
        edge_key = '5-10%'
    elif '10-20' in range_name or '15-25' in range_name:
        edge_key = '10-20%'
    elif '80-90' in range_name or '85-95' in range_name:
        edge_key = '80-90%'
    elif '90-100' in range_name:
        edge_key = '90-100%'
    
    if edge_key and edge_key in calib:
        data = calib[edge_key]
        edge = data['edge']
        emoji = "✅" if edge > 5 else "⚠️" if edge > 0 else "❌"
        print(f"{range_name:<12} | {len(opps)} opps | Edge: {edge:+.1f}% {emoji}")
    else:
        print(f"{range_name:<12} | {len(opps)} opps | Edge: Unknown")

print("\n" + "=" * 80)
print("🎯 FINAL RECOMMENDATION:")
print("=" * 80)

# Find range with both opportunities AND positive edge
best_combo = None
for range_name, opps in sorted_results:
    if len(opps) < 2:
        continue
    
    # Check if it's 80-90 (has +7.4% edge)
    if '80-90' in range_name:
        best_combo = (range_name, opps, 7.4)
        break
    # Check if it's 1-10 (has negative edge)
    elif '1-10' in range_name:
        continue
    # Check if it's 90-100 (has +2.1% edge)
    elif '90-100' in range_name:
        best_combo = (range_name, opps, 2.1)
        break

if best_combo:
    range_name, opps, edge = best_combo
    print(f"\n✅ BEST OPTION: {range_name}")
    print(f"   • {len(opps)} opportunities available NOW")
    print(f"   • Edge: +{edge}%")
    print(f"   • Pass all TIER 1 filters")
    print(f"   • Can start trading immediately")
else:
    print("\n⚠️  NO IDEAL RANGE FOUND")
    print("   Consider waiting or adjusting filters")
