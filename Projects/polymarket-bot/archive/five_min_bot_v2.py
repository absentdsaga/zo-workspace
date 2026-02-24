#!/usr/bin/env python3
"""
Polymarket 5-Minute Market Trading Bot v2
Uses direct market slug checking instead of API scanning
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timezone
from py_clob_client.client import ClobClient

class FiveMinuteBotV2:
    def __init__(self, paper_trading=True):
        self.client = ClobClient('https://clob.polymarket.com')
        self.paper_trading = paper_trading
        self.paper_balance = 100.0
        self.trades = []
        
        print("="*70)
        print("🚀 POLYMARKET 5-MINUTE MARKET BOT V2")
        print("="*70)
        if paper_trading:
            print("⚠️  PAPER TRADING MODE - ZERO RISK")
            print(f"   Starting balance: ${self.paper_balance:.2f}")
        print("="*70)
        print()
    
    def get_current_5min_markets(self):
        """
        5-min markets follow predictable URL patterns:
        https://polymarket.com/event/btc-updown-5m-{timestamp}
        
        They're created every 5 minutes on the clock (XX:00, XX:05, XX:10, etc.)
        Timestamp is Unix time of the market start
        """
        print("🔍 Checking for active 5-minute markets...")
        
        # Calculate current and next 5-min windows
        now = datetime.now(timezone.utc)
        current_min = now.minute
        
        # Round to nearest 5-min interval
        intervals = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        
        # Find the current and next intervals
        current_interval = max([i for i in intervals if i <= current_min])
        
        # Generate timestamps for current and next markets
        current_time = now.replace(minute=current_interval, second=0, microsecond=0)
        next_time = current_time.replace(minute=(current_interval + 5) % 60)
        if next_time <= current_time:
            next_time = next_time.replace(hour=current_time.hour + 1)
        
        timestamps = [
            int(current_time.timestamp()),
            int(next_time.timestamp()),
        ]
        
        markets = []
        for ts in timestamps:
            # Try BTC 5-min market
            slug = f"btc-updown-5m-{ts}"
            url = f"https://polymarket.com/event/{slug}"
            
            try:
                # Try to fetch the market page
                response = requests.get(url, timeout=5)
                if response.status_code == 200 and 'Bitcoin Up or Down' in response.text:
                    markets.append({
                        'slug': slug,
                        'url': url,
                        'timestamp': ts,
                        'asset': 'BTC'
                    })
                    print(f"   ✅ Found active market: {slug}")
            except:
                pass
        
        return markets
    
    async def scan_markets(self):
        """Scan for 5-min markets every 30 seconds"""
        iteration = 0
        
        while True:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"📊 SCAN #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            
            markets = self.get_current_5min_markets()
            
            if markets:
                print(f"\n✅ Found {len(markets)} active 5-minute markets")
                for m in markets:
                    print(f"   • {m['slug']}")
            else:
                print("\n⚠️  No active 5-minute markets found")
                print("   Possible reasons:")
                print("   - Markets only active during US trading hours")
                print("   - Currently 10:54 PM ET (after hours)")
                print("   - Try again tomorrow 9:30 AM - 4:00 PM ET")
            
            # Show account status
            if iteration % 3 == 0:
                print(f"\n{'='*70}")
                print("📈 ACCOUNT STATUS")
                print(f"{'='*70}")
                print(f"Paper Balance: ${self.paper_balance:.2f}")
                print(f"Total Trades: {len(self.trades)}")
                print(f"{'='*70}")
            
            await asyncio.sleep(30)

async def main():
    bot = FiveMinuteBotV2(paper_trading=True)
    await bot.scan_markets()

if __name__ == "__main__":
    asyncio.run(main())
