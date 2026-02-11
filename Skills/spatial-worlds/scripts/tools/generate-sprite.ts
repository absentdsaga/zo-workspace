// Generate high-quality Chrono Trigger-style sprite
// 48×64px total: 32×48 character + 32×20 platform

const canvas = document.createElement('canvas');
canvas.width = 48;
canvas.height = 64;
const ctx = canvas.getContext('2d')!;

// Chrono Trigger color palette (SNES-inspired)
const colors = {
  // Character colors
  skin: '#f4d0a0',
  skinShadow: '#d4a070',
  hair: '#4a3020',
  hairHighlight: '#6a5040',
  tunic: '#4a6aaf',
  tunicShadow: '#3a5a8f',
  belt: '#8a6a4a',
  boots: '#3a2a1a',

  // Platform colors
  grassTop: '#5a8a4f',
  grassSide: '#4a7a3f',
  earth: '#6a4a2a',
  earthShadow: '#4a3a1a',
};

// Draw isometric grass platform (bottom 20px)
function drawPlatform() {
  ctx.save();
  ctx.translate(24, 54); // Center bottom of sprite

  // Isometric platform (32×20)
  // Top face (grass)
  ctx.fillStyle = colors.grassTop;
  ctx.beginPath();
  ctx.moveTo(0, -10);           // Top
  ctx.lineTo(16, 0);            // Right
  ctx.lineTo(0, 10);            // Bottom
  ctx.lineTo(-16, 0);           // Left
  ctx.closePath();
  ctx.fill();

  // Left side (earth)
  ctx.fillStyle = colors.earth;
  ctx.beginPath();
  ctx.moveTo(-16, 0);
  ctx.lineTo(0, 10);
  ctx.lineTo(0, 14);
  ctx.lineTo(-16, 4);
  ctx.closePath();
  ctx.fill();

  // Right side (earth, darker)
  ctx.fillStyle = colors.earthShadow;
  ctx.beginPath();
  ctx.moveTo(0, 10);
  ctx.lineTo(16, 0);
  ctx.lineTo(16, 4);
  ctx.lineTo(0, 14);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}

// Draw character (32×48, centered on platform)
function drawCharacter() {
  const centerX = 24;
  const baseY = 44; // Standing on platform

  // Boots (bottom)
  ctx.fillStyle = colors.boots;
  ctx.fillRect(centerX - 3, baseY, 6, 4);

  // Legs
  ctx.fillStyle = colors.tunicShadow;
  ctx.fillRect(centerX - 4, baseY - 10, 8, 10);

  // Tunic body
  ctx.fillStyle = colors.tunic;
  ctx.fillRect(centerX - 6, baseY - 22, 12, 12);

  // Belt
  ctx.fillStyle = colors.belt;
  ctx.fillRect(centerX - 6, baseY - 12, 12, 2);

  // Arms
  ctx.fillStyle = colors.tunicShadow;
  ctx.fillRect(centerX - 8, baseY - 20, 3, 8);
  ctx.fillRect(centerX + 5, baseY - 20, 3, 8);

  // Neck
  ctx.fillStyle = colors.skinShadow;
  ctx.fillRect(centerX - 2, baseY - 24, 4, 2);

  // Head (8×10)
  ctx.fillStyle = colors.skin;
  ctx.fillRect(centerX - 4, baseY - 32, 8, 8);

  // Hair (spiky)
  ctx.fillStyle = colors.hair;
  ctx.fillRect(centerX - 5, baseY - 36, 10, 4); // Top
  ctx.fillRect(centerX - 5, baseY - 34, 2, 4); // Left spike
  ctx.fillRect(centerX + 3, baseY - 34, 2, 4); // Right spike

  // Eyes
  ctx.fillStyle = '#000000';
  ctx.fillRect(centerX - 3, baseY - 30, 1, 1);
  ctx.fillRect(centerX + 2, baseY - 30, 1, 1);

  // Sword (right hand)
  ctx.fillStyle = '#c0c0c0';
  ctx.fillRect(centerX + 6, baseY - 24, 2, 10);
  ctx.fillStyle = '#8a6a4a';
  ctx.fillRect(centerX + 6, baseY - 15, 2, 2); // Hilt
}

// Generate sprite
ctx.clearRect(0, 0, 48, 64);
drawPlatform();
drawCharacter();

// Export to PNG
export function generateSprite(): HTMLCanvasElement {
  return canvas;
}

// For browser execution
if (typeof window !== 'undefined') {
  const sprite = generateSprite();
  document.body.appendChild(sprite);

  // Download link
  const link = document.createElement('a');
  link.download = 'warrior-chrono-style.png';
  link.href = sprite.toDataURL();
  link.textContent = 'Download Sprite';
  document.body.appendChild(link);
}
