#!/usr/local/bin/python3
"""
RESOLUTION SCRAPER
Scrapes Polymarket API for resolved markets to build price calibration

Strategy:
- Fetch all closed markets from API
- Identify resolved markets by checking if outcome prices are 0/1
- Build dataset of: market_id, price_history, winning_outcome
- This lets us calculate actual win rates per price bucket
"""
import requests
import json
import pandas as pd
import time
from datetime import datetime
from collections import defaultdict

class ResolutionScraper:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com/markets"
        self.resolved_markets = []

    def is_resolved(self, market):
        """Check if market is resolved by looking at outcome prices"""
        try:
            prices_str = market.get('outcomePrices', '[]')
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str

            if len(prices) != 2:
                return False, None

            price0 = float(prices[0])
            price1 = float(prices[1])

            # Resolved markets have one outcome at ~0 and one at ~1
            if price0 < 0.01 and price1 > 0.99:
                return True, 1  # Outcome 1 won
            elif price1 < 0.01 and price0 > 0.99:
                return True, 0  # Outcome 0 won

            return False, None

        except:
            return False, None

    def fetch_closed_markets(self, limit=100, offset=0):
        """Fetch batch of closed markets"""
        try:
            resp = requests.get(
                self.base_url,
                params={
                    "closed": "true",
                    "limit": limit,
                    "offset": offset
                },
                timeout=10
            )

            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"❌ API error {resp.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def scrape_all_resolutions(self, max_markets=10000):
        """Scrape all resolved markets"""
        print("=" * 80)
        print("🔍 RESOLUTION SCRAPER")
        print("=" * 80)
        print(f"Target: {max_markets:,} closed markets")
        print()

        offset = 0
        batch_size = 100
        total_checked = 0
        total_resolved = 0

        while total_checked < max_markets:
            print(f"📥 Fetching batch at offset {offset}...")
            markets = self.fetch_closed_markets(limit=batch_size, offset=offset)

            if not markets:
                print("✅ No more markets - reached end")
                break

            # Check each market for resolution
            for market in markets:
                total_checked += 1

                resolved, winner = self.is_resolved(market)

                if resolved:
                    market_data = {
                        'market_id': market.get('id'),
                        'question': market.get('question', '')[:100],
                        'slug': market.get('slug', ''),
                        'outcomes': market.get('outcomes', '[]'),
                        'winner': winner,
                        'volume': float(market.get('volume', 0)),
                        'closed_time': market.get('closedTime', ''),
                        'category': market.get('category', ''),
                        'condition_id': market.get('conditionId', ''),
                        'clob_token_ids': market.get('clobTokenIds', '[]')
                    }

                    self.resolved_markets.append(market_data)
                    total_resolved += 1

                    if total_resolved % 100 == 0:
                        print(f"   ✓ Found {total_resolved} resolved markets (checked {total_checked})")

            # Check if we got a full batch
            if len(markets) < batch_size:
                print(f"✅ Reached end of data ({len(markets)} < {batch_size})")
                break

            offset += batch_size
            time.sleep(0.5)  # Rate limit

        print()
        print("=" * 80)
        print(f"📊 SCRAPING COMPLETE")
        print("=" * 80)
        print(f"   Total checked: {total_checked:,}")
        print(f"   Total resolved: {total_resolved:,}")
        print(f"   Resolution rate: {total_resolved/total_checked*100:.1f}%")
        print()

        return self.resolved_markets

    def save_results(self, filename='resolved_markets.csv'):
        """Save to CSV"""
        if not self.resolved_markets:
            print("❌ No resolved markets to save")
            return

        df = pd.DataFrame(self.resolved_markets)
        df.to_csv(filename, index=False)

        print(f"💾 Saved {len(df):,} resolved markets to: {filename}")
        print()

        # Show sample
        print("📊 Sample resolved markets:")
        print(df[['question', 'winner', 'volume']].head(5).to_string())

        return df

def main():
    scraper = ResolutionScraper()

    # Scrape resolved markets
    resolved = scraper.scrape_all_resolutions(max_markets=50000)

    # Save results
    df = scraper.save_results('resolved_markets.csv')

    if df is not None:
        # Show stats
        print()
        print("=" * 80)
        print("📈 RESOLUTION STATISTICS")
        print("=" * 80)

        print(f"\n💰 Volume:")
        print(f"   Total: ${df['volume'].sum():,.0f}")
        print(f"   Mean: ${df['volume'].mean():,.0f}")
        print(f"   Median: ${df['volume'].median():,.0f}")

        print(f"\n🎯 Outcome Distribution:")
        print(f"   Outcome 0 wins: {(df['winner'] == 0).sum():,}")
        print(f"   Outcome 1 wins: {(df['winner'] == 1).sum():,}")

        if 'category' in df.columns:
            print(f"\n🏷️ Top Categories:")
            top_cats = df['category'].value_counts().head(10)
            for cat, count in top_cats.items():
                print(f"   {cat}: {count:,}")

if __name__ == "__main__":
    main()
