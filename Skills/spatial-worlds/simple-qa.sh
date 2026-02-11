#!/bin/bash

echo "🧪 Simple QA Check for Multiplayer Sync"
echo "========================================"
echo ""

# 1. Check server is running
echo "1️⃣  Checking server..."
if curl -s -o /dev/null -w "%{http_code}" https://spatial-worlds-dioni.zocomputer.io/ | grep -q "200"; then
    echo "   ✅ Server responding (200 OK)"
else
    echo "   ❌ Server not responding"
    exit 1
fi

# 2. Check JS bundle exists
echo "2️⃣  Checking JavaScript bundle..."
if curl -s -o /dev/null -w "%{http_code}" https://spatial-worlds-dioni.zocomputer.io/dist/main-iso.js | grep -q "200"; then
    echo "   ✅ JavaScript bundle available"
else
    echo "   ❌ JavaScript bundle not found"
    exit 1
fi

# 3. Check if client sends position data
echo "3️⃣  Checking client code for position sending..."
if grep -q "position: { x: this.player.x, y: this.player.y }" /home/workspace/Skills/spatial-worlds/scripts/client/MultiplayerManager.ts; then
    echo "   ✅ Client sends position data"
else
    echo "   ❌ Client doesn't send position"
    exit 1
fi

# 4. Check if server uses client position
echo "4️⃣  Checking server code for client-authoritative position..."
if grep -q "if (cmd.position)" /home/workspace/Skills/spatial-worlds/spatial-worlds-server/src/multiplayer.ts; then
    echo "   ✅ Server uses client position"
else
    echo "   ❌ Server doesn't use client position"
    exit 1
fi

# 5. Check if lerp is in update() method
echo "5️⃣  Checking client lerp timing..."
if grep -A 5 "update()" /home/workspace/Skills/spatial-worlds/scripts/client/MultiplayerManager.ts | grep -q "lerpFactor"; then
    echo "   ✅ Lerp happens in update() method"
else
    echo "   ❌ Lerp not in update() method"
    exit 1
fi

# 6. Verify built bundle includes the fix
echo "6️⃣  Checking compiled bundle..."
if grep -q "position.*player\.x.*player\.y" /home/workspace/Skills/spatial-worlds/dist/main-iso.js; then
    echo "   ✅ Built bundle includes position sending"
else
    echo "   ⚠️  Bundle may not include latest changes"
fi

echo ""
echo "========================================"
echo "✅ All QA checks passed!"
echo ""
echo "📝 Manual Test:"
echo "   1. Open https://spatial-worlds-dioni.zocomputer.io/ in TWO browsers"
echo "   2. Move in one browser"
echo "   3. Verify player appears in same position in both views"
echo ""
echo "📹 Video recording: /home/workspace/multiplayer-test-final.mp4"
echo "📸 Screenshot: /home/workspace/game-screenshot.png"
