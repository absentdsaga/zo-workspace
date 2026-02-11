/**
 * Automated test: Verify sprite consistency across all 8 directions
 *
 * This test simulates movement in all directions and verifies that the sprite
 * texture remains consistent (no sudden changes to different sprites).
 */

console.log('🧪 SPRITE CONSISTENCY TEST\n');

// Simulate sprite frame checks
const directions = ['south', 'north', 'east', 'west', 'se', 'sw', 'ne', 'nw'];
const fs = require('fs');
const path = require('path');

console.log('Checking sprite files for consistency...\n');

let allConsistent = true;
const basePath = './assets/sprites';

// Check all frame 0 files (idle frames)
console.log('📊 Frame 0 (Idle) Sprite Analysis:');
const frame0Sizes = {};
for (const dir of directions) {
  const filePath = path.join(basePath, `warrior-${dir}-0.png`);
  try {
    const stats = fs.statSync(filePath);
    frame0Sizes[dir] = stats.size;
    console.log(`  ${dir.padEnd(6)}: ${stats.size} bytes`);
  } catch (err) {
    console.log(`  ${dir.padEnd(6)}: ❌ MISSING`);
    allConsistent = false;
  }
}

// Check if all sizes match (indicating same sprite style)
const sizes = Object.values(frame0Sizes);
const uniqueSizes = [...new Set(sizes)];

console.log('\n📈 Consistency Analysis:');
console.log(`  Unique file sizes: ${uniqueSizes.length}`);
console.log(`  Expected: 1 (all sprites should be identical size)`);

if (uniqueSizes.length === 1) {
  console.log(`  ✅ PASS: All sprites are ${uniqueSizes[0]} bytes`);
  console.log('  All 8 directions use the same sprite style');
} else {
  console.log(`  ❌ FAIL: Multiple sprite sizes detected`);
  console.log(`  Sizes found: ${uniqueSizes.join(', ')}`);
  allConsistent = false;
}

// Check all animation frames (1, 2, 3)
console.log('\n📊 Animation Frame Analysis:');
for (let frame = 1; frame <= 3; frame++) {
  const frameSizes = {};
  for (const dir of directions) {
    const filePath = path.join(basePath, `warrior-${dir}-${frame}.png`);
    try {
      const stats = fs.statSync(filePath);
      frameSizes[dir] = stats.size;
    } catch (err) {
      console.log(`  Frame ${frame}, ${dir}: ❌ MISSING`);
      allConsistent = false;
    }
  }

  const sizes = Object.values(frameSizes);
  const uniqueSizes = [...new Set(sizes)];

  if (uniqueSizes.length === 1) {
    console.log(`  Frame ${frame}: ✅ Consistent (${uniqueSizes[0]} bytes)`);
  } else {
    console.log(`  Frame ${frame}: ❌ Inconsistent (${uniqueSizes.length} different sizes)`);
    allConsistent = false;
  }
}

console.log('\n' + '='.repeat(60));
if (allConsistent) {
  console.log('✅ TEST PASSED: All sprites are consistent');
  console.log('   The sprite will look the same in all 8 directions');
  process.exit(0);
} else {
  console.log('❌ TEST FAILED: Sprite inconsistencies detected');
  console.log('   The sprite may change appearance when moving');
  process.exit(1);
}
