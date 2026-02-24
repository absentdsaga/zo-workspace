#!/usr/bin/env python3
"""
Polymarket Longshot Bot - "Buy Everything Under 5¢" Strategy
Based on real trader who turned $150 → $104K

STRATEGY: 
- Buy ANY outcome priced < 5¢
- No analysis, just volume on obscure/low-liquidity markets
- Wait for black swans to hit
- Paper trading mode (set PAPER_TRADE=False for mainnet)

Real example wins:
- S&P direction: $4.55 → $2,531 (55,500% ROI)
- Syria strikes: $16.78 → $2,324 (13,800% ROI)
"""
import requests
import json
import time
from datetime import datetime
from py_clob_client.client import ClobClient

# ==================== CONFIGURATION ====================
PAPER_TRADE = True  # Set to False for MAINNET execution
MAX_PRICE_CENTS = 0.05  # Buy anything under 5 cents
BET_SIZE_PER_OUTCOME = 5  # $5 per cheap outcome
MIN_MARKET_VOLUME = 100  # Minimum $100 volume (avoid dead markets)
CHECK_INTERVAL = 300  # Check every 5 minutes
MAX_DAILY_SPEND = 50  # Max $50/day on new positions

# Mainnet config (only used if PAPER_TRADE=False)
PRIVATE_KEY = ""  # YOUR POLYMARKET WALLET PRIVATE KEY
CHAIN_ID = 137  # Polygon mainnet

# ==================== INITIALIZATION ====================
clob_client = ClobClient("https://clob.polymarket.com")

# Track what we've bought
positions = {}
daily_spend = 0
last_reset = datetime.now().date()

def log(message, level="INFO"):
    """Structured logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode = "[PAPER]" if PAPER_TRADE else "[LIVE]"
    print(f"{timestamp} {mode} [{level}] {message}")

def reset_daily_limits():
    """Reset daily spend at midnight"""
    global daily_spend, last_reset
    today = datetime.now().date()
    if today != last_reset:
        log(f"Daily reset: Spent ${daily_spend:.2f} yesterday")
        daily_spend = 0
        last_reset = today

def get_all_markets():
    """Fetch all active markets from Polymarket"""
    try:
        resp = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "active": "true",
                "closed": "false", 
                "limit": 200  # Get more markets
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            markets = resp.json()
            log(f"Fetched {len(markets)} active markets")
            return markets
        else:
            log(f"API error: {resp.status_code}", "ERROR")
            return []
    except Exception as e:
        log(f"Error fetching markets: {e}", "ERROR")
        return []

def find_cheap_outcomes(markets):
    """Find ALL outcomes priced < 5 cents"""
    opportunities = []
    
    for market in markets:
        try:
            # Get market metadata
            question = market.get('question', 'Unknown')
            slug = market.get('slug', '')
            volume = float(market.get('volume', 0))
            
            # Skip low volume markets
            if volume < MIN_MARKET_VOLUME:
                continue
            
            # Get outcomes and prices
            outcomes_str = market.get('outcomes', '[]')
            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
            
            prices_str = market.get('outcomePrices', '[]')
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
            
            if not outcomes or not prices:
                continue
            
            # Check each outcome
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                
                # FOUND A CHEAP ONE!
                if price < MAX_PRICE_CENTS and price > 0:
                    # Get token ID for this outcome
                    tokens_str = market.get('clobTokenIds', '[]')
                    tokens = json.loads(tokens_str) if isinstance(tokens_str, str) else tokens_str
                    
                    token_id = tokens[i] if i < len(tokens) else None
                    
                    opportunities.append({
                        'question': question,
                        'slug': slug,
                        'outcome': outcome,
                        'price': price,
                        'volume': volume,
                        'token_id': token_id,
                        'expected_roi': (1.0 / price - 1) * 100  # % gain if it hits
                    })
        
        except Exception as e:
            continue
    
    return opportunities

def execute_trade(opp, amount):
    """Execute trade (paper or mainnet)"""
    global daily_spend
    
    if PAPER_TRADE:
        # PAPER TRADE - just log it
        shares = amount / opp['price']
        
        log(f"📝 PAPER TRADE: Buy {shares:.1f} shares of '{opp['outcome']}'")
        log(f"   Market: {opp['question'][:60]}")
        log(f"   Price: ${opp['price']:.4f} (${opp['price']*100:.2f}¢)")
        log(f"   Cost: ${amount:.2f}")
        log(f"   Potential: ${shares:.2f} if wins ({opp['expected_roi']:.0f}% ROI)")
        log(f"   URL: https://polymarket.com/event/{opp['slug']}")
        
        # Track position
        positions[opp['slug'] + '_' + opp['outcome']] = {
            'cost': amount,
            'shares': shares,
            'price': opp['price'],
            'question': opp['question'],
            'outcome': opp['outcome'],
            'bought_at': datetime.now()
        }
        
        daily_spend += amount
        return True
        
    else:
        # MAINNET EXECUTION
        log(f"🔴 MAINNET: Executing real trade!", "WARN")
        
        # TODO: Implement actual Polymarket API execution
        # This requires:
        # 1. Sign transaction with PRIVATE_KEY
        # 2. Call clob_client.create_order()
        # 3. Handle order confirmation
        
        log("⚠️  Mainnet execution not yet implemented!", "ERROR")
        return False

def show_portfolio():
    """Display current positions"""
    if not positions:
        log("No positions yet")
        return
    
    total_invested = sum(p['cost'] for p in positions.values())
    
    log("=" * 80)
    log("💼 CURRENT PORTFOLIO")
    log("=" * 80)
    log(f"Total positions: {len(positions)}")
    log(f"Total invested: ${total_invested:.2f}")
    log(f"Daily spend: ${daily_spend:.2f} / ${MAX_DAILY_SPEND}")
    log("")
    
    for key, pos in list(positions.items())[:10]:  # Show first 10
        days_held = (datetime.now() - pos['bought_at']).days
        log(f"• {pos['outcome']}: {pos['shares']:.1f} shares @ ${pos['price']:.4f}")
        log(f"  {pos['question'][:60]}")
        log(f"  Held: {days_held} days | Potential: ${pos['shares']:.2f}")
        log("")

def main():
    log("=" * 80)
    log("🎰 POLYMARKET LONGSHOT BOT")
    log("=" * 80)
    log(f"Strategy: Buy everything under {MAX_PRICE_CENTS*100:.0f}¢")
    log(f"Bet size: ${BET_SIZE_PER_OUTCOME} per outcome")
    log(f"Daily limit: ${MAX_DAILY_SPEND}")
    log(f"Mode: {'PAPER TRADING' if PAPER_TRADE else '🔴 MAINNET 🔴'}")
    log("=" * 80)
    log("")
    
    if not PAPER_TRADE and not PRIVATE_KEY:
        log("ERROR: PRIVATE_KEY required for mainnet!", "ERROR")
        return
    
    scan_count = 0
    
    while True:
        try:
            reset_daily_limits()
            scan_count += 1
            
            log(f"🔍 Scan #{scan_count}: Searching for cheap outcomes...")
            
            # Get all markets
            markets = get_all_markets()
            
            if not markets:
                log("No markets found, retrying...", "WARN")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # Find cheap outcomes
            opportunities = find_cheap_outcomes(markets)
            
            if opportunities:
                # Sort by expected ROI (highest first)
                opportunities.sort(key=lambda x: x['expected_roi'], reverse=True)
                
                log(f"✅ Found {len(opportunities)} outcomes under {MAX_PRICE_CENTS*100:.0f}¢!")
                log("")
                
                # Show top 10
                for i, opp in enumerate(opportunities[:10], 1):
                    log(f"{i}. {opp['price']*100:.2f}¢ - {opp['outcome']}")
                    log(f"   {opp['question'][:60]}")
                    log(f"   ROI if wins: {opp['expected_roi']:.0f}% | Vol: ${opp['volume']:,.0f}")
                    log("")
                
                # Execute trades on new opportunities
                executed = 0
                for opp in opportunities:
                    # Check if we already bought this
                    position_key = opp['slug'] + '_' + opp['outcome']
                    if position_key in positions:
                        continue
                    
                    # Check daily limit
                    if daily_spend + BET_SIZE_PER_OUTCOME > MAX_DAILY_SPEND:
                        log(f"⚠️  Daily limit reached (${daily_spend:.2f}/${MAX_DAILY_SPEND})")
                        break
                    
                    # EXECUTE TRADE
                    if execute_trade(opp, BET_SIZE_PER_OUTCOME):
                        executed += 1
                        time.sleep(1)  # Rate limit
                
                if executed > 0:
                    log(f"✅ Executed {executed} new trades")
                    log("")
            else:
                log(f"No opportunities found under {MAX_PRICE_CENTS*100:.0f}¢")
            
            # Show portfolio
            show_portfolio()
            
            log(f"💤 Sleeping {CHECK_INTERVAL}s until next scan...")
            log("")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("\n👋 Shutting down...")
            show_portfolio()
            break
        except Exception as e:
            log(f"Error in main loop: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            time.sleep(60)

if __name__ == "__main__":
    main()
