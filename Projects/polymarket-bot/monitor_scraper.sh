#!/bin/bash
# Monitor blockchain scraping progress

while true; do
    clear
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "🔗 POLYMARKET BLOCKCHAIN SCRAPER - LIVE MONITOR"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Check if running
    if ps aux | grep -q "[u]pdate_all.py"; then
        echo "✅ Status: RUNNING"
    else
        echo "❌ Status: STOPPED"
    fi
    
    echo ""
    echo "📊 DATA COLLECTED:"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    # Markets
    if [ -f /tmp/poly_data/markets.csv ]; then
        MARKETS=$(wc -l < /tmp/poly_data/markets.csv)
        SIZE=$(ls -lh /tmp/poly_data/markets.csv | awk '{print $5}')
        echo "  Markets:        $(($MARKETS - 1)) markets ($SIZE)"
    fi
    
    # Orders
    if [ -f /tmp/poly_data/goldsky/orderFilled.csv ]; then
        ORDERS=$(wc -l < /tmp/poly_data/goldsky/orderFilled.csv)
        SIZE=$(ls -lh /tmp/poly_data/goldsky/orderFilled.csv | awk '{print $5}')
        echo "  Orders:         $(($ORDERS - 1)) blockchain events ($SIZE)"
    fi
    
    # Trades
    if [ -f /tmp/poly_data/processed/trades.csv ]; then
        TRADES=$(wc -l < /tmp/poly_data/processed/trades.csv)
        SIZE=$(ls -lh /tmp/poly_data/processed/trades.csv | awk '{print $5}')
        echo "  Processed:      $(($TRADES - 1)) trades ($SIZE)"
    fi
    
    echo ""
    echo "📝 RECENT LOG OUTPUT:"
    echo "───────────────────────────────────────────────────────────────────────────"
    tail -10 /dev/shm/polymarket_scraper.log 2>/dev/null | sed 's/^/  /'
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "Refreshing every 5 seconds... (Ctrl+C to exit)"
    
    sleep 5
done
