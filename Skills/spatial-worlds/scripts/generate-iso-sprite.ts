#!/usr/bin/env bun

/**
 * Generate isometric sprite placeholder with platform
 * (Temporary - will be replaced with AI-generated sprites)
 */

import { createCanvas } from 'canvas';
import fs from 'fs';

const canvas = createCanvas(48, 64);
const ctx = canvas.getContext('2d');

// Clear canvas
ctx.fillStyle = 'transparent';
ctx.fillRect(0, 0, 48, 64);

// Draw isometric grass platform at bottom
const platformY = 44;

// Top face (diamond)
ctx.fillStyle = '#5a7a4f';
ctx.beginPath();
ctx.moveTo(24, platformY);                    // Top point
ctx.lineTo(40, platformY + 8);                // Right point
ctx.lineTo(24, platformY + 16);               // Bottom point
ctx.lineTo(8, platformY + 8);                 // Left point
ctx.closePath();
ctx.fill();

// Left side (darker)
ctx.fillStyle = '#4a3820';
ctx.beginPath();
ctx.moveTo(8, platformY + 8);
ctx.lineTo(24, platformY + 16);
ctx.lineTo(24, platformY + 20);
ctx.lineTo(8, platformY + 12);
ctx.closePath();
ctx.fill();

// Right side (medium brown)
ctx.fillStyle = '#6a5830';
ctx.beginPath();
ctx.moveTo(24, platformY + 16);
ctx.lineTo(40, platformY + 8);
ctx.lineTo(40, platformY + 12);
ctx.lineTo(24, platformY + 20);
ctx.closePath();
ctx.fill();

// Draw shadow on platform
ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
ctx.beginPath();
ctx.ellipse(24, platformY + 10, 6, 3, 0, 0, Math.PI * 2);
ctx.fill();

// Draw character body on platform
const charY = 12;

// Body (blue armor)
ctx.fillStyle = '#4a9eff';
ctx.fillRect(18, charY + 20, 12, 16);

// Head (skin tone)
ctx.fillStyle = '#f4d0a0';
ctx.fillRect(20, charY + 12, 8, 8);

// Hair (red spiky)
ctx.fillStyle = '#ca4540';
ctx.fillRect(19, charY + 8, 10, 6);
// Spikes
ctx.fillRect(17, charY + 10, 2, 2);
ctx.fillRect(29, charY + 10, 2, 2);

// Arms
ctx.fillStyle = '#4a9eff';
ctx.fillRect(16, charY + 22, 2, 8);
ctx.fillRect(30, charY + 22, 2, 8);

// Legs (dark pants)
ctx.fillStyle = '#2c2c2c';
ctx.fillRect(20, charY + 36, 3, 8);
ctx.fillRect(25, charY + 36, 3, 8);

// Outline for readability (simple dark pixels)
ctx.fillStyle = '#000000';
// Top of head
for (let x = 19; x < 29; x++) {
  ctx.fillRect(x, charY + 7, 1, 1);
}

// Save as PNG
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync('/home/workspace/Skills/spatial-worlds/assets/sprites/warrior-iso.png', buffer);

console.log('✅ Generated warrior-iso.png (48×64px)');
console.log('   Platform: Grass with depth');
console.log('   Character: Warrior with red hair, blue armor');
console.log('   Location: assets/sprites/warrior-iso.png');
