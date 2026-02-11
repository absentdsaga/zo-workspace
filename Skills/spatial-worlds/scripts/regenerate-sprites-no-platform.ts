#!/usr/bin/env bun

/**
 * Regenerate warrior sprites WITHOUT platform
 * Just character + small shadow underneath
 */

import { createCanvas } from 'canvas';
import fs from 'fs';

const directions = [
  { name: 'chrono', frames: 1 },
  { name: 'south', frames: 4 },
  { name: 'north', frames: 4 },
  { name: 'east', frames: 4 },
  { name: 'west', frames: 4 }
];

function generateSprite(filename: string) {
  const canvas = createCanvas(48, 48);  // 48x48 instead of 48x64 (no platform space)
  const ctx = canvas.getContext('2d');

  // Clear canvas
  ctx.clearRect(0, 0, 48, 48);

  // Draw small shadow at bottom (just a subtle oval)
  ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
  ctx.beginPath();
  ctx.ellipse(24, 42, 8, 3, 0, 0, Math.PI * 2);
  ctx.fill();

  // Draw character body
  const charY = 4;

  // Head (skin tone)
  ctx.fillStyle = '#f4d0a0';
  ctx.fillRect(20, charY + 8, 8, 8);

  // Hair (red spiky - Chrono style)
  ctx.fillStyle = '#ca4540';
  ctx.fillRect(19, charY + 4, 10, 6);
  // Spikes
  ctx.fillRect(17, charY + 6, 2, 2);
  ctx.fillRect(29, charY + 6, 2, 2);

  // Body (blue armor)
  ctx.fillStyle = '#4a9eff';
  ctx.fillRect(18, charY + 16, 12, 12);

  // Arms
  ctx.fillStyle = '#4a9eff';
  ctx.fillRect(16, charY + 18, 2, 8);
  ctx.fillRect(30, charY + 18, 2, 8);

  // Legs (dark pants)
  ctx.fillStyle = '#2c2c2c';
  ctx.fillRect(20, charY + 28, 3, 8);
  ctx.fillRect(25, charY + 28, 3, 8);

  // Simple outline for visibility
  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 1;
  ctx.strokeRect(19, charY + 3, 10, 34);

  // Save as PNG
  const buffer = canvas.toBuffer('image/png');
  const path = `/home/workspace/Skills/spatial-worlds/assets/sprites/${filename}`;
  fs.writeFileSync(path, buffer);
  console.log(`✅ Generated ${filename}`);
}

// Generate all warrior sprites
console.log('🎨 Regenerating warrior sprites WITHOUT platforms...\n');

for (const dir of directions) {
  if (dir.frames === 1) {
    generateSprite(`warrior-${dir.name}.png`);
  } else {
    for (let i = 0; i < dir.frames; i++) {
      generateSprite(`warrior-${dir.name}-${i}.png`);
    }
  }
}

console.log('\n✅ All sprites regenerated!');
console.log('   Size: 48x48px (was 48x64px)');
console.log('   No platform - just character + shadow');
console.log('   Location: assets/sprites/warrior-*.png');
