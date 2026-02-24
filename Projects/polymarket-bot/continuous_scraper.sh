#!/bin/bash
# Continuous scraper - keeps running update_all.py until it stops finding new data

cd /tmp/poly_data

echo "==================================================================="
echo "🔁 CONTINUOUS POLYMARKET BLOCKCHAIN SCRAPER"
echo "==================================================================="
echo "Will keep running until no new data is found"
echo ""

iterations=0
max_iterations=100  # Safety limit

while [ $iterations -lt $max_iterations ]; do
    iterations=$((iterations + 1))

    echo "─────────────────────────────────────────────────────────────────"
    echo "📊 Iteration #$iterations"
    echo "─────────────────────────────────────────────────────────────────"

    # Get current counts
    if [ -f "goldsky/orderFilled.csv" ]; then
        before=$(wc -l < goldsky/orderFilled.csv)
    else
        before=0
    fi

    # Run scraper
    echo "🔄 Running scraper..."
    uv run python update_all.py 2>&1 | tail -20

    # Get new counts
    if [ -f "goldsky/orderFilled.csv" ]; then
        after=$(wc -l < goldsky/orderFilled.csv)
    else
        after=0
    fi

    new_records=$((after - before))

    echo ""
    echo "📈 Results:"
    echo "   Before: $before orders"
    echo "   After: $after orders"
    echo "   New: $new_records orders"
    echo ""

    # If no new records, we're done
    if [ $new_records -eq 0 ]; then
        echo "✅ No new data found - scraping complete!"
        break
    fi

    echo "⏳ Found $new_records new records, continuing..."
    sleep 2
done

if [ $iterations -eq $max_iterations ]; then
    echo "⚠️  Reached max iterations ($max_iterations)"
fi

echo ""
echo "==================================================================="
echo "✅ CONTINUOUS SCRAPING COMPLETE"
echo "==================================================================="

# Show final stats
if [ -f "goldsky/orderFilled.csv" ]; then
    total_orders=$(wc -l < goldsky/orderFilled.csv)
    echo "📊 Total blockchain events: $total_orders"
fi

if [ -f "processed/trades.csv" ]; then
    total_trades=$(wc -l < processed/trades.csv)
    echo "📊 Total processed trades: $total_trades"
fi

if [ -f "markets.csv" ]; then
    total_markets=$(wc -l < markets.csv)
    echo "📊 Total markets: $total_markets"
fi

echo ""
echo "✅ Run real_data_analyzer.py to analyze the data!"
