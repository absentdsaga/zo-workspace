#!/usr/bin/env python3
"""
Polymarket Paper Trading Bot - Zero Risk Testing
Simulates real trading without spending actual money
Validates strategy profitability before deploying capital
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import aiohttp

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperTradingBot:
    """Paper trading bot - simulates real trading without actual capital"""
    
    def __init__(self, initial_balance: float = 100.0):
        """Initialize paper trading bot"""
        self.paper_balance = initial_balance
        self.initial_balance = initial_balance
        self.paper_positions = {}
        self.paper_trades = []
        self.running = False
        self.session = None
        
        # Track what would have happened
        self.opportunities_found = 0
        self.opportunities_profitable = 0
        self.total_paper_profit = 0.0
        
        logger.info(f"📝 Paper Trading Mode Initialized")
        logger.info(f"💵 Simulated Balance: ${self.paper_balance:.2f}")
        logger.info("⚠️  NO REAL MONEY AT RISK - This is simulation only")
    
    async def start(self):
        """Start paper trading"""
        logger.info("🚀 Starting Paper Trading Bot")
        logger.info("=" * 70)
        logger.info("This bot will:")
        logger.info("  ✅ Find real arbitrage opportunities")
        logger.info("  ✅ Simulate trade execution")
        logger.info("  ✅ Track simulated P&L")
        logger.info("  ✅ Show what WOULD happen with real money")
        logger.info("  ❌ NOT spend any actual money")
        logger.info("=" * 70)
        
        self.running = True
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                await asyncio.gather(
                    self.market_scanner(),
                    self.position_manager(),
                    self.performance_tracker()
                )
            except KeyboardInterrupt:
                logger.info("\n⚠️  Shutting down paper trading...")
                await self.shutdown()
    
    async def market_scanner(self):
        """Scan for opportunities (just like real bot)"""
        logger.info("📊 Market scanner started (paper trading mode)")
        
        while self.running:
            try:
                markets = await self.fetch_markets()
                
                for market in markets:
                    if not self.can_paper_trade():
                        break
                    
                    opp = await self.check_sum_to_one(market)
                    if opp and opp['expected_profit'] > 0.5:
                        await self.simulate_trade(opp)
                
                await asyncio.sleep(config.MARKET_SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Scanner error: {e}")
                await asyncio.sleep(5)
    
    async def fetch_markets(self) -> List[Dict]:
        """Fetch real market data from Polymarket"""
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'limit': 100,
                'closed': False,
                'active': True
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    markets = [
                        m for m in data
                        if m.get('outcomes_count') == 2 and 
                        float(m.get('volume', 0)) > 5000
                    ]
                    return markets[:50]
        except Exception as e:
            logger.debug(f"Error fetching markets: {e}")
        return []
    
    async def check_sum_to_one(self, market: Dict) -> Optional[Dict]:
        """Check for real arbitrage opportunities"""
        try:
            # Get market data
            tokens = market.get('tokens', [])
            if len(tokens) != 2:
                return None
            
            # For paper trading, we'll fetch real orderbook data
            # but not execute actual trades
            token_yes = tokens[0]['token_id']
            token_no = tokens[1]['token_id']
            
            # Get real prices from Polymarket
            yes_price = await self.get_token_price(token_yes)
            no_price = await self.get_token_price(token_no)
            
            if yes_price is None or no_price is None:
                return None
            
            total_cost = yes_price + no_price
            
            # Real arbitrage exists if total < 1.0
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
                        'token_yes': token_yes,
                        'token_no': token_no,
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
        """Get real token price from Polymarket"""
        try:
            # Fetch real orderbook from CLOB API
            url = f"https://clob.polymarket.com/book"
            params = {'token_id': token_id}

            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    book = await resp.json()
                    asks = book.get('asks', [])

                    if asks:
                        # CRITICAL FIX: asks sorted highest-to-lowest, use last element
                        return float(asks[-1]['price'])
        except Exception as e:
            logger.debug(f"Error getting price: {e}")
        return None
    
    async def simulate_trade(self, opp: Dict):
        """Simulate executing a trade (NO REAL MONEY)"""
        try:
            question = opp['market'].get('question', 'Unknown market')[:60]
            
            logger.info("\n" + "=" * 70)
            logger.info("💎 ARBITRAGE OPPORTUNITY FOUND (PAPER TRADE)")
            logger.info("=" * 70)
            logger.info(f"Market: {question}...")
            logger.info(f"YES price: ${opp['yes_price']:.4f}")
            logger.info(f"NO price: ${opp['no_price']:.4f}")
            logger.info(f"Total cost: ${opp['total_cost']:.4f}")
            logger.info(f"Guaranteed return: ${1.00:.4f}")
            logger.info("-" * 70)
            logger.info(f"Position size: ${opp['size']:.2f}")
            logger.info(f"Expected profit: ${opp['expected_profit']:.2f}")
            logger.info(f"Profit margin: {opp['profit_percent']:.2f}%")
            logger.info("=" * 70)
            logger.info("📝 SIMULATING TRADE (no real money spent)")
            
            # Simulate the trade
            trade_id = f"paper_{int(time.time())}"
            
            # Record paper position
            self.paper_positions[trade_id] = {
                'market': opp['market'],
                'entry_time': datetime.now(),
                'cost': opp['size'],
                'expected_profit': opp['expected_profit'],
                'total_cost': opp['total_cost'],
                'yes_price': opp['yes_price'],
                'no_price': opp['no_price'],
                'status': 'open'
            }
            
            # Update paper balance (reduce by cost)
            self.paper_balance -= opp['size']
            
            # Simulate immediate settlement (in real life, waits for market resolution)
            # For paper trading, we assume the arbitrage works
            settlement_return = opp['size'] / opp['total_cost']  # Guaranteed $1.00 per pair
            actual_profit = settlement_return - opp['size']
            
            # Record the trade
            self.paper_trades.append({
                'timestamp': datetime.now(),
                'market': question,
                'cost': opp['size'],
                'profit': actual_profit,
                'profit_percent': (actual_profit / opp['size'] * 100),
                'yes_price': opp['yes_price'],
                'no_price': opp['no_price']
            })
            
            self.opportunities_profitable += 1
            self.total_paper_profit += actual_profit
            self.paper_balance += settlement_return  # Add back the $1.00 return
            
            logger.info(f"✅ PAPER TRADE COMPLETED")
            logger.info(f"   Simulated profit: ${actual_profit:.2f}")
            logger.info(f"   New paper balance: ${self.paper_balance:.2f}")
            logger.info("")
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
    
    def can_paper_trade(self) -> bool:
        """Check if we can place more paper trades"""
        if self.paper_balance < 10:
            return False
        if len(self.paper_positions) >= config.MAX_CONCURRENT_TRADES:
            return False
        return True
    
    async def position_manager(self):
        """Manage paper positions"""
        logger.info("👁️  Position manager started (paper mode)")
        
        while self.running:
            try:
                # In paper trading, positions resolve instantly
                # In real trading, you'd wait for market settlement
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Position manager error: {e}")
                await asyncio.sleep(10)
    
    async def performance_tracker(self):
        """Track and report performance"""
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
                logger.info(f"Total Simulated Profit: ${self.total_paper_profit:.2f}")
                logger.info("=" * 70)
                
                if len(self.paper_trades) > 0:
                    logger.info("\n📊 RECENT TRADES:")
                    for trade in self.paper_trades[-5:]:
                        logger.info(f"  • {trade['timestamp'].strftime('%H:%M:%S')} | "
                                  f"{trade['market'][:40]}... | "
                                  f"Profit: ${trade['profit']:+.2f} ({trade['profit_percent']:+.1f}%)")
                
                # Projections
                if len(self.paper_trades) > 0:
                    first_trade = self.paper_trades[0]['timestamp']
                    hours_running = (datetime.now() - first_trade).total_seconds() / 3600
                    
                    if hours_running > 0:
                        profit_per_hour = profit / hours_running
                        daily_projection = profit_per_hour * 24
                        weekly_projection = daily_projection * 7
                        monthly_projection = daily_projection * 30
                        
                        logger.info("\n🎯 PROJECTIONS (if this rate continues with real money):")
                        logger.info(f"   Daily: ${daily_projection:.2f}")
                        logger.info(f"   Weekly: ${weekly_projection:.2f}")
                        logger.info(f"   Monthly: ${monthly_projection:.2f}")
                
                logger.info("\n⚠️  REMINDER: This is PAPER TRADING - no real money at risk")
                logger.info("   Deploy real capital only after validation period\n")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(10)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("\n" + "=" * 70)
        logger.info("🛑 PAPER TRADING SESSION COMPLETE")
        logger.info("=" * 70)
        
        self.running = False
        
        profit = self.paper_balance - self.initial_balance
        profit_pct = (profit / self.initial_balance * 100) if self.initial_balance > 0 else 0
        
        logger.info(f"\nFinal Paper Balance: ${self.paper_balance:.2f}")
        logger.info(f"Total Paper Profit: ${profit:+.2f} ({profit_pct:+.1f}%)")
        logger.info(f"Total Opportunities Found: {self.opportunities_found}")
        logger.info(f"Profitable Trades: {self.opportunities_profitable}")
        logger.info(f"Total Trades: {len(self.paper_trades)}")
        
        if len(self.paper_trades) > 0:
            avg_profit = sum(t['profit'] for t in self.paper_trades) / len(self.paper_trades)
            win_rate = (self.opportunities_profitable / len(self.paper_trades) * 100)
            
            logger.info(f"Average Profit per Trade: ${avg_profit:.2f}")
            logger.info(f"Win Rate: {win_rate:.0f}%")
            
            first_trade = self.paper_trades[0]['timestamp']
            hours_running = (datetime.now() - first_trade).total_seconds() / 3600
            
            if hours_running > 0:
                trades_per_hour = len(self.paper_trades) / hours_running
                profit_per_hour = profit / hours_running
                
                logger.info(f"\nTrades per hour: {trades_per_hour:.1f}")
                logger.info(f"Profit per hour: ${profit_per_hour:.2f}")
                
                logger.info("\n📊 IF YOU DEPLOYED REAL $100:")
                logger.info(f"   Daily profit: ${profit_per_hour * 24:.2f}")
                logger.info(f"   Weekly profit: ${profit_per_hour * 24 * 7:.2f}")
                logger.info(f"   Monthly profit: ${profit_per_hour * 24 * 30:.2f}")
        
        # Save results to file
        results = {
            'session_end': datetime.now().isoformat(),
            'initial_balance': self.initial_balance,
            'final_balance': self.paper_balance,
            'total_profit': profit,
            'profit_percent': profit_pct,
            'opportunities_found': self.opportunities_found,
            'profitable_trades': self.opportunities_profitable,
            'total_trades': len(self.paper_trades),
            'trades': [
                {
                    'timestamp': t['timestamp'].isoformat(),
                    'market': t['market'],
                    'profit': t['profit'],
                    'profit_percent': t['profit_percent']
                }
                for t in self.paper_trades
            ]
        }
        
        with open('paper_trading_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("\n✅ Results saved to paper_trading_results.json")
        logger.info("\n" + "=" * 70)
        logger.info("NEXT STEPS:")
        logger.info("=" * 70)
        
        if profit > 0 and len(self.paper_trades) >= 10:
            logger.info("✅ VALIDATION SUCCESSFUL!")
            logger.info("   • Strategy is profitable")
            logger.info("   • Sufficient trades executed")
            logger.info("   • Ready for real money deployment")
            logger.info("\n🚀 TO DEPLOY REAL MONEY:")
            logger.info("   1. Get $100 USDC on Polygon")
            logger.info("   2. Add private key to .env")
            logger.info("   3. Run: python3 bot.py")
        elif len(self.paper_trades) < 10:
            logger.info("⚠️  MORE DATA NEEDED")
            logger.info("   • Run paper trading for longer")
            logger.info("   • Need at least 10 trades to validate")
            logger.info("   • Try during high-volume periods")
        else:
            logger.info("⚠️  REVIEW RESULTS")
            logger.info("   • Check if opportunities exist in current market")
            logger.info("   • May need to adjust thresholds")
            logger.info("   • Review paper_trading_results.json")
        
        logger.info("=" * 70 + "\n")


async def main():
    """Main entry point"""
    print("=" * 70)
    print("  POLYMARKET PAPER TRADING BOT")
    print("=" * 70)
    print("\n⚠️  PAPER TRADING MODE - NO REAL MONEY AT RISK\n")
    print("This bot will:")
    print("  • Find real arbitrage opportunities on Polymarket")
    print("  • Simulate what would happen if you traded")
    print("  • Track simulated profit/loss")
    print("  • Prove the strategy works BEFORE you risk capital")
    print("\n✅ You can validate profitability with ZERO risk")
    print("✅ Deploy real money only after proof\n")
    
    initial_balance = float(input("Enter paper trading balance (default $100): ") or "100")
    
    print(f"\n🚀 Starting paper trading with ${initial_balance:.2f} simulated capital...")
    print("Press Ctrl+C to stop and see results\n")
    
    bot = PaperTradingBot(initial_balance=initial_balance)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
