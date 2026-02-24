#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

print("🌍 FULL POLYMARKET LANDSCAPE")
print("=" * 80)
print(f"Total active markets: {len(markets)}\n")

price_ranges = {
    '1-10¢': (0.01, 0.10),
    '10-20¢': (0.10, 0.20),
    '20-30¢': (0.20, 0.30),
    '30-40¢': (0.30, 0.40),
    '40-50¢': (0.40, 0.50),
    '50-60¢': (0.50, 0.60),
    '60-70¢': (0.60, 0.70),
    '70-80¢': (0.70, 0.80),
    '80-90¢': (0.80, 0.90),
    '90-99¢': (0.90, 0.99),
}

# Progressive filter counts
stage1 = {name: 0 for name in price_ranges}  # No filters
stage2 = {name: 0 for name in price_ranges}  # + $50k volume
stage3 = {name: 0 for name in price_ranges}  # + $1k/day
stage4 = {name: 0 for name in price_ranges}  # + 14 days

for market in markets:
    try:
        outcomes = json.loads(market.get("outcomes", "[]")) if isinstance(market.get("outcomes"), str) else market.get("outcomes", [])
        prices = json.loads(market.get("outcomePrices", "[]")) if isinstance(market.get("outcomePrices"), str) else market.get("outcomePrices", [])
        
        volume = float(market.get("volume", 0))
        volume_24hr = float(market.get("volume24hr", 0))
        
        end_date_str = market.get("endDate")
        days = 999
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days = (end_date - datetime.now(timezone.utc)).days
            except:
                pass
        
        if not outcomes or len(outcomes) < 2:
            continue
            
        for price in prices:
            price = float(price)
            for range_name, (min_p, max_p) in price_ranges.items():
                if min_p <= price < max_p:
                    stage1[range_name] += 1
                    if volume >= 50000:
                        stage2[range_name] += 1
                        if volume_24hr >= 1000:
                            stage3[range_name] += 1
                            if days <= 14:
                                stage4[range_name] += 1
                    break
    except:
        continue

print("Range      | Raw  | +$50k vol | +$1k/day | +14 days")
print("-" * 60)
for name in price_ranges:
    print(f"{name:<10} | {stage1[name]:>4} | {stage2[name]:>9} | {stage3[name]:>8} | {stage4[name]:>8}")

print("\n" + "=" * 80)
print(f"\nTOTALS: {sum(stage1.values())} → {sum(stage2.values())} → {sum(stage3.values())} → {sum(stage4.values())}")

print(f"\n🎯 30-40¢ RANGE:")
print(f"   Raw markets: {stage1['30-40¢']}")
print(f"   With volume: {stage2['30-40¢']}")  
print(f"   With liquidity: {stage3['30-40¢']}")
print(f"   With time filter: {stage4['30-40¢']}")

if stage3['30-40¢'] > stage4['30-40¢']:
    diff = stage3['30-40¢'] - stage4['30-40¢']
    print(f"\n   ⚠️  {diff} market(s) blocked ONLY by 14-day filter")
    print(f"   These are the long-dated markets we're avoiding for liquidity")
elif stage3['30-40¢'] == 0:
    print(f"\n   ❌ Zero markets even before time filter")
    print(f"   The range is structurally dead")
