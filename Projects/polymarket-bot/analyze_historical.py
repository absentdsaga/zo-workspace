#!/usr/bin/env python3
import csv

print("📚 CHECKING RESOLVED MARKETS FILE")
print("=" * 80)

with open('resolved_markets.csv', 'r') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    markets = list(reader)

print(f"Total markets: {len(markets)}")
print(f"Headers: {headers}")
print(f"\nSample market:")
for k, v in list(markets[0].items())[:8]:
    print(f"  {k}: {v}")

# The file doesn't have outcome_price - we need to check the calibration file
print("\n" + "=" * 80)
print("Checking calibration files instead...")

import json
try:
    with open('per_market_calibration.json', 'r') as f:
        calib = json.load(f)
    
    print(f"\nPer-market calibration markets: {len(calib)}")
    
    # Check price distribution
    range_30_40_count = 0
    for market_id, data in calib.items():
        try:
            price = data.get('avg_price', 0)
            if 0.30 <= price <= 0.40:
                range_30_40_count += 1
        except:
            continue
    
    print(f"Markets in 30-40¢ range: {range_30_40_count}")
    print(f"Percentage: {range_30_40_count / len(calib) * 100:.1f}%")
    
    if range_30_40_count > 0:
        print("\n✅ The 30-40¢ range HAD markets historically")
        print("   Current drought is likely TEMPORARY")
    
except FileNotFoundError:
    print("No calibration file found")
