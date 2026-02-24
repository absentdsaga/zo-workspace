#!/usr/bin/env python3
"""
Polymarket Paper Trading Bot - REST API Version
SIMPLIFIED: No WebSocket complexity, just reliable REST polling
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import aiohttp

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimplePaperTradingBot:
    """Simple REST-based paper trading bot - no WebSocket complexity"""

    def __init__(self, initial_balance: float = 100.0):
        self.paper_balance = initial_balance
        self.initial_balance = initial_balance
        self.paper_positions = {}
        self.paper_trades = []
        self.running = False
        self.session = None
        
        self.market_cache = {}
        self.opportunities_found = 0
        self.opportunities_profitable = 0
        self.total_paper_profit = 0.0
        
        self.markets_scanned = 0
        self.api_calls = 0
        
        logger.info(f"📝 Simple Paper Trading Bot Initialized")
        logger.info(f"💵 Simulated Balance: ${self.paper_balance:.2f}")
        logger.info(f"⚠️  NO REAL MONEY AT RISK")

    async def start(self):
        logger.info("🚀 Starting Simple Paper Trading Bot (REST API)")
        logger.info("=" * 70)
        
        self.running = True
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                await asyncio.gather(
                    self.market_scanner(),
                    self.performance_tracker()
                )
            except KeyboardInterrupt:
                logger.info("\n⚠️  Shutting down...")
                await self.shutdown()

    async def market_scanner(self):
        """Scan markets via REST API every 10 seconds"""
        logger.info("📊 Market scanner started (REST API mode)")
        logger.info(f"🔄 Scanning every {config.MARKET_SCAN_INTERVAL} seconds")
        
        while self.running:
            try:
                # Fetch active markets
                markets = await self.fetch_markets()
                
                for market in markets:
                    if not self.can_paper_trade():
                        break
                    
                    # Check for arbitrage
                    opp = await self.check_sum_to_one(market)
                    if opp and opp['expected_profit'] > 0.5:
                        await self.simulate_trade(opp)
                    
                    self.markets_scanned += 1
                
                await asyncio.sleep(config.MARKET_SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Scanner error: {e}")
                await asyncio.sleep(5)

    async def fetch_markets(self) -> List[Dict]:
        """Fetch markets from Polymarket API"""
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'limit': 50,  # Reduced for faster scanning
                'closed': 'false',
                'active': 'true'
            }
            
            self.api_calls += 1
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    markets = [
                        m for m in data
                        if m.get('clobTokenIds') and
                        float(m.get('volume', 0)) > 5000 and
                        m.get('closed') != True
                    ]
                    return markets[:50]
        except Exception as e:
            logger.debug(f"Error fetching markets: {e}")
        return []

    async def check_sum_to_one(self, market: Dict) -> Optional[Dict]:
        """Check for arbitrage opportunity"""
        try:
            clob_tokens = market.get('clobTokenIds')
            if not clob_tokens:
                return None
            
            token_ids = json.loads(clob_tokens) if isinstance(clob_tokens, str) else clob_tokens
            if len(token_ids) != 2:
                return None
            
            # Get prices via REST
            yes_price = await self.get_token_price(token_ids[0])
            no_price = await self.get_token_price(token_ids[1])
            
            if yes_price is None or no_price is None:
                return None
            
            total_cost = yes_price + no_price
            
            # Check for arbitrage
            if total_cost < 0.995:
                self.opportunities_found += 1
                profit_per_dollar = 1.0 - total_cost
                
                if profit_per_dollar >= config.MIN_PROFIT_THRESHOLD:
                    position_size = min(
                        config.MAX_POSITION_SIZE,
                        self.paper_balance * 0.4
                    )
                    
                    return {
                        'market': market,
                        'token_yes': token_ids[0],
                        'token_no': token_ids[1],
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'total_cost': total_cost,
                        'size': position_size,
                        'expected_profit': position_size * profit_per_dollar,
                        'profit_percent': profit_per_dollar * 100,
                        'timestamp': datetime.now()
                    }
        except Exception as e:
            logger.debug(f"Error checking market: {e}")
        
        return None

    async def get_token_price(self, token_id: str) -> Optional[float]:
        """Get token price from orderbook"""
        try:
            url = f"https://clob.polymarket.com/book"
            params = {'token_id': token_id}
            
            self.api_calls += 1
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    book = await resp.json()
                    asks = book.get('asks', [])
                    
                    if asks:
                        # Use lowest ask (last element)
                        return float(asks[-1]['price'])
        except Exception as e:
            logger.debug(f"Error getting price: {e}")
        
        return None

    async def simulate_trade(self, opp: Dict):
        """Simulate a paper trade"""
        try:
            question = opp['market'].get('question', 'Unknown')[:60]
            
            logger.info("\n" + "=" * 70)
            logger.info("💎 ARBITRAGE OPPORTUNITY FOUND (PAPER TRADE)")
            logger.info("=" * 70)
            logger.info(f"Market: {question}...")
            logger.info(f"YES: ${opp['yes_price']:.4f} | NO: ${opp['no_price']:.4f}")
            logger.info(f"Total cost: ${opp['total_cost']:.4f}")
            logger.info(f"Position size: ${opp['size']:.2f}")
            logger.info(f"Expected profit: ${opp['expected_profit']:.2f} ({opp['profit_percent']:.2f}%)")
            logger.info("=" * 70)
            
            # Simulate trade
            self.paper_balance -= opp['size']
            settlement_return = opp['size'] / opp['total_cost']
            actual_profit = settlement_return - opp['size']
            
            self.paper_trades.append({
                'timestamp': datetime.now(),
                'market': question,
                'cost': opp['size'],
                'profit': actual_profit,
                'profit_percent': (actual_profit / opp['size'] * 100)
            })
            
            self.opportunities_profitable += 1
            self.total_paper_profit += actual_profit
            self.paper_balance += settlement_return
            
            logger.info(f"✅ Simulated profit: ${actual_profit:.2f}")
            logger.info(f"   New balance: ${self.paper_balance:.2f}\n")
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")

    def can_paper_trade(self) -> bool:
        if self.paper_balance < 10:
            return False
        if len(self.paper_positions) >= config.MAX_CONCURRENT_TRADES:
            return False
        return True

    async def performance_tracker(self):
        """Track performance"""
        logger.info("📊 Performance tracker started")
        
        while self.running:
            try:
                profit = self.paper_balance - self.initial_balance
                profit_pct = (profit / self.initial_balance * 100) if self.initial_balance > 0 else 0
                win_rate = (self.opportunities_profitable / self.opportunities_found * 100) if self.opportunities_found > 0 else 0
                
                logger.info("\n" + "=" * 70)
                logger.info("📈 PAPER TRADING PERFORMANCE")
                logger.info("=" * 70)
                logger.info(f"Paper Balance: ${self.paper_balance:.2f}")
                logger.info(f"Paper P&L: ${profit:+.2f} ({profit_pct:+.1f}%)")
                logger.info(f"Opportunities Found: {self.opportunities_found}")
                logger.info(f"Profitable Trades: {self.opportunities_profitable}")
                logger.info(f"Win Rate: {win_rate:.0f}%")
                logger.info(f"Markets Scanned: {self.markets_scanned}")
                logger.info(f"API Calls: {self.api_calls}")
                logger.info("=" * 70)
                
                if len(self.paper_trades) > 0:
                    logger.info("\n📊 RECENT TRADES:")
                    for trade in self.paper_trades[-5:]:
                        logger.info(f"  • {trade['timestamp'].strftime('%H:%M:%S')} | "
                                  f"{trade['market'][:40]}... | "
                                  f"${trade['profit']:+.2f} ({trade['profit_percent']:+.1f}%)")
                
                logger.info("\n⚠️  Paper trading mode - no real money at risk\n")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(10)

    async def shutdown(self):
        self.running = False
        logger.info("\n🛑 Session complete")
        logger.info(f"Final balance: ${self.paper_balance:.2f}")
        logger.info(f"Total trades: {len(self.paper_trades)}")


async def main():
    print("=" * 70)
    print("  SIMPLE POLYMARKET PAPER TRADING BOT")
    print("  REST API - Reliable & Simple")
    print("=" * 70)
    print("\n⚠️  PAPER TRADING - NO REAL MONEY\n")
    
    initial_balance = float(input("Enter balance (default $100): ") or "100")
    
    print(f"\n🚀 Starting with ${initial_balance:.2f}...")
    print("Press Ctrl+C to stop\n")
    
    bot = SimplePaperTradingBot(initial_balance=initial_balance)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
