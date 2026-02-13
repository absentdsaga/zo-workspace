#!/bin/bash

# Restore Normal Mode - exits NFT test mode

echo "🔄 RESTORING NORMAL MODE"
echo "======================"
echo ""

if [ -f "scripts/client/config-iso.ts.backup" ]; then
  echo "📝 Restoring original config..."
  mv scripts/client/config-iso.ts.backup scripts/client/config-iso.ts

  echo "🔨 Rebuilding..."
  ./build-client.sh

  echo ""
  echo "✅ NORMAL MODE RESTORED"
  echo ""
  echo "Game now uses warrior sprites (no NFT characters)"
  echo "URL: https://spatial-worlds-dioni.zocomputer.io"
else
  echo "❌ No backup found. Already in normal mode?"
fi
