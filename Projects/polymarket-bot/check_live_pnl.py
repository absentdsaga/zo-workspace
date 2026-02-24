#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime

def get_orderbook(token_id):
    """Get orderbook from CLOB API"""
    try:
        url = f'https://clob.polymarket.com/book?token_id={token_id}'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            # Get best bid price (what we can sell for)
            if data.get('bids') and len(data['bids']) > 0:
                return float(data['bids'][0]['price'])
    except Exception as e:
        print(f"    Error getting orderbook: {e}")
    return None

# Load positions
with open('paper_positions_30_40.json', 'r') as f:
    positions = json.load(f)

position_details = []
total_unrealized_pnl = 0
total_invested = 0

print("📊 LIVE P&L ANALYSIS")
print("=" * 80)

for pos in positions['open']:
    token_id = pos['token_id']
    
    # Get current best bid price
    current_price = get_orderbook(token_id)
    
    if current_price is None:
        print(f"  ⚠️  No liquidity for {pos['question'][:50]}...")
        continue
    
    # Calculate P&L
    entry_price = pos['price']
    bet_size = pos['bet_size']
    cost = pos['cost']
    
    # Current value = bet_size * current_price (what we'd get if we sold now)
    current_value = bet_size * current_price
    unrealized_pnl = current_value - cost
    pnl_pct = (unrealized_pnl / cost) * 100
    
    total_unrealized_pnl += unrealized_pnl
    total_invested += cost
    
    position_details.append({
        'question': pos['question'],
        'outcome': pos['outcome'],
        'entry': entry_price,
        'current': current_price,
        'cost': cost,
        'value': current_value,
        'pnl': unrealized_pnl,
        'pnl_pct': pnl_pct
    })

if not position_details:
    print("\n⚠️  Could not fetch any market data")
    exit(1)

# Group by question
grouped = {}
for detail in position_details:
    key = (detail['question'], detail['outcome'])
    if key not in grouped:
        grouped[key] = {
            'question': detail['question'],
            'outcome': detail['outcome'],
            'positions': [],
            'total_cost': 0,
            'total_value': 0,
            'total_pnl': 0
        }
    grouped[key]['positions'].append(detail)
    grouped[key]['total_cost'] += detail['cost']
    grouped[key]['total_value'] += detail['value']
    grouped[key]['total_pnl'] += detail['pnl']

# Print grouped results
for key, group in sorted(grouped.items(), key=lambda x: x[1]['total_pnl'], reverse=True):
    avg_entry = sum(p['entry'] for p in group['positions']) / len(group['positions'])
    avg_current = sum(p['current'] for p in group['positions']) / len(group['positions'])
    total_pnl_pct = (group['total_pnl'] / group['total_cost']) * 100
    price_change = ((avg_current - avg_entry) / avg_entry) * 100
    
    emoji = "🟢" if group['total_pnl'] > 0 else "🔴" if group['total_pnl'] < 0 else "⚪"
    
    print(f"\n{emoji} {group['question'][:65]}")
    print(f"  Outcome: {group['outcome']}")
    print(f"  Positions: {len(group['positions'])}")
    print(f"  Avg Entry: {avg_entry:.3f} → Current: {avg_current:.3f} ({price_change:+.1f}%)")
    print(f"  Invested: ${group['total_cost']:.2f} → Value: ${group['total_value']:.2f}")
    print(f"  P&L: ${group['total_pnl']:+.2f} ({total_pnl_pct:+.1f}%)")

print("\n" + "=" * 80)
print(f"💰 TOTAL UNREALIZED P&L: ${total_unrealized_pnl:+.2f}")
print(f"📊 Total Invested: ${total_invested:.2f}")
print(f"📈 Overall Return: {(total_unrealized_pnl / total_invested * 100):+.1f}%")

# Calculate true bankroll
with open('paper_stats_30_40.json', 'r') as f:
    stats = json.load(f)
    
unrealized_value = total_invested + total_unrealized_pnl
free_cash = stats['current_bankroll']
true_bankroll = free_cash + unrealized_value

print(f"\n💵 TRUE BANKROLL:")
print(f"  Free Cash: ${free_cash:.2f}")
print(f"  Position Value: ${unrealized_value:.2f}")
print(f"  📊 Total Bankroll: ${true_bankroll:.2f}")
print(f"  {'🟢 Profit' if true_bankroll > 1000 else '🔴 Loss'}: ${true_bankroll - 1000:+.2f} ({((true_bankroll - 1000) / 1000 * 100):+.1f}%)")
