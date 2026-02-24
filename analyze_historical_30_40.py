#!/usr/bin/env python3
import csv
from datetime import datetime, timezone

print("📚 HISTORICAL ANALYSIS: Was 30-40¢ range EVER active?")
print("=" * 80)

# Load the resolved markets data
with open('resolved_markets.csv', 'r') as f:
    reader = csv.DictReader(f)
    markets = list(reader)

print(f"\nTotal resolved markets in dataset: {len(markets)}")

# Find 30-40¢ markets
range_30_40 = []
for m in markets:
    try:
        price = float(m.get('outcome_price', 0))
        if 0.30 <= price <= 0.40:
            range_30_40.append(m)
    except:
        continue

print(f"Markets in 30-40¢ range: {len(range_30_40)}")

if range_30_40:
    # Analyze when they were created
    years = {}
    for m in range_30_40:
        try:
            created = m.get('created_at', '')
            if created:
                year = created[:4]
                years[year] = years.get(year, 0) + 1
        except:
            continue
    
    print(f"\n📅 30-40¢ markets by year:")
    for year in sorted(years.keys()):
        print(f"   {year}: {years[year]} markets")
    
    # Sample recent ones
    print(f"\n🔍 Sample of 30-40¢ markets (showing 10):")
    for m in range_30_40[:10]:
        question = m.get('question', '')[:60]
        price = float(m.get('outcome_price', 0))
        volume = float(m.get('volume', 0))
        created = m.get('created_at', '')[:10]
        print(f"   • {question}... @ {price*100:.1f}¢")
        print(f"     Vol: ${volume:,.0f} | Created: {created}")

print("\n" + "=" * 80)
print("\n💡 CONCLUSION:")

# Check if most are old
recent_count = sum(1 for m in range_30_40 if m.get('created_at', '')[:4] in ['2025', '2026'])
old_count = len(range_30_40) - recent_count

print(f"\n   Recent (2025-2026): {recent_count} markets")
print(f"   Older (pre-2025): {old_count} markets")

if old_count > recent_count * 2:
    print(f"\n   ⚠️  30-40¢ range was MORE ACTIVE in the past")
    print(f"   • This suggests structural shift in Polymarket")
    print(f"   • Platform may have evolved away from this range")
    print(f"   • Your +14% edge is from HISTORICAL data that may not apply now")
else:
    print(f"\n   ✅ 30-40¢ range is cyclical")
    print(f"   • Current drought is temporary")
    print(f"   • Patience may pay off")
