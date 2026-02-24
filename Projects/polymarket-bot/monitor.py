#!/usr/bin/env python3
"""
Real-time monitoring dashboard for Polymarket bot
View performance metrics in your terminal
"""

import os
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def parse_log_file(log_file='bot.log'):
    """Parse bot log file for metrics"""
    trades = []
    current_balance = 100.0
    
    if not os.path.exists(log_file):
        return trades, current_balance
    
    with open(log_file, 'r') as f:
        for line in f:
            # Parse trade executions
            if 'ARB FOUND' in line or 'Position opened' in line:
                trades.append({
                    'timestamp': datetime.now(),
                    'type': 'arbitrage'
                })
            
            # Parse balance updates
            if 'Balance:' in line:
                try:
                    balance_str = line.split('Balance: $')[1].split('|')[0].strip()
                    current_balance = float(balance_str)
                except:
                    pass
    
    return trades, current_balance

def calculate_metrics(trades, current_balance, initial_balance=100.0):
    """Calculate performance metrics"""
    profit = current_balance - initial_balance
    profit_pct = (profit / initial_balance * 100) if initial_balance > 0 else 0
    
    # Calculate hourly/daily rates
    if trades:
        first_trade_time = trades[0]['timestamp']
        hours_running = (datetime.now() - first_trade_time).total_seconds() / 3600
        
        trades_per_hour = len(trades) / hours_running if hours_running > 0 else 0
        profit_per_hour = profit / hours_running if hours_running > 0 else 0
    else:
        trades_per_hour = 0
        profit_per_hour = 0
        hours_running = 0
    
    return {
        'profit': profit,
        'profit_pct': profit_pct,
        'trades': len(trades),
        'trades_per_hour': trades_per_hour,
        'profit_per_hour': profit_per_hour,
        'hours_running': hours_running,
        'current_balance': current_balance
    }

def display_dashboard(metrics):
    """Display ASCII dashboard"""
    clear_screen()
    
    print("=" * 70)
    print("  POLYMARKET BOT DASHBOARD".center(70))
    print("=" * 70)
    print()
    
    # Main metrics
    profit_indicator = "📈" if metrics['profit'] >= 0 else "📉"
    color = "\033[92m" if metrics['profit'] >= 0 else "\033[91m"
    reset = "\033[0m"
    
    print(f"  {profit_indicator}  PROFIT & LOSS")
    print(f"      Current Balance: ${metrics['current_balance']:.2f}")
    print(f"      P&L: {color}${metrics['profit']:+.2f} ({metrics['profit_pct']:+.1f}%){reset}")
    print()
    
    # Trading activity
    print("  📊  TRADING ACTIVITY")
    print(f"      Total Trades: {metrics['trades']}")
    print(f"      Trades/Hour: {metrics['trades_per_hour']:.1f}")
    print(f"      Profit/Hour: ${metrics['profit_per_hour']:.2f}")
    print()
    
    # Runtime
    print("  ⏱️   RUNTIME")
    hours = int(metrics['hours_running'])
    minutes = int((metrics['hours_running'] - hours) * 60)
    print(f"      Running for: {hours}h {minutes}m")
    print()
    
    # Projections
    if metrics['hours_running'] > 0:
        daily_profit = metrics['profit_per_hour'] * 24
        weekly_profit = daily_profit * 7
        monthly_profit = daily_profit * 30
        
        print("  🎯  PROJECTIONS (if rate continues)")
        print(f"      Daily: ${daily_profit:.2f}")
        print(f"      Weekly: ${weekly_profit:.2f}")
        print(f"      Monthly: ${monthly_profit:.2f}")
        print()
    
    # Status
    print("  ✅  STATUS")
    if metrics['trades'] == 0:
        print("      Waiting for opportunities...")
    elif metrics['profit'] > 0:
        print("      Profitably trading! ✨")
    else:
        print("      Active, monitoring performance")
    
    print()
    print("=" * 70)
    print(f"  Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Press Ctrl+C to exit")
    print("=" * 70)

def main():
    """Main monitoring loop"""
    print("🚀 Starting Polymarket Bot Monitor...")
    print("Watching bot.log for updates...")
    time.sleep(2)
    
    try:
        while True:
            trades, balance = parse_log_file()
            metrics = calculate_metrics(trades, balance)
            display_dashboard(metrics)
            time.sleep(5)  # Update every 5 seconds
    
    except KeyboardInterrupt:
        print("\n\n✋ Monitor stopped")

if __name__ == "__main__":
    main()
