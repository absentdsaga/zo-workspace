#!/usr/local/bin/python3
"""
Polymarket Longshot Bot V2 - VOLATILE LONGSHOTS ONLY
Strategy: Buy cheap outcomes that are ACTUALLY MOVING (not frozen)

Key improvements:
- Only buys markets with proven 24h price volatility
- Filters out dead markets near resolution
- Tracks position performance with live P&L
- Auto-exits frozen positions
"""
import requests
import json
import time
from datetime import datetime, timedelta

# ==================== CONFIGURATION ====================
PAPER_TRADE = True  # Set to False for MAINNET execution
MAX_PRICE_CENTS = 0.05  # Buy anything under 5 cents
BET_SIZE_PER_OUTCOME = 5  # $5 per cheap outcome
MIN_MARKET_VOLUME = 1000  # Minimum $1k volume (increased from $100)
CHECK_INTERVAL = 600  # Check every 10 minutes (slower to allow volatility checks)
MAX_DAILY_SPEND = 50  # Max $50/day on new positions

# Volatility filters
MIN_VOLATILITY_RANGE = 0.003  # Must move at least 0.3¢ in 24h
MIN_VOLATILITY_STD = 0.001  # Min standard deviation
MIN_DAYS_UNTIL_END = 14  # Skip markets ending in < 2 weeks
MIN_HISTORY_POINTS = 10  # Need at least 10 data points to assess volatility

# Auto-exit frozen positions
FREEZE_CHECK_HOURS = 12  # Check if position frozen after 12h
FREEZE_THRESHOLD_RANGE = 0.001  # If price range < 0.1¢ in 12h, consider frozen

# Mainnet config (only used if PAPER_TRADE=False)
PRIVATE_KEY = ""  # YOUR POLYMARKET WALLET PRIVATE KEY
CHAIN_ID = 137  # Polygon mainnet

# ==================== STATE ====================
positions = {}  # Active positions
frozen_positions = {}  # Positions we've exited due to freeze
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

def get_market_history(token_id, hours=24):
    """Fetch recent price history"""
    try:
        end_time = int(time.time())
        start_time = end_time - (hours * 3600)
        
        resp = requests.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": token_id,
                "startTs": start_time,
                "endTs": end_time,
                "interval": "1h"
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get('history', [])
    except:
        pass
    
    return []

def calculate_volatility(price_history):
    """Calculate price volatility metrics"""
    if len(price_history) < MIN_HISTORY_POINTS:
        return None
    
    prices = [float(h['p']) for h in price_history if 'p' in h]
    
    if len(prices) < MIN_HISTORY_POINTS:
        return None
    
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    std_dev = variance ** 0.5
    price_range = max(prices) - min(prices)
    
    return {
        'std_dev': std_dev,
        'range': price_range,
        'min': min(prices),
        'max': max(prices),
        'current': prices[-1] if prices else 0,
        'data_points': len(prices)
    }

def get_all_markets():
    """Fetch active markets from Polymarket"""
    try:
        resp = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "active": "true",
                "closed": "false",
                "limit": 200
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

def find_volatile_longshots(markets):
    """Find cheap outcomes with PROVEN volatility"""
    opportunities = []
    checked = 0
    
    for market in markets:
        try:
            question = market.get('question', 'Unknown')
            slug = market.get('slug', '')
            volume = float(market.get('volume', 0))
            
            # Skip low volume
            if volume < MIN_MARKET_VOLUME:
                continue
            
            # Check end date
            end_date_str = market.get('endDate', '')
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days_until_end = (end_date - datetime.now(end_date.tzinfo)).days
                    
                    if days_until_end < MIN_DAYS_UNTIL_END:
                        continue
                except:
                    pass
            
            # Get outcomes and prices
            outcomes_str = market.get('outcomes', '[]')
            outcomes = json.loads(outcomes_str) if isinstance(outcomes_str, str) else outcomes_str
            
            prices_str = market.get('outcomePrices', '[]')
            prices = json.loads(prices_str) if isinstance(prices_str, str) else prices_str
            
            tokens_str = market.get('clobTokenIds', '[]')
            tokens = json.loads(tokens_str) if isinstance(tokens_str, str) else tokens_str
            
            if not outcomes or not prices:
                continue
            
            # Check each outcome
            for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                price = float(price_str)
                
                # Only longshots
                if price >= MAX_PRICE_CENTS or price <= 0:
                    continue
                
                checked += 1
                
                token_id = tokens[i] if i < len(tokens) else None
                if not token_id:
                    continue
                
                # Fetch price history
                history = get_market_history(token_id, hours=24)
                
                if not history:
                    continue
                
                # Calculate volatility
                vol = calculate_volatility(history)
                
                if not vol:
                    continue
                
                # FILTER: Must have actual movement
                if vol['std_dev'] < MIN_VOLATILITY_STD and vol['range'] < MIN_VOLATILITY_RANGE:
                    continue
                
                # This is a LIVE longshot!
                opportunities.append({
                    'question': question,
                    'slug': slug,
                    'outcome': outcome,
                    'price': price,
                    'volume': volume,
                    'token_id': token_id,
                    'volatility': vol,
                    'end_date': end_date_str,
                    'expected_roi': (1.0 / price - 1) * 100
                })
                
                # Rate limit
                time.sleep(0.2)
            
            # Progress update
            if checked % 20 == 0 and checked > 0:
                log(f"Checked {checked} longshots, found {len(opportunities)} volatile ones...")
        
        except Exception as e:
            continue
    
    log(f"Total checked: {checked} longshots")
    return opportunities

def check_position_frozen(position):
    """Check if a position has frozen (no price movement)"""
    token_id = position.get('token_id')
    if not token_id:
        return False
    
    # Get recent history
    history = get_market_history(token_id, hours=FREEZE_CHECK_HOURS)
    vol = calculate_volatility(history)
    
    if not vol:
        return True  # No data = probably frozen
    
    # If range is tiny, it's frozen
    return vol['range'] < FREEZE_THRESHOLD_RANGE

def execute_trade(opp, amount):
    """Execute trade (paper or mainnet)"""
    global daily_spend
    
    if PAPER_TRADE:
        shares = amount / opp['price']
        vol = opp['volatility']
        
        log(f"📝 PAPER TRADE: Buy {shares:.1f} shares of '{opp['outcome']}'")
        log(f"   Market: {opp['question'][:60]}")
        log(f"   Price: ${opp['price']:.4f} (${opp['price']*100:.2f}¢)")
        log(f"   Cost: ${amount:.2f}")
        log(f"   24h Volatility: {vol['min']*100:.2f}¢ → {vol['max']*100:.2f}¢ (Δ{vol['range']*100:.2f}¢)")
        log(f"   Potential: ${shares:.2f} if wins ({opp['expected_roi']:.0f}% ROI)")
        log(f"   URL: https://polymarket.com/event/{opp['slug']}")
        
        # Track position
        position_key = opp['slug'] + '_' + opp['outcome']
        positions[position_key] = {
            'cost': amount,
            'shares': shares,
            'buy_price': opp['price'],
            'current_price': opp['price'],
            'question': opp['question'],
            'outcome': opp['outcome'],
            'slug': opp['slug'],
            'token_id': opp['token_id'],
            'bought_at': datetime.now(),
            'last_volatility_check': datetime.now()
        }
        
        daily_spend += amount
        return True
    else:
        log(f"🔴 MAINNET: Executing real trade!", "WARN")
        log("⚠️  Mainnet execution not yet implemented!", "ERROR")
        return False

def check_frozen_positions():
    """Check all positions for freezing, exit if frozen"""
    for key, pos in list(positions.items()):
        # Only check if it's been at least FREEZE_CHECK_HOURS since we bought
        hours_held = (datetime.now() - pos['bought_at']).total_seconds() / 3600
        
        if hours_held < FREEZE_CHECK_HOURS:
            continue
        
        # Check if frozen
        if check_position_frozen(pos):
            log(f"❄️  FROZEN POSITION: {pos['outcome']} - {pos['question'][:50]}", "WARN")
            log(f"   No movement in {FREEZE_CHECK_HOURS}h, exiting position")
            
            # Move to frozen list
            frozen_positions[key] = pos
            del positions[key]

def show_portfolio():
    """Display current positions with P&L"""
    if not positions and not frozen_positions:
        log("No positions yet")
        return
    
    total_invested = sum(p['cost'] for p in positions.values())
    
    log("=" * 80)
    log("💼 ACTIVE PORTFOLIO")
    log("=" * 80)
    log(f"Active positions: {len(positions)}")
    log(f"Frozen positions: {len(frozen_positions)}")
    log(f"Total invested: ${total_invested:.2f}")
    log(f"Daily spend: ${daily_spend:.2f} / ${MAX_DAILY_SPEND}")
    log("")
    
    if positions:
        log("🟢 ACTIVE POSITIONS:")
        for key, pos in list(positions.items())[:10]:
            days_held = (datetime.now() - pos['bought_at']).days
            hours_held = (datetime.now() - pos['bought_at']).total_seconds() / 3600
            
            log(f"• {pos['outcome']}: {pos['shares']:.1f} shares @ ${pos['buy_price']:.4f}")
            log(f"  {pos['question'][:60]}")
            log(f"  Held: {days_held}d {hours_held%24:.0f}h | Potential: ${pos['shares']:.2f}")
            log("")
    
    if frozen_positions:
        log("❄️  FROZEN POSITIONS (Auto-exited):")
        for key, pos in list(frozen_positions.items())[:5]:
            log(f"• {pos['outcome']} - {pos['question'][:50]}")
            log(f"  Reason: No price movement")
            log("")

def main():
    log("=" * 80)
    log("🎰 POLYMARKET LONGSHOT BOT V2 - VOLATILE ONLY")
    log("=" * 80)
    log(f"Strategy: Buy longshots under {MAX_PRICE_CENTS*100:.0f}¢ with proven volatility")
    log(f"Volatility filter: {MIN_VOLATILITY_RANGE*100:.1f}¢ range OR {MIN_VOLATILITY_STD*100:.1f}¢ std dev")
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
            
            log(f"🔍 Scan #{scan_count}: Searching for VOLATILE cheap outcomes...")
            
            # Get all markets
            markets = get_all_markets()
            
            if not markets:
                log("No markets found, retrying...", "WARN")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # Find volatile longshots
            opportunities = find_volatile_longshots(markets)
            
            if opportunities:
                # Sort by volatility range (most volatile first)
                opportunities.sort(key=lambda x: x['volatility']['range'], reverse=True)
                
                log(f"✅ Found {len(opportunities)} VOLATILE outcomes under {MAX_PRICE_CENTS*100:.0f}¢!")
                log("")
                
                # Show top 10
                for i, opp in enumerate(opportunities[:10], 1):
                    vol = opp['volatility']
                    log(f"{i}. {opp['price']*100:.2f}¢ - {opp['outcome']}")
                    log(f"   {opp['question'][:60]}")
                    log(f"   Volatility: {vol['min']*100:.2f}¢→{vol['max']*100:.2f}¢ (Δ{vol['range']*100:.2f}¢)")
                    log(f"   ROI if wins: {opp['expected_roi']:.0f}% | Vol: ${opp['volume']:,.0f}")
                    log("")
                
                # Execute trades on new opportunities
                executed = 0
                for opp in opportunities:
                    # Check if we already have this position
                    position_key = opp['slug'] + '_' + opp['outcome']
                    if position_key in positions or position_key in frozen_positions:
                        continue
                    
                    # Check daily limit
                    if daily_spend + BET_SIZE_PER_OUTCOME > MAX_DAILY_SPEND:
                        log(f"⚠️  Daily limit reached (${daily_spend:.2f}/${MAX_DAILY_SPEND})")
                        break
                    
                    # EXECUTE TRADE
                    if execute_trade(opp, BET_SIZE_PER_OUTCOME):
                        executed += 1
                        time.sleep(1)
                
                if executed > 0:
                    log(f"✅ Executed {executed} new trades")
                    log("")
            else:
                log(f"No volatile opportunities found under {MAX_PRICE_CENTS*100:.0f}¢")
            
            # Check for frozen positions
            if positions:
                log("🔍 Checking positions for freezing...")
                check_frozen_positions()
            
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
