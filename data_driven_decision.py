#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone

# Fetch markets
url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100"
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=15) as response:
    markets = json.loads(response.read().decode())

print("📊 DATA-DRIVEN DECISION ANALYSIS")
print("=" * 80)

PRICE_MIN = 0.30
PRICE_MAX = 0.40
MIN_VOLUME = 50000

# Test different combinations
test_scenarios = [
    # (max_days, min_24hr_vol, name)
    (14, 5000, "Current (14d, $5k/day)"),
    (30, 5000, "Relax days (30d, $5k/day)"),
    (60, 5000, "Very relax days (60d, $5k/day)"),
    (14, 2500, "Lower liquidity (14d, $2.5k/day)"),
    (14, 1000, "Low liquidity (14d, $1k/day)"),
    (30, 2500, "Compromise (30d, $2.5k/day)"),
    (30, 1000, "Aggressive (30d, $1k/day)"),
]

results = []

for max_days, min_24hr_vol, name in test_scenarios:
    opportunities = []
    
    for market in markets:
        try:
            # Check days to resolution
            end_date_str = market.get("endDate")
            days_to_resolution = None
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (end_date - datetime.now(timezone.utc)).days
                    if days_to_resolution > max_days:
                        continue
                except:
                    pass
            
            # Parse data
            outcomes_str = market.get("outcomes", "[]")
            prices_str = market.get("outcomePrices", "[]")
            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
            
            volume = float(market.get("volume", 0))
            volume_24hr = float(market.get("volume24hr", 0))
            question = market.get("question", "")
            
            # Check filters
            if volume < MIN_VOLUME:
                continue
            if volume_24hr < min_24hr_vol:
                continue
            if not outcomes or len(outcomes) < 2:
                continue
            
            # Check price range
            for i, price in enumerate(prices):
                price = float(price)
                if PRICE_MIN <= price <= PRICE_MAX:
                    opportunities.append({
                        'question': question,
                        'outcome': outcomes[i] if i < len(outcomes) else "?",
                        'price': price,
                        'volume': volume,
                        'volume_24hr': volume_24hr,
                        'days': days_to_resolution
                    })
                    break
                    
        except:
            continue
    
    results.append({
        'scenario': name,
        'max_days': max_days,
        'min_24hr_vol': min_24hr_vol,
        'count': len(opportunities),
        'opps': opportunities
    })

print("\n🔬 SCENARIO TESTING RESULTS:")
print("=" * 80)

for r in results:
    status = "✅" if r['count'] > 0 else "❌"
    print(f"\n{status} {r['scenario']:<35} → {r['count']:>2} opportunities")
    
    if r['count'] > 0:
        # Show details
        for opp in r['opps'][:3]:
            days_str = f"{opp['days']}d" if opp['days'] is not None else "?"
            print(f"     • {opp['question'][:50]}...")
            print(f"       {opp['outcome']} @ {opp['price']*100:.1f}¢ | ${opp['volume_24hr']:,.0f}/day | {days_str}")

print("\n" + "=" * 80)
print("\n📈 KEY INSIGHTS:")

# Find viable options
viable = [r for r in results if r['count'] >= 1]

if not viable:
    print("\n❌ NO VIABLE OPTIONS - The 30-40¢ range is completely dead")
    print("\n   The data says: PIVOT STRATEGY")
    print("   • This price range has no active markets right now")
    print("   • Waiting won't help - there's simply no flow")
    print("   • Need to either:")
    print("     1. Wait weeks/months for markets to appear")
    print("     2. Analyze different price range (1-10¢ or 80-90¢)")
    print("     3. Build event-driven strategy instead of price-range strategy")
else:
    print(f"\n✅ {len(viable)} scenarios yield opportunities:")
    
    # Rank by risk/reward
    for r in sorted(viable, key=lambda x: (x['count'], -x['max_days']), reverse=True):
        print(f"\n   {r['scenario']}: {r['count']} opps")
        
        if r['opps']:
            # Analyze liquidity quality
            avg_24hr = sum(o['volume_24hr'] for o in r['opps']) / len(r['opps'])
            avg_days = sum(o['days'] for o in r['opps'] if o['days']) / len([o for o in r['opps'] if o['days']])
            
            print(f"     Avg 24hr volume: ${avg_24hr:,.0f}")
            print(f"     Avg days to resolution: {avg_days:.0f}")
            
            # Risk assessment
            if avg_days > 60:
                risk = "🔴 HIGH RISK - Very long dated"
            elif avg_days > 30:
                risk = "🟡 MEDIUM RISK - Long dated"
            elif avg_days > 14:
                risk = "🟢 ACCEPTABLE - Moderate timeframe"
            else:
                risk = "✅ LOW RISK - Short dated"
            
            if avg_24hr < 2500:
                liq_risk = "🔴 Poor liquidity"
            elif avg_24hr < 5000:
                liq_risk = "🟡 Moderate liquidity"
            else:
                liq_risk = "✅ Good liquidity"
            
            print(f"     {risk}")
            print(f"     {liq_risk}")

print("\n" + "=" * 80)
print("\n🎯 DATA-DRIVEN RECOMMENDATION:")

if not viable:
    print("\n   PIVOT AWAY FROM 30-40¢ RANGE")
    print("   • This range is structurally dead on Polymarket right now")
    print("   • Your +14% edge is valid but can't be realized with no markets")
    print("   • Best option: Analyze 1-10¢ or 80-90¢ range (where action is)")
else:
    best = max(viable, key=lambda x: x['count'])
    print(f"\n   OPTIMAL: {best['scenario']}")
    print(f"   • Gives {best['count']} opportunities vs 0 currently")
    
    if best['max_days'] > 30:
        print(f"   ⚠️  WARNING: Accepts {best['max_days']}-day timeframe")
        print(f"   • This is what got you in trouble before")
        print(f"   • Only do this if you're willing to hold long-term")
        print(f"   • OR: Just wait for better markets to appear")
