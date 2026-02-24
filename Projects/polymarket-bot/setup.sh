#!/bin/bash
# Polymarket Bot Setup Script

echo "🚀 Polymarket Trading Bot Setup"
echo "================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✅ .env file found"
else
    echo "📝 Creating .env file..."
    cat > .env << 'EOFENV'
# Polymarket Bot Configuration
# Get your private key from MetaMask or another Ethereum wallet
# IMPORTANT: This wallet needs USDC on Polygon network

POLYMARKET_PRIVATE_KEY=your_private_key_here

# Optional: Separate funder address if using different wallet for gas
# POLYMARKET_FUNDER=0x...
EOFENV
    echo "⚠️  Please edit .env and add your private key"
    echo ""
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install py-clob-client web3 python-dotenv aiohttp requests

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your POLYMARKET_PRIVATE_KEY"
echo "2. Fund your wallet with USDC on Polygon (minimum $100)"
echo "3. Run: python3 bot.py"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "- Start with small amounts to test ($100-500)"
echo "- Bot uses sum-to-one arbitrage (low risk but requires fast execution)"
echo "- Monitor the first few trades carefully"
echo "- Profits compound - be patient!"
echo ""
