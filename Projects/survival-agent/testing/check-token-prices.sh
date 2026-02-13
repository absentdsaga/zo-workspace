#!/bin/bash
# Quick check if token prices are actually moving on-chain

echo "🔍 Checking if token prices are real or cached..."
echo ""

# Extract current positions from log
TOKENS=$(tail -200 /tmp/paper-trade-final.log 2>/dev/null | grep -a "Token:" | tail -3)

echo "Current positions:"
echo "$TOKENS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# For each token, check DexScreener twice with 10 second gap
echo "📊 Testing price updates (checking twice, 10 seconds apart)..."
echo ""

# Awakening
echo "1️⃣  Awakening (Efn6UJbp...):"
ADDR1="Efn6UJbpzLNqW7qKmkCPEwR38GLvvPP3Wa5yCjZ4pump"
PRICE1=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR1" | jq -r '.pairs[0].priceUsd // "null"')
echo "   First check:  $$PRICE1"
sleep 10
PRICE1B=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR1" | jq -r '.pairs[0].priceUsd // "null"')
echo "   Second check: $$PRICE1B"
if [ "$PRICE1" = "$PRICE1B" ]; then
  echo "   ⚠️  EXACT SAME PRICE - likely cached/stale data"
else
  echo "   ✅ Price updated"
fi
echo ""

# Hot dog
echo "2️⃣  Hot dog (57KoEZXm...):"
ADDR2="57KoEZXmjCRCbGHqaFqv2GzB3eNa4VY9V3UKNhUYpump"
PRICE2=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR2" | jq -r '.pairs[0].priceUsd // "null"')
echo "   First check:  $$PRICE2"
sleep 10
PRICE2B=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR2" | jq -r '.pairs[0].priceUsd // "null"')
echo "   Second check: $$PRICE2B"
if [ "$PRICE2" = "$PRICE2B" ]; then
  echo "   ⚠️  EXACT SAME PRICE - likely cached/stale data"
else
  echo "   ✅ Price updated"
fi
echo ""

# Preguntale
echo "3️⃣  Preguntale (...):"
ADDR3="BcbYD2bXg9Q3sCAnDhm4EpqHVYjdexH4rjUUNJnpump"
PRICE3=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR3" | jq -r '.pairs[0].priceUsd // "null"')
echo "   First check:  $$PRICE3"
sleep 10
PRICE3B=$(curl -s "https://api.dexscreener.com/latest/dex/tokens/$ADDR3" | jq -r '.pairs[0].priceUsd // "null"')
echo "   Second check: $$PRICE3B"
if [ "$PRICE3" = "$PRICE3B" ]; then
  echo "   ⚠️  EXACT SAME PRICE - likely cached/stale data"
else
  echo "   ✅ Price updated"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 DIAGNOSIS:"
echo ""
echo "If all 3 tokens show EXACT SAME PRICE on both checks:"
echo "  → DexScreener is returning cached data (not real-time)"
echo "  → Token is likely delisted/rugged (no active trading)"
echo "  → Exit logic won't trigger because price never changes"
echo ""
echo "If prices vary between checks:"
echo "  → API is working correctly"
echo "  → Token is actively trading"
echo "  → Exit logic should work when thresholds are met"
echo ""
