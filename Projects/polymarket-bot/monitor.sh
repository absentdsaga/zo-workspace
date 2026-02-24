#!/bin/bash
# Main monitoring script - Choose your monitoring style

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Polymarket Bot Monitoring Options"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose your monitoring style:"
echo ""
echo "1) 📊 Live Stats Dashboard (recommended)"
echo "   - Real-time price tracking"
echo "   - Opportunity counter"
echo "   - Best spread tracker"
echo "   - Profit trend chart"
echo ""
echo "2) 📋 Simple Log Monitor"
echo "   - Raw bot output"
echo "   - Color-coded alerts"
echo "   - Good for debugging"
echo ""
echo "3) Exit"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting Live Dashboard..."
        /usr/local/bin/python3 stats_dashboard.py
        ;;
    2)
        echo ""
        echo "Starting Log Monitor..."
        ./monitor_hybrid.sh
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
