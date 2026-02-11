#!/bin/bash
# Quick test runner for spatial-worlds multiplayer sync

echo "🎮 SPATIAL WORLDS - QUICK TEST"
echo "================================"
echo ""

# Check if server is running
echo "🔍 Checking server status..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running!"
    echo ""
    echo "Please start the server first:"
    echo "  cd Skills/spatial-worlds"
    echo "  bun run dev"
    echo ""
    exit 1
fi

echo ""
echo "🚀 Starting automated tests..."
echo ""

cd "$(dirname "$0")"
bun run test:report

exit $?
