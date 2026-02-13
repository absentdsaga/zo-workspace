#!/usr/bin/env python3
"""
Add Shocked extraction to bot watchlist
Merges tokens from dated extraction folder into active watchlist
"""

import sys
import json
from pathlib import Path
from datetime import datetime

WATCHLIST_PATH = '/tmp/shocked-watchlist.json'

def load_watchlist():
    """Load existing watchlist"""
    try:
        with open(WATCHLIST_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_extraction(extraction_dir):
    """Load tokens from extraction directory"""
    tokens = []
    info_file = extraction_dir / 'tokens-with-info.txt'
    
    with open(info_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 4:
                addr, symbol, fdv, gain = parts
                gain_num = int(gain.replace('%', ''))
                
                # Determine priority
                if gain_num >= 200:
                    priority = 'high'
                elif gain_num >= 50:
                    priority = 'medium'
                else:
                    priority = 'low'
                
                tokens.append({
                    'address': addr,
                    'symbol': symbol,
                    'fdv': fdv,
                    'gain': gain_num,
                    'priority': priority
                })
    
    return tokens

def merge_to_watchlist(tokens, source_date):
    """Merge tokens into watchlist, avoiding duplicates"""
    watchlist = load_watchlist()
    existing_addrs = {item[0] for item in watchlist}
    
    added = 0
    skipped = 0
    
    for token in tokens:
        if token['address'] not in existing_addrs:
            watchlist.append([
                token['address'],
                {
                    'address': token['address'],
                    'symbol': token['symbol'],
                    'addedAt': int(datetime.now().timestamp() * 1000),
                    'source': f'shocked-pdf-{source_date}',
                    'notes': f"FDV: {token['fdv']}, Gain: {token['gain']}%",
                    'priority': token['priority']
                }
            ])
            added += 1
            print(f"  ✅ {token['symbol']:15} ({token['priority']:6}) - {token['gain']}% gain")
        else:
            skipped += 1
    
    # Save updated watchlist
    with open(WATCHLIST_PATH, 'w') as f:
        json.dump(watchlist, f, indent=2)
    
    return added, skipped, len(watchlist)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add-to-watchlist.py <YYYY-MM-DD>")
        print("\nExample: python3 add-to-watchlist.py 2026-02-12")
        sys.exit(1)
    
    date_str = sys.argv[1]
    extraction_dir = Path(__file__).parent / date_str
    
    if not extraction_dir.exists():
        print(f"❌ Extraction directory not found: {extraction_dir}")
        sys.exit(1)
    
    print(f"📥 Loading extraction from {date_str}...")
    tokens = load_extraction(extraction_dir)
    
    print(f"🔄 Merging {len(tokens)} tokens into watchlist...")
    added, skipped, total = merge_to_watchlist(tokens, date_str)
    
    print(f"\n✅ Watchlist updated!")
    print(f"   Added: {added} new tokens")
    print(f"   Skipped: {skipped} duplicates")
    print(f"   Total in watchlist: {total}")
    
    print(f"\n💡 Restart bot to load new tokens:")
    print(f"   kill $(pgrep -f paper-trade-bot.ts)")
    print(f"   cd /home/workspace/Projects/survival-agent")
    print(f"   source ~/.zo_secrets && nohup bun run testing/paper-trade-bot.ts > /tmp/paper-bot.log 2>&1 &")

if __name__ == '__main__':
    main()
