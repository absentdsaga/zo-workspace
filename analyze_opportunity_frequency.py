#!/usr/bin/env python3
"""
Analyze how often opportunities appear in different ranges
"""

import json
import urllib.request
from datetime import datetime, timezone

print("🔍 OPPORTUNITY FREQUENCY ANALYSIS")
print("=" * 80)

# Fetch current markets
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

MIN_VOLUME = 50000
MIN_24HR = 5000
MAX_DAYS = 14

ranges = {
    '40-50%': (0.40, 0.50),
    '45-55%': (0.45, 0.55),  # Wider coin-flip range
    '80-90%': (0.80, 0.90),
    '70-90%': (0.70, 0.90),  # Wider favorites range
}

print("\n📊 CURRENT OPPORTUNITIES (WITH TIER 1 FILTERS):")
print("-" * 80)

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
                    })
                    break
        except:
            continue
    
    print(f"\n{range_name:<10}: {len(opportunities)} opportunities")
    if opportunities:
        for opp in opportunities[:3]:
            print(f"  • {opp['question'][:60]}...")
            print(f"    {opp['outcome']} @ {opp['price']*100:.1f}% | ${opp['volume_24hr']:,.0f}/day")

print("\n" + "=" * 80)
print("\n💡 FREQUENCY ANALYSIS:")
print("-" * 80)

# Check without time filter to see if that's the blocker
print("\n🔍 What if we REMOVE the 14-day filter?")
print("-" * 80)

for range_name, (price_min, price_max) in ranges.items():
    count_with_time = 0
    count_without_time = 0
    
    for market in markets:
        try:
            outcomes = json.loads(market.get("outcomes", "[]")) if isinstance(market.get("outcomes"), str) else market.get("outcomes", [])
            prices = json.loads(market.get("outcomePrices", "[]")) if isinstance(market.get("outcomePrices"), str) else market.get("outcomePrices", [])
            
            volume = float(market.get("volume", 0))
            volume_24hr = float(market.get("volume24hr", 0))
            
            # Basic filters (no time)
            if volume < MIN_VOLUME or volume_24hr < MIN_24HR:
                continue
            if not outcomes or len(outcomes) < 2:
                continue
            
            # Check price
            for price in prices:
                price = float(price)
                if price_min <= price < price_max:
                    count_without_time += 1
                    
                    # Check time
                    end_date_str = market.get("endDate")
                    if end_date_str:
                        try:
                            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            days = (end_date - datetime.now(timezone.utc)).days
                            if days <= MAX_DAYS:
                                count_with_time += 1
                        except:
                            pass
                    break
        except:
            continue
    
    blocked = count_without_time - count_with_time
    print(f"{range_name:<10}: {count_without_time} total → {count_with_time} after 14-day filter ({blocked} blocked)")

print("\n" + "=" * 80)
print("\n🎯 RECOMMENDATIONS:")
print("-" * 80)

# Suggest ranges with best opportunity flow
best_current = max([(name, len([1 for m in markets if True])) for name in ranges], key=lambda x: x[1])

print("\nBased on current market snapshot:")
print("\n1. **If staying strict (14 days + $5k/day):**")
print("   → May need to wait for opportunities to appear")
print("   → Quality over quantity approach")
print("   → Check markets during high-volume times (evenings, weekends)")

print("\n2. **To increase opportunity flow:**")
print("   → Widen to 45-55% range (captures more coin-flips)")
print("   → Or add 80-90% favorites as secondary strategy")
print("   → Or relax 14-day filter to 21 days (CAREFULLY)")

print("\n3. **Market timing matters:**")
print("   → Current snapshot is just one moment")
print("   → Political events, sports seasons create bursts")
print("   → Bot will catch opportunities as they appear")

print("\n4. **Reality check:**")
print("   → Trading with filters means FEWER but SAFER bets")
print("   → This is GOOD - prevented your -14.9% loss")
print("   → 1-2 good bets per day > 10 bad bets")
