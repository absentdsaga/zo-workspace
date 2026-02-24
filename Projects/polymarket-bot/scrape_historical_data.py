#!/usr/local/bin/python3
"""
Scrape REAL Polymarket historical data
- Get all resolved markets
- Fetch final prices before resolution
- Build price calibration dataset
- Calculate ACTUAL win rates per price bucket
"""
import requests
import json
import time
from datetime import datetime
from collections import defaultdict
import pickle

class PolymarketDataScraper:
    def __init__(self):
        self.resolved_markets = []
        self.calibration_data = defaultdict(lambda: {'prices': [], 'won': [], 'market_names': []})
        
    def fetch_resolved_markets(self, limit=1000):
        """Get resolved markets from Polymarket API"""
        print("=" * 80)
        print("📥 FETCHING RESOLVED MARKETS")
        print("=" * 80)
        
        all_markets = []
        offset = 0
        batch_size = 100
        
        while offset < limit:
            try:
                print(f"Batch {offset//batch_size + 1}... ", end='', flush=True)
                
                resp = requests.get(
                    "https://gamma-api.polymarket.com/markets",
                    params={
                        "closed": "true",
                        "_lt": 100,  # Get closed markets
                        "limit": batch_size,
                        "offset": offset
                    },
                    timeout=15
                )
                
                if resp.status_code == 200:
                    batch = resp.json()
                    if not batch or len(batch) == 0:
                        print("No more markets")
                        break
                    
                    # Filter for resolved markets only
                    resolved = [m for m in batch if m.get('resolved') == True]
                    all_markets.extend(resolved)
                    
                    print(f"{len(resolved)} resolved")
                    offset += batch_size
                    time.sleep(0.5)  # Rate limit
                else:
                    print(f"Error {resp.status_code}")
                    break
                    
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.resolved_markets = all_markets
        print(f"\n✅ Total resolved markets: {len(all_markets)}\n")
        return all_markets
    
    def build_calibration_dataset(self):
        """Build price -> outcome dataset from resolved markets"""
        print("=" * 80)
        print("📊 BUILDING CALIBRATION DATASET")
        print("=" * 80)
        print()
        
        total_outcomes = 0
        
        for i, market in enumerate(self.resolved_markets):
            if i % 100 == 0:
                print(f"Processing market {i}/{len(self.resolved_markets)}...")
            
            try:
                question = market.get('question', '')
                winning_outcome = market.get('winningOutcome')
                
                if not winning_outcome:
                    continue
                
                # Get outcomes and final prices
                outcomes_str = market.get('outcomes', '[]')
                outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
                
                prices_str = market.get('outcomePrices', '[]')
                prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
                
                if not outcomes or not prices:
                    continue
                
                # Record each outcome
                for outcome, price_str in zip(outcomes, prices):
                    try:
                        price = float(price_str)
                        
                        if price <= 0 or price >= 1:
                            continue
                        
                        won = 1 if outcome == winning_outcome else 0
                        
                        # Categorize by price bucket
                        bucket = self.get_bucket(price)
                        
                        self.calibration_data[bucket]['prices'].append(price)
                        self.calibration_data[bucket]['won'].append(won)
                        self.calibration_data[bucket]['market_names'].append(question[:50])
                        
                        total_outcomes += 1
                        
                    except:
                        continue
                        
            except:
                continue
        
        print(f"\n✅ Processed {total_outcomes} outcomes from {len(self.resolved_markets)} markets\n")
        return self.calibration_data
    
    def get_bucket(self, price):
        """Categorize price into bucket"""
        p = price * 100
        if p <= 5: return '0-5%'
        elif p <= 10: return '5-10%'
        elif p <= 20: return '10-20%'
        elif p <= 30: return '20-30%'
        elif p <= 40: return '30-40%'
        elif p <= 50: return '40-50%'
        elif p <= 60: return '50-60%'
        elif p <= 70: return '60-70%'
        elif p <= 80: return '70-80%'
        elif p <= 90: return '80-90%'
        else: return '90-100%'
    
    def analyze_calibration(self):
        """Analyze price calibration from REAL data"""
        print("=" * 80)
        print("📊 PRICE CALIBRATION ANALYSIS (REAL DATA)")
        print("=" * 80)
        print()
        print("Bucket   | N      | Expected | Actual  | Edge    | Verdict")
        print("-" * 70)
        
        results = []
        
        bucket_order = ['0-5%', '5-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
                       '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
        
        for bucket in bucket_order:
            data = self.calibration_data.get(bucket)
            if not data or len(data['prices']) < 10:
                continue
            
            n = len(data['prices'])
            wins = sum(data['won'])
            
            # Expected (midpoint of bucket)
            expected_map = {
                '0-5%': 2.5, '5-10%': 7.5, '10-20%': 15.0,
                '20-30%': 25.0, '30-40%': 35.0, '40-50%': 45.0,
                '50-60%': 55.0, '60-70%': 65.0, '70-80%': 75.0,
                '80-90%': 85.0, '90-100%': 95.0,
            }
            
            expected = expected_map[bucket]
            actual = (wins / n) * 100
            edge = actual - expected
            
            # Verdict
            if edge > 2 and n > 100:
                verdict = "🟢 EDGE"
            elif edge < -2 and n > 100:
                verdict = "🔴 NEGATIVE"
            else:
                verdict = "⚪ NEUTRAL"
            
            results.append({
                'bucket': bucket,
                'n': n,
                'expected': expected,
                'actual': actual,
                'edge': edge,
                'verdict': verdict
            })
            
            print(f"{bucket:8} | {n:6} | {expected:8.1f}% | {actual:7.1f}% | {edge:+7.2f}% | {verdict}")
        
        return results
    
    def save_dataset(self, filename='polymarket_calibration.pkl'):
        """Save dataset for later analysis"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'calibration_data': dict(self.calibration_data),
                'resolved_markets': self.resolved_markets,
                'timestamp': datetime.now()
            }, f)
        print(f"\n💾 Dataset saved to {filename}")

def main():
    print("=" * 80)
    print("🎯 POLYMARKET REAL DATA SCRAPER")
    print("=" * 80)
    print()
    
    scraper = PolymarketDataScraper()
    
    # Step 1: Fetch resolved markets
    print("⏱️  This will take 2-4 hours to get comprehensive data...")
    print("    Starting with first 1000 markets as proof of concept\n")
    
    markets = scraper.fetch_resolved_markets(limit=1000)
    
    if len(markets) < 10:
        print("❌ Not enough data. API might have changed.")
        return
    
    # Step 2: Build calibration dataset
    scraper.build_calibration_dataset()
    
    # Step 3: Analyze
    results = scraper.analyze_calibration()
    
    # Step 4: Save
    scraper.save_dataset()
    
    print("\n" + "=" * 80)
    print("✅ SCRAPING COMPLETE")
    print("=" * 80)
    print(f"\nNext steps:")
    print("1. Run Monte Carlo simulations on this REAL data")
    print("2. Identify which price ranges have TRUE mathematical edge")
    print("3. Build bot based on ACTUAL results, not assumptions")

if __name__ == "__main__":
    main()
