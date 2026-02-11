#!/usr/bin/env node
// Create Chrono Trigger-style warrior sprite (48×64px)

const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

const canvas = createCanvas(48, 64);
const ctx = canvas.getContext('2d');

// Chrono Trigger SNES palette
const colors = {
  skin: '#f4d0a0',
  skinDark: '#d4a070',
  hair: '#4a3020',
  hairLight: '#6a5040',
  tunic: '#4a6aaf',
  tunicDark: '#3a5a8f',
  belt: '#8a6a4a',
  boots: '#2a1a0a',
  sword: '#c0c0c0',
  swordDark: '#a0a0a0',
  grassTop: '#5a8a4f',
  grassSide: '#4a7a3f',
  earth: '#6a4a2a',
  earthDark: '#4a3a1a',
};

// Clear canvas
ctx.clearRect(0, 0, 48, 64);

// Draw isometric grass platform (bottom 20px)
ctx.save();
ctx.translate(24, 54);

// Grass top (diamond)
ctx.fillStyle = colors.grassTop;
ctx.beginPath();
ctx.moveTo(0, -10);
ctx.lineTo(16, 0);
ctx.lineTo(0, 10);
ctx.lineTo(-16, 0);
ctx.closePath();
ctx.fill();

// Earth left side
ctx.fillStyle = colors.earth;
ctx.beginPath();
ctx.moveTo(-16, 0);
ctx.lineTo(0, 10);
ctx.lineTo(0, 14);
ctx.lineTo(-16, 4);
ctx.closePath();
ctx.fill();

// Earth right side (darker)
ctx.fillStyle = colors.earthDark;
ctx.beginPath();
ctx.moveTo(0, 10);
ctx.lineTo(16, 0);
ctx.lineTo(16, 4);
ctx.lineTo(0, 14);
ctx.closePath();
ctx.fill();

ctx.restore();

// Draw character (centered above platform)
const cx = 24;
const by = 44;

// Boots
ctx.fillStyle = colors.boots;
ctx.fillRect(cx - 3, by, 6, 4);

// Legs
ctx.fillStyle = colors.tunicDark;
ctx.fillRect(cx - 4, by - 10, 8, 10);

// Tunic
ctx.fillStyle = colors.tunic;
ctx.fillRect(cx - 6, by - 22, 12, 12);
ctx.fillStyle = colors.tunicDark;
ctx.fillRect(cx - 6, by - 22, 12, 2); // Shadow

// Belt
ctx.fillStyle = colors.belt;
ctx.fillRect(cx - 6, by - 12, 12, 2);

// Arms
ctx.fillStyle = colors.tunicDark;
ctx.fillRect(cx - 8, by - 20, 3, 8);
ctx.fillRect(cx + 5, by - 20, 3, 8);

// Hands
ctx.fillStyle = colors.skinDark;
ctx.fillRect(cx - 8, by - 13, 2, 2);
ctx.fillRect(cx + 6, by - 13, 2, 2);

// Neck
ctx.fillStyle = colors.skinDark;
ctx.fillRect(cx - 2, by - 24, 4, 2);

// Head
ctx.fillStyle = colors.skin;
ctx.fillRect(cx - 4, by - 32, 8, 8);
// Face shadow
ctx.fillStyle = colors.skinDark;
ctx.fillRect(cx + 2, by - 32, 2, 8);

// Hair
ctx.fillStyle = colors.hair;
ctx.fillRect(cx - 5, by - 36, 10, 5);
// Spikes
ctx.fillRect(cx - 5, by - 38, 2, 2);
ctx.fillRect(cx - 1, by - 38, 2, 2);
ctx.fillRect(cx + 3, by - 38, 2, 2);
// Hair highlight
ctx.fillStyle = colors.hairLight;
ctx.fillRect(cx - 4, by - 36, 3, 1);

// Eyes
ctx.fillStyle = '#000000';
ctx.fillRect(cx - 3, by - 30, 1, 1);
ctx.fillRect(cx + 2, by - 30, 1, 1);

// Mouth
ctx.fillStyle = colors.skinDark;
ctx.fillRect(cx - 1, by - 27, 2, 1);

// Sword (right side)
ctx.fillStyle = colors.sword;
ctx.fillRect(cx + 7, by - 26, 2, 12);
// Sword highlight
ctx.fillStyle = '#ffffff';
ctx.fillRect(cx + 7, by - 26, 1, 12);
// Hilt
ctx.fillStyle = colors.belt;
ctx.fillRect(cx + 6, by - 15, 4, 2);

// Save to file
const outputPath = path.join(__dirname, '../../assets/sprites/warrior-chrono.png');
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync(outputPath, buffer);

console.log(`✅ Sprite created: ${outputPath}`);
console.log(`   Dimensions: 48×64px`);
console.log(`   Style: Chrono Trigger SNES`);
console.log(`   Format: PNG`);
