#!/usr/bin/env node
// Create 8-direction walk animation sprites
// Each direction has 4 frames (idle, walk1, walk2, walk3)

const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

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

function drawPlatform(ctx, cx, cy) {
  ctx.save();
  ctx.translate(cx, cy);

  // Grass top
  ctx.fillStyle = colors.grassTop;
  ctx.beginPath();
  ctx.moveTo(0, -10);
  ctx.lineTo(16, 0);
  ctx.lineTo(0, 10);
  ctx.lineTo(-16, 0);
  ctx.closePath();
  ctx.fill();

  // Earth left
  ctx.fillStyle = colors.earth;
  ctx.beginPath();
  ctx.moveTo(-16, 0);
  ctx.lineTo(0, 10);
  ctx.lineTo(0, 14);
  ctx.lineTo(-16, 4);
  ctx.closePath();
  ctx.fill();

  // Earth right
  ctx.fillStyle = colors.earthDark;
  ctx.beginPath();
  ctx.moveTo(0, 10);
  ctx.lineTo(16, 0);
  ctx.lineTo(16, 4);
  ctx.lineTo(0, 14);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}

function drawWarrior(ctx, cx, by, frame = 0, direction = 'south') {
  // Leg offset for walk animation
  const legOffset = frame === 1 ? 1 : frame === 2 ? -1 : 0;
  const armOffset = frame === 1 ? -1 : frame === 2 ? 1 : 0;

  // Direction-specific adjustments
  let bodyRotation = 0;
  let headTurn = 0; // -1 = left, 0 = front, 1 = right
  let swordSide = 1; // 1 = right, -1 = left

  switch(direction) {
    case 'south':
      bodyRotation = 0;
      headTurn = 0;
      swordSide = 1;
      break;
    case 'north':
      bodyRotation = 0;
      headTurn = 0;
      swordSide = -1;
      break;
    case 'east':
      bodyRotation = 0;
      headTurn = 1;
      swordSide = 1;
      break;
    case 'west':
      bodyRotation = 0;
      headTurn = -1;
      swordSide = -1;
      break;
    case 'se':
      bodyRotation = 0;
      headTurn = 1;
      swordSide = 1;
      break;
    case 'sw':
      bodyRotation = 0;
      headTurn = -1;
      swordSide = -1;
      break;
    case 'ne':
      bodyRotation = 0;
      headTurn = 1;
      swordSide = 1;
      break;
    case 'nw':
      bodyRotation = 0;
      headTurn = -1;
      swordSide = -1;
      break;
  }

  // Boots
  ctx.fillStyle = colors.boots;
  ctx.fillRect(cx - 3 + legOffset, by, 6, 4);

  // Legs
  ctx.fillStyle = colors.tunicDark;
  ctx.fillRect(cx - 4, by - 10, 8, 10);

  // Tunic
  ctx.fillStyle = colors.tunic;
  ctx.fillRect(cx - 6, by - 22, 12, 12);
  ctx.fillStyle = colors.tunicDark;
  ctx.fillRect(cx - 6, by - 22, 12, 2);

  // Belt
  ctx.fillStyle = colors.belt;
  ctx.fillRect(cx - 6, by - 12, 12, 2);

  // Arms (position based on direction)
  ctx.fillStyle = colors.tunicDark;
  if (headTurn >= 0) {
    // Right arm visible
    ctx.fillRect(cx + 5, by - 20 - armOffset, 3, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx + 6, by - 13 - armOffset, 2, 2);
  }
  if (headTurn <= 0) {
    // Left arm visible
    ctx.fillStyle = colors.tunicDark;
    ctx.fillRect(cx - 8, by - 20 + armOffset, 3, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx - 8, by - 13 + armOffset, 2, 2);
  }

  // Neck
  ctx.fillStyle = colors.skinDark;
  ctx.fillRect(cx - 2, by - 24, 4, 2);

  // Head (adjust based on direction)
  ctx.fillStyle = colors.skin;
  const isBackFacing = direction === 'north' || direction === 'ne' || direction === 'nw';

  if (isBackFacing) {
    // Back of head (no face visible)
    ctx.fillRect(cx - 4, by - 32, 8, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx - 4, by - 32, 2, 8);
  } else if (headTurn === 0) {
    // Front facing
    ctx.fillRect(cx - 4, by - 32, 8, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx + 2, by - 32, 2, 8);
  } else if (headTurn > 0) {
    // Right facing
    ctx.fillRect(cx - 3, by - 32, 8, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx + 3, by - 32, 2, 8);
  } else {
    // Left facing
    ctx.fillRect(cx - 5, by - 32, 8, 8);
    ctx.fillStyle = colors.skinDark;
    ctx.fillRect(cx - 5, by - 32, 2, 8);
  }

  // Hair (adjust based on direction)
  ctx.fillStyle = colors.hair;
  if (isBackFacing) {
    // Back of head - full hair coverage
    ctx.fillRect(cx - 5, by - 36, 10, 5);
    ctx.fillRect(cx - 5, by - 38, 10, 2);
    ctx.fillStyle = colors.hairLight;
    ctx.fillRect(cx - 4, by - 36, 3, 1);
  } else if (headTurn === 0) {
    ctx.fillRect(cx - 5, by - 36, 10, 5);
    ctx.fillRect(cx - 5, by - 38, 2, 2);
    ctx.fillRect(cx - 1, by - 38, 2, 2);
    ctx.fillRect(cx + 3, by - 38, 2, 2);
    ctx.fillStyle = colors.hairLight;
    ctx.fillRect(cx - 4, by - 36, 3, 1);
  } else if (headTurn > 0) {
    ctx.fillRect(cx - 4, by - 36, 10, 5);
    ctx.fillRect(cx - 2, by - 38, 2, 2);
    ctx.fillRect(cx + 2, by - 38, 2, 2);
    ctx.fillRect(cx + 4, by - 38, 2, 2);
    ctx.fillStyle = colors.hairLight;
    ctx.fillRect(cx - 3, by - 36, 3, 1);
  } else {
    ctx.fillRect(cx - 6, by - 36, 10, 5);
    ctx.fillRect(cx - 6, by - 38, 2, 2);
    ctx.fillRect(cx - 2, by - 38, 2, 2);
    ctx.fillRect(cx + 2, by - 38, 2, 2);
    ctx.fillStyle = colors.hairLight;
    ctx.fillRect(cx - 5, by - 36, 3, 1);
  }

  // Eyes (adjust based on direction) - not visible when back-facing
  if (!isBackFacing) {
    ctx.fillStyle = '#000000';
    if (headTurn === 0) {
      ctx.fillRect(cx - 3, by - 30, 1, 1);
      ctx.fillRect(cx + 2, by - 30, 1, 1);
    } else if (headTurn > 0) {
      ctx.fillRect(cx + 1, by - 30, 1, 1);
    } else {
      ctx.fillRect(cx - 2, by - 30, 1, 1);
    }

    // Mouth - not visible when back-facing
    ctx.fillStyle = colors.skinDark;
    if (headTurn === 0) {
      ctx.fillRect(cx - 1, by - 27, 2, 1);
    } else {
      ctx.fillRect(cx + (headTurn > 0 ? 0 : -1), by - 27, 2, 1);
    }
  }

  // Sword (position based on direction)
  ctx.fillStyle = colors.sword;
  const swordX = cx + (7 * swordSide);
  if (swordSide > 0) {
    ctx.fillRect(swordX, by - 26, 2, 12);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(swordX, by - 26, 1, 12);
    ctx.fillStyle = colors.belt;
    ctx.fillRect(swordX - 1, by - 15, 4, 2);
  } else {
    ctx.fillRect(swordX - 2, by - 26, 2, 12);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(swordX - 1, by - 26, 1, 12);
    ctx.fillStyle = colors.belt;
    ctx.fillRect(swordX - 3, by - 15, 4, 2);
  }
}

// All 8 directions
const directions = ['south', 'north', 'east', 'west', 'se', 'sw', 'ne', 'nw'];

console.log('🎬 Creating 8-direction walk animations...\n');

for (const direction of directions) {
  for (let frame = 0; frame < 4; frame++) {
    const canvas = createCanvas(48, 64);
    const ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, 48, 64);
    drawPlatform(ctx, 24, 54);
    drawWarrior(ctx, 24, 44, frame, direction);

    const filename = `warrior-${direction}-${frame}.png`;
    const outputPath = path.join(__dirname, '../../assets/sprites', filename);
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buffer);

    console.log(`✅ Created: ${filename}`);
  }
}

console.log('\n🎬 Walk animation frames created (8 directions × 4 frames = 32 sprites)');
console.log('   Frames: 0=idle, 1=step-right, 2=idle, 3=step-left');
console.log('   Directions: south, north, east, west, se, sw, ne, nw');
