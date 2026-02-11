---
name: isometric-sprite-gen
description: Generate high-quality isometric sprites in Chrono Trigger style for tactical RPG worlds. Creates character sprites on elevated square tiles with 8-direction movement and rich animation.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: game-art
  version: 1.0.0
---

# Isometric Sprite Generator

Generate beautiful isometric character sprites in Chrono Trigger style, standing on elevated square tiles (Final Fantasy Tactics perspective).

## Visual Style

**Reference**: Chrono Trigger characters + Final Fantasy Tactics isometric perspective
- **Tile shape**: Square platforms with depth (not diamonds)
- **Camera angle**: 45° isometric, elevated view
- **Character style**: Chunky pixel art, 2.5-3 heads tall
- **Platform**: Visible grass/stone tile with sides showing elevation
- **Animation**: 8-direction movement (N, NE, E, SE, S, SW, W, NW)

## Key Differences from Top-Down

### Isometric Requirements
1. **Show depth**: Characters have front, sides, and back
2. **Platform elevation**: Tiles show vertical sides (3-5 pixels tall)
3. **Foreshortening**: Legs appear shorter due to perspective
4. **8-direction sprites**: More angles than top-down (4-dir)
5. **Layered rendering**: Characters can stand "behind" elevated tiles

## Generation Pipeline

### Step 1: Analyze Reference
Extract style rules from Chrono Trigger + FFT:
```bash
bun run scripts/analyze-reference.ts \
  --chrono-trigger-sprites chrono_ref/ \
  --fft-perspective fft_ref/ \
  --output style-guide.json
```

### Step 2: Generate Base Sprite
Create character on platform tile:
```bash
bun run scripts/generate-iso-sprite.ts \
  --character "warrior with red hair and blue armor" \
  --platform "grass tile" \
  --style chrono-trigger \
  --output sprites/warrior-base.png
```

### Step 3: Create 8-Direction Variations
```bash
bun run scripts/create-directions.ts \
  --input sprites/warrior-base.png \
  --directions 8 \
  --output sprites/warrior-all-dirs.png
```

### Step 4: Animate Walk Cycles
```bash
bun run scripts/animate-walk.ts \
  --input sprites/warrior-all-dirs.png \
  --frames 4 \
  --fps 8 \
  --output sprites/warrior-animated.png
```

### Step 5: Export for Phaser
```bash
bun run scripts/export-phaser.ts \
  --input sprites/warrior-animated.png \
  --output assets/sprites/warrior.png \
  --json assets/sprites/warrior.json
```

## Sprite Specifications

### Character Sprite
- **Size**: 48×64px (larger than top-down to show detail)
- **Platform**: 32×16px isometric tile base
- **Character**: 32×48px (standing on platform)
- **Total canvas**: 48×64px with padding

### Platform Tile
- **Top face**: 32×16px diamond shape
- **Depth**: 4-6px vertical sides
- **Texture**: Grass, stone, wood, etc.
- **Shadow**: Character casts shadow on tile

### Animation Frames
- **Idle**: 2 frames (breathing)
- **Walk**: 4 frames per direction
- **Run**: 6 frames per direction (optional)
- **Attack**: 4 frames (optional)

### Color Palette
- **Characters**: Chrono Trigger 64-color palette
- **Platforms**: Earth tones (browns, greens)
- **Shadows**: Transparency + multiply blend
- **Highlights**: Top-right lighting (consistent)

## Advanced Features

### Multi-Layer Sprites
```typescript
// Generate sprite with equipment layers
{
  base: "human-male-body",
  armor: "blue-plate-mail",
  hair: "red-spiky",
  weapon: "sword-broadsword",
  accessory: "cape-red"
}
```

### Palette Swapping
```bash
# Create variations with different colors
bun run scripts/palette-swap.ts \
  --input warrior.png \
  --palette red,blue,green \
  --output warriors/
```

### Batch Generation
```bash
# Generate 50 diverse characters
bun run scripts/batch-generate.ts \
  --count 50 \
  --diversity high \
  --output sprites/characters/
```

## Quality Checklist

Before using a sprite:
- [ ] Platform tile shows proper isometric perspective
- [ ] Character proportions match Chrono Trigger (2.5-3 heads)
- [ ] All 8 directions are distinct and readable
- [ ] Walk cycle loops seamlessly
- [ ] Shadow falls correctly on platform
- [ ] Colors match Chrono Trigger palette
- [ ] No more than 64 colors total
- [ ] Proper anti-aliasing (pixel-perfect edges)

## Usage in Spatial Worlds

```typescript
// Load isometric sprite
this.load.spritesheet('warrior', 'assets/sprites/warrior.png', {
  frameWidth: 48,
  frameHeight: 64,
});

// Create 8-direction animations
const directions = ['s', 'se', 'e', 'ne', 'n', 'nw', 'w', 'sw'];
directions.forEach((dir, i) => {
  this.anims.create({
    key: `walk-${dir}`,
    frames: this.anims.generateFrameNumbers('warrior', {
      start: i * 4,
      end: i * 4 + 3,
    }),
    frameRate: 8,
    repeat: -1,
  });
});
```

## Integration with Spatial Worlds

This skill replaces the placeholder sprite generation in Spatial Worlds with high-quality isometric sprites that match your vision:
- FFT-style elevated square tiles
- Chrono Trigger character aesthetic
- 8-direction movement
- Platform depth and shadows

Run this skill BEFORE Day 2 of Spatial Worlds to have proper art assets ready.
