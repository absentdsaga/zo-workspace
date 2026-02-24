#!/usr/bin/env python3
"""
PRODUCTION 5-Minute Trading Bot - ACTUALLY WORKS
Extracts data from HTML since APIs don't have it
"""

import asyncio
import time
import json
import re
import requests
from datetime import datetime, timezone, timedelta
from py_clob_client.client import ClobClient

class WorkingBot:
    def __init__(self):
        self.client = ClobClient('https://clob.polymarket.com')
        self.paper_balance = 100.0
        self.trades = []
        
        print("="*70)
        print("🚀 PRODUCTION 5-MINUTE TRADING BOT")
        print("="*70)
        print(f"💰 Starting balance: ${self.paper_balance:.2f}")
        print("="*70)
        print()
    
    def get_live_market_slugs(self):
        """Calculate current 5-min market timestamps"""
        now = datetime.now(timezone.utc)
        et_now = now - timedelta(hours=5)
        
        # Round to current 5-min interval
        current_min = (et_now.minute // 5) * 5
        market_time = et_now.replace(minute=current_min, second=0, microsecond=0)
        
        slugs = []
        # Check current + next 3 intervals (20 minutes)
        for offset in [0, 5, 10, 15]:
            t = market_time + timedelta(minutes=offset)
            ts = int((t + timedelta(hours=5)).timestamp())
            slugs.append({
                'slug': f"btc-updown-5m-{ts}",
                'timestamp': ts,
                'time_et': t.strftime('%I:%M %p ET')
            })
        
        return slugs
    
    def get_market_data_from_html(self, slug):
        """Extract market data from HTML page"""
        try:
            url = f"https://polymarket.com/event/{slug}"
            resp = requests.get(url, timeout=5)
            
            if resp.status_code != 200:
                return None
            
            # Extract __NEXT_DATA__
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', resp.text)
            if not match:
                return None
            
            data = json.loads(match.group(1))
            
            # Navigate to market data
            page_props = data.get('props', {}).get('pageProps', {})
            dehydrated = page_props.get('dehydratedState', {})
            queries = dehydrated.get('queries', [])
            
            # Find the market query
            market_data = None
            for query in queries:
                state_data = query.get('state', {}).get('data', {})
                if isinstance(state_data, dict) and state_data.get('market_slug') == slug:
                    market_data = state_data
                    break
            
            if not market_data:
                return None
            
            tokens = market_data.get('tokens', [])
            if len(tokens) < 2:
                return None
            
            return {
                'question': market_data.get('question', slug),
                'yes_token': tokens[0]['token_id'],
                'no_token': tokens[1]['token_id'],
                'active': market_data.get('active', False),
                'closed': market_data.get('closed', False)
            }
            
        except Exception as e:
            print(f"      ⚠️  Error extracting data: {str(e)[:50]}")
            return None
    
    def get_prices(self, market_data):
        """Get orderbook prices"""
        try:
            yes_book = self.client.get_order_book(market_data['yes_token'])
            no_book = self.client.get_order_book(market_data['no_token'])
            
            yes_asks = yes_book.get('asks', [])
            no_asks = no_book.get('asks', [])
            
            if not yes_asks or not no_asks:
                return None
            
            # Best ask prices (sorted high to low, take LAST)
            yes_price = float(yes_asks[-1]['price'])
            no_price = float(no_asks[-1]['price'])
            
            return {
                'yes': yes_price,
                'no': no_price,
                'sum': yes_price + no_price
            }
        except:
            return None
    
    def check_opportunity(self, prices):
        """Check for profitable opportunities"""
        total = prices['sum']
        
        # Spread arbitrage: sum < $0.95 (5%+ profit)
        if total < 0.95:
            profit_pct = ((1.0 - total) / total) * 100
            if profit_pct > 3:  # Only if > 3% profit (covers fees)
                return {
                    'type': 'SPREAD_ARB',
                    'profit_pct': profit_pct,
                    'cost': total,
                    'action': 'BUY_BOTH'
                }
        
        # Momentum: extreme mispricings
        if prices['yes'] < 0.35:
            upside = ((0.90 - prices['yes']) / prices['yes']) * 100
            if upside > 100:  # 100%+ upside
                return {
                    'type': 'MOMENTUM',
                    'side': 'YES',
                    'entry': prices['yes'],
                    'upside': upside
                }
        
        if prices['no'] < 0.35:
            upside = ((0.90 - prices['no']) / prices['no']) * 100
            if upside > 100:
                return {
                    'type': 'MOMENTUM',
                    'side': 'NO',
                    'entry': prices['no'],
                    'upside': upside
                }
        
        return None
    
    async def run(self):
        """Main trading loop"""
        scan = 0
        
        while True:
            scan += 1
            now = datetime.now(timezone.utc) - timedelta(hours=5)
            print(f"\n{'='*70}")
            print(f"📊 SCAN #{scan} - {now.strftime('%I:%M:%S %p ET')}")
            print(f"{'='*70}")
            
            # Get potential market slugs
            market_slugs = self.get_live_market_slugs()
            
            print(f"🔍 Checking {len(market_slugs)} potential markets...\n")
            
            active_count = 0
            for m in market_slugs:
                print(f"  ⏰ {m['time_et']} - {m['slug']}")
                
                # Get market data from HTML
                market_data = self.get_market_data_from_html(m['slug'])
                
                if not market_data:
                    print(f"     ❌ Not found or closed")
                    continue
                
                if market_data['closed']:
                    print(f"     🔒 Market closed")
                    continue
                
                active_count += 1
                
                # Get prices
                prices = self.get_prices(market_data)
                
                if not prices:
                    print(f"     ⚠️  No liquidity")
                    continue
                
                print(f"     💵 YES: ${prices['yes']:.3f} | NO: ${prices['no']:.3f} | SUM: ${prices['sum']:.3f}")
                
                # Check for opportunity
                opp = self.check_opportunity(prices)
                
                if opp:
                    if opp['type'] == 'SPREAD_ARB':
                        print(f"     🔥 SPREAD ARB: {opp['profit_pct']:.1f}% profit (cost ${opp['cost']:.3f})")
                        self.trades.append({
                            'time': datetime.now().isoformat(),
                            'market': m['slug'],
                            'type': 'spread_arb',
                            'profit_pct': opp['profit_pct']
                        })
                    elif opp['type'] == 'MOMENTUM':
                        print(f"     🚀 MOMENTUM: {opp['side']} @ ${opp['entry']:.3f} ({opp['upside']:.0f}% upside)")
                        self.trades.append({
                            'time': datetime.now().isoformat(),
                            'market': m['slug'],
                            'type': 'momentum',
                            'side': opp['side'],
                            'upside': opp['upside']
                        })
            
            # Summary
            print(f"\n📈 ACTIVE MARKETS: {active_count} | OPPORTUNITIES: {len(self.trades)}")
            
            if len(self.trades) > 0:
                print(f"💰 Latest opportunity: {self.trades[-1]['type']}")
            
            await asyncio.sleep(20)  # Scan every 20 seconds

async def main():
    bot = WorkingBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
