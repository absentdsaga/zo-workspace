#!/bin/bash

# Test NFT Sprite Script
# Temporarily swaps in NFT test version to see how one sprite looks in game

NFT_SPRITE="${1:-set2-char2}"  # Default to set2-char2 if not specified

echo "🧪 NFT SPRITE TEST MODE"
echo "===================="
echo ""
echo "Testing sprite: $NFT_SPRITE"
echo ""

# 1. Backup original config
cp scripts/client/config-iso.ts scripts/client/config-iso.ts.backup

# 2. Update config to use test scene
echo "📝 Updating config to use NFT test scene..."
cat > scripts/client/config-iso.ts << 'EOF'
import Phaser from 'phaser';
import { BootScene } from './scenes/Boot';
import { IsoGameScene } from './scenes/IsoGame-NFT-TEST';  // TEST VERSION

export const isoConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
  width: 1280,
  height: 720,
  parent: 'game-container',
  backgroundColor: '#2b2b2b',
  pixelArt: true,
  antialias: false,
  roundPixels: true,

  physics: {
    default: 'arcade',
    arcade: {
      debug: false,
      debugShowBody: false,
      debugShowVelocity: false,
      debugShowStaticBody: false,
      gravity: { x: 0, y: 0 },
      tileBias: 16,
    },
  },

  render: {
    batchSize: 2048,
    maxTextures: 8,
    antialias: false,
    pixelArt: true,
  },

  scene: [BootScene, IsoGameScene],

  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },

  fps: {
    target: 60,
    forceSetTimeOut: true,
  },
};
EOF

# 3. Update test file to use specified sprite
echo "📝 Setting test sprite to: $NFT_SPRITE"
sed -i "s/const TEST_NFT_SPRITE = '.*';/const TEST_NFT_SPRITE = '$NFT_SPRITE';/" scripts/client/scenes/IsoGame-NFT-TEST.ts

# 4. Build
echo ""
echo "🔨 Building..."
./build-client.sh

echo ""
echo "✅ TEST MODE ACTIVE"
echo ""
echo "Testing: $NFT_SPRITE"
echo "URL: https://spatial-worlds-dioni.zocomputer.io"
echo ""
echo "What to check:"
echo "  - Does sprite render? (should see NFT character, not warrior)"
echo "  - Is size correct? (should match NPC size)"
echo "  - Is background transparent? (no beige/tan box)"
echo "  - Do animations work? (walk in 4 directions)"
echo "  - Is movement smooth?"
echo ""
echo "To test different sprite: ./test-nft-sprite.sh set1-char3"
echo "To restore normal mode: ./restore-normal-mode.sh"
