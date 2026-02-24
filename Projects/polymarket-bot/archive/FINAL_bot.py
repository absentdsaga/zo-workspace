#!/usr/bin/env python3
"""
PRODUCTION 5-Minute Trading Bot
Uses Polymarket's real-time WebSocket feed for instant trade data
"""

import asyncio
import json
import websockets
from datetime import datetime, timezone, timedelta
from py_clob_client.client import ClobClient

class FinalBot:
    def __init__(self):
        self.client = ClobClient('https://clob.polymarket.com')
        self.ws_url = "wss://real-time-data-streaming.polymarket.com"
        self.paper_balance = 100.0
        self.trades = []
        self.market_prices = {}  # Cache latest prices
        
        print("="*70)
        print("🚀 PRODUCTION 5-MINUTE TRADING BOT - FINAL")
        print("="*70)
        print(f"💰 Starting balance: ${self.paper_balance:.2f}")
        print(f"📡 WebSocket: {self.ws_url}")
        print("="*70)
        print()
    
    def get_current_5min_slug(self):
        """Get current 5-minute market slug"""
        now = datetime.now(timezone.utc) - timedelta(hours=5)
        current_min = (now.minute // 5) * 5
        market_time = now.replace(minute=current_min, second=0, microsecond=0)
        ts = int((market_time + timedelta(hours=5)).timestamp())
        return f"btc-updown-5m-{ts}", market_time.strftime('%I:%M %p ET')
    
    async def connect_websocket(self):
        """Connect to Polymarket WebSocket and stream trade data"""
        print("🔌 Connecting to WebSocket...")
        
        async with websockets.connect(self.ws_url) as websocket:
            print("✅ Connected!\n")
            
            # Get current 5-min market
            slug, time_et = self.get_current_5min_slug()
            print(f"🎯 Subscribing to: {slug}")
            print(f"   Time: {time_et}\n")
            
            # Subscribe to trades for this market
            subscribe_msg = {
                "action": "subscribe",
                "subscriptions": [
                    {
                        "topic": "activity",
                        "type": "trades",
                        "filters": json.dumps({"market_slug": slug})
                    }
                ]
            }
            
            await websocket.send(json.dumps(subscribe_msg))
            print("📨 Subscription sent\n")
            print("⏳ Waiting for trade data...")
            print("   (This will update when real trades happen)\n")
            
            # Listen for messages
            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(message)
                    
                    message_count += 1
                    
                    # Process trade data
                    if data.get('type') == 'trades':
                        payload = data.get('payload', {})
                        print(f"\n💰 TRADE #{message_count} DETECTED!")
                        print(f"   Market: {payload.get('slug', 'N/A')[:50]}")
                        print(f"   Side: {payload.get('side', 'N/A')}")
                        print(f"   Price: ${payload.get('price', 0):.4f}")
                        print(f"   Size: {payload.get('size', 0)}")
                        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                        
                        # Update price cache
                        self.update_price_cache(slug, payload)
                        
                        # Check for arbitrage
                        self.check_opportunity(slug)
                    
                    else:
                        # Other message types
                        print(f"📨 Message: {data.get('type', 'unknown')}")
                    
                except asyncio.TimeoutError:
                    # No messages in 30s - check if we should switch to next market
                    new_slug, new_time = self.get_current_5min_slug()
                    if new_slug != slug:
                        print(f"\n🔄 Market changed! Resubscribing to {new_slug}")
                        slug = new_slug
                        
                        # Resubscribe
                        await websocket.send(json.dumps(subscribe_msg))
                    else:
                        print(f"\n⏰ No trades in 30s (market might be inactive)")
                
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    break
    
    def update_price_cache(self, slug, trade_data):
        """Update cached prices from trade data"""
        price = trade_data.get('price', 0)
        side = trade_data.get('side', '')
        
        if slug not in self.market_prices:
            self.market_prices[slug] = {'last_yes': None, 'last_no': None}
        
        # Assuming YES = BUY side, NO = SELL side (might need adjustment)
        if side == 'BUY':
            self.market_prices[slug]['last_yes'] = price
        elif side == 'SELL':
            self.market_prices[slug]['last_no'] = price
    
    def check_opportunity(self, slug):
        """Check if current prices present an arbitrage opportunity"""
        if slug not in self.market_prices:
            return
        
        prices = self.market_prices[slug]
        yes_price = prices.get('last_yes')
        no_price = prices.get('last_no')
        
        if yes_price and no_price:
            total = yes_price + no_price
            
            if total < 0.95:
                profit_pct = ((1.0 - total) / total) * 100
                if profit_pct > 3:
                    print(f"\n🔥 ARBITRAGE OPPORTUNITY!")
                    print(f"   YES: ${yes_price:.4f} + NO: ${no_price:.4f} = ${total:.4f}")
                    print(f"   Profit: {profit_pct:.2f}%")
                    
                    self.trades.append({
                        'time': datetime.now().isoformat(),
                        'market': slug,
                        'type': 'arbitrage',
                        'profit_pct': profit_pct
                    })
    
    async def run(self):
        """Main entry point"""
        while True:
            try:
                await self.connect_websocket()
            except Exception as e:
                print(f"\n❌ Connection lost: {e}")
                print("🔄 Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    bot = FinalBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user")
