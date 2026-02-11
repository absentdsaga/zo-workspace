---
name: asset-pipeline-iso
description: End-to-end asset pipeline for isometric game art - from AI generation to optimized sprite atlases. Handles Chrono Trigger style enforcement, palette quantization, and automated sprite sheet creation.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: game-art-pipeline
  version: 1.0.0
---

# Isometric Asset Pipeline

Automated pipeline from concept to production-ready game assets for isometric tactical RPG worlds.

## Pipeline Overview

```
Concept → AI Generation → Style Transfer → Palette Quantization → 
Animation → Atlas Packing → Compression → Integration
```

## Stage 1: AI Generation

### Prompt Engineering for Isometric
```typescript
interface IsoSpritePrompt {
  character: string;
  style: 'chrono-trigger' | 'final-fantasy-tactics';
  view: 'isometric-45deg';
  platform: 'grass' | 'stone' | 'wood';
  resolution: '48x64px';
  details: string[];
}

function buildPrompt(spec: IsoSpritePrompt): string {
  return `
    Isometric pixel art character sprite, ${spec.resolution},
    ${spec.style} style, standing on elevated ${spec.platform} tile platform,
    45-degree isometric view, square tile with visible depth,
    character: ${spec.character},
    ${spec.details.join(', ')},
    clean pixel art, no blur, dithered shadows,
    warm Chrono Trigger color palette (64 colors max),
    platform shows grass texture and brown earth sides
  `.trim();
}
```

### Generate Base Sprite
```bash
bun run scripts/generate-base.ts \
  --character "warrior with red spiky hair" \
  --platform grass \
  --output temp/warrior-gen.png
```

## Stage 2: Style Enforcement

### Chrono Trigger Color Extraction
```typescript
class ChronoTriggerPalette {
  // Extracted from CT sprite sheets
  static PALETTE = [
    // Skin tones (12)
    '#F4D0A0', '#E8B088', '#D99160', '#C67240',
    '#A85A30', '#8B4A28', '#6B3820', '#4A2818',
    
    // Hair colors (8)
    '#2C1810', '#CA4540', '#E8B040', '#5A7A4F',
    
    // Armor/clothes (16)
    '#4A9EFF', '#3A7EDF', '#2A5EBF', '#1A3E9F',
    '#CA4540', '#AA3530', '#8A2520', '#6A1510',
    
    // Environment (28)
    '#5A7A4F', '#7A9A6F', '#9ABA8F', // Greens
    '#6B6B6B', '#8B8B8B', '#ABABAB', // Grays
    '#4A3820', '#6A5830', '#8A7840', // Browns
    // ... (64 total colors)
  ];
  
  quantize(image: ImageData): ImageData {
    // Reduce image to CT palette using nearest-color matching
    const palette = this.PALETTE.map(hex => this.hexToRgb(hex));
    
    for (let i = 0; i < image.data.length; i += 4) {
      const r = image.data[i];
      const g = image.data[i + 1];
      const b = image.data[i + 2];
      
      const nearest = this.findNearestColor({ r, g, b }, palette);
      
      image.data[i] = nearest.r;
      image.data[i + 1] = nearest.g;
      image.data[i + 2] = nearest.b;
    }
    
    return image;
  }
}
```

### Apply Dithering
```bash
bun run scripts/apply-style.ts \
  --input temp/warrior-gen.png \
  --palette chrono-trigger \
  --dither checkerboard \
  --output temp/warrior-styled.png
```

## Stage 3: Platform Integration

### Add Isometric Tile Base
```typescript
class PlatformCompositor {
  addPlatform(
    character: ImageData,
    platformType: 'grass' | 'stone' | 'wood'
  ): ImageData {
    const platform = this.generateIsoPlatform(platformType);
    
    // Composite: platform below, character on top
    const canvas = createCanvas(48, 64);
    const ctx = canvas.getContext('2d')!;
    
    // Draw platform at bottom
    ctx.putImageData(platform, 8, 48);
    
    // Draw character centered on platform
    ctx.putImageData(character, 8, 0);
    
    // Add shadow
    this.drawShadow(ctx, 24, 52);
    
    return ctx.getImageData(0, 0, 48, 64);
  }
  
  generateIsoPlatform(type: string): ImageData {
    const canvas = createCanvas(32, 20);
    const ctx = canvas.getContext('2d')!;
    
    // Draw isometric diamond top
    ctx.fillStyle = type === 'grass' ? '#5A7A4F' : '#6B6B6B';
    ctx.beginPath();
    ctx.moveTo(16, 0);  // Top
    ctx.lineTo(32, 8);  // Right
    ctx.lineTo(16, 16); // Bottom
    ctx.lineTo(0, 8);   // Left
    ctx.closePath();
    ctx.fill();
    
    // Draw left side (darker)
    ctx.fillStyle = type === 'grass' ? '#4A3820' : '#4A4A4A';
    ctx.beginPath();
    ctx.moveTo(0, 8);
    ctx.lineTo(16, 16);
    ctx.lineTo(16, 20);
    ctx.lineTo(0, 12);
    ctx.closePath();
    ctx.fill();
    
    // Draw right side (medium)
    ctx.fillStyle = type === 'grass' ? '#6A5830' : '#5A5A5A';
    ctx.beginPath();
    ctx.moveTo(16, 16);
    ctx.lineTo(32, 8);
    ctx.lineTo(32, 12);
    ctx.lineTo(16, 20);
    ctx.closePath();
    ctx.fill();
    
    return ctx.getImageData(0, 0, 32, 20);
  }
}
```

## Stage 4: 8-Direction Generation

### Rotate for 8 Directions
```typescript
class DirectionGenerator {
  generate8Directions(baseSprite: ImageData): Map<string, ImageData> {
    const directions = new Map<string, ImageData>();
    
    // Start with south (facing camera)
    directions.set('s', baseSprite);
    
    // Generate other 7 directions
    directions.set('se', this.rotate(baseSprite, 45));
    directions.set('e', this.flip(baseSprite, 'horizontal'));
    directions.set('ne', this.rotate(this.flip(baseSprite, 'horizontal'), -45));
    
    // North (back view) - special generation
    directions.set('n', this.generateBackView(baseSprite));
    directions.set('nw', this.rotate(directions.get('n')!, -45));
    directions.set('w', this.flip(directions.get('e')!, 'horizontal'));
    directions.set('sw', this.flip(directions.get('se')!, 'horizontal'));
    
    return directions;
  }
  
  generateBackView(front: ImageData): ImageData {
    // AI-assisted back view generation
    // (or hand-drawn, or mirrored with head adjustments)
    return generateImage({
      prompt: 'same character, back view, same style',
      reference: front,
    });
  }
}
```

## Stage 5: Walk Cycle Animation

### Create 4-Frame Walk Cycle
```typescript
class WalkCycleGenerator {
  generate(direction: ImageData): ImageData[] {
    const frames: ImageData[] = [];
    
    // Frame 1: Left foot forward
    frames.push(this.shiftLeg(direction, 'left', 2));
    
    // Frame 2: Center (passing pose)
    frames.push(direction);
    
    // Frame 3: Right foot forward
    frames.push(this.shiftLeg(direction, 'right', 2));
    
    // Frame 4: Center (return)
    frames.push(direction);
    
    return frames;
  }
  
  shiftLeg(sprite: ImageData, leg: 'left' | 'right', pixels: number): ImageData {
    // Shift leg pixels forward (simple animation)
    // In production, use more sophisticated bone-based animation
    const modified = cloneImageData(sprite);
    
    // Identify leg pixels (bottom 1/3 of sprite)
    // Shift them forward by `pixels`
    
    return modified;
  }
}
```

## Stage 6: Atlas Packing

### Combine into Sprite Sheet
```typescript
class SpriteAtlasPacker {
  pack(sprites: Map<string, ImageData[]>): { image: ImageData, json: any } {
    // Layout: 8 directions × 4 frames = 32 sprites
    // Arrange in 8 rows (directions) × 4 columns (frames)
    
    const frameWidth = 48;
    const frameHeight = 64;
    const cols = 4;
    const rows = 8;
    
    const atlasWidth = frameWidth * cols;
    const atlasHeight = frameHeight * rows;
    
    const canvas = createCanvas(atlasWidth, atlasHeight);
    const ctx = canvas.getContext('2d')!;
    
    const directions = ['s', 'se', 'e', 'ne', 'n', 'nw', 'w', 'sw'];
    
    directions.forEach((dir, row) => {
      const frames = sprites.get(dir)!;
      frames.forEach((frame, col) => {
        ctx.putImageData(frame, col * frameWidth, row * frameHeight);
      });
    });
    
    const image = ctx.getImageData(0, 0, atlasWidth, atlasHeight);
    
    // Generate JSON metadata for Phaser
    const json = {
      frames: {},
      meta: {
        image: 'warrior.png',
        size: { w: atlasWidth, h: atlasHeight },
        scale: '1',
      },
    };
    
    directions.forEach((dir, row) => {
      for (let col = 0; col < 4; col++) {
        const frameName = `${dir}-${col}`;
        json.frames[frameName] = {
          frame: {
            x: col * frameWidth,
            y: row * frameHeight,
            w: frameWidth,
            h: frameHeight,
          },
        };
      }
    });
    
    return { image, json };
  }
}
```

## Stage 7: Optimization

### Compress & Optimize
```bash
# PNG optimization (lossless)
bun run scripts/optimize.ts \
  --input sprites/warrior.png \
  --output assets/sprites/warrior.png \
  --quality 100

# Result: ~5KB per sprite sheet
```

### Generate Multiple Resolutions
```bash
# 1x (base)
# 2x (high-DPI)
# 0.5x (low-end mobile)

bun run scripts/generate-resolutions.ts \
  --input sprites/warrior.png \
  --resolutions 0.5,1,2 \
  --output assets/sprites/
```

## Full Pipeline Script

### One-Command Generation
```bash
bun run Skills/asset-pipeline-iso/scripts/generate-character.ts \
  --character "warrior with red hair, blue armor" \
  --output warrior \
  --platform grass \
  --directions 8 \
  --frames 4 \
  --palette chrono-trigger \
  --optimize
```

**Output**:
- `assets/sprites/warrior.png` (192×512px atlas)
- `assets/sprites/warrior.json` (Phaser metadata)
- `assets/sprites/warrior@2x.png` (high-DPI)

## Quality Assurance

### Automated Checks
```typescript
class AssetQA {
  validate(spriteSheet: ImageData, json: any): QAReport {
    const report: QAReport = { passed: true, issues: [] };
    
    // Check dimensions
    if (spriteSheet.width !== 192 || spriteSheet.height !== 512) {
      report.issues.push('Invalid atlas size');
      report.passed = false;
    }
    
    // Check color count
    const colors = this.extractColors(spriteSheet);
    if (colors.size > 64) {
      report.issues.push(`Too many colors: ${colors.size} (max 64)`);
      report.passed = false;
    }
    
    // Check platform presence
    const hasPlatform = this.detectPlatform(spriteSheet);
    if (!hasPlatform) {
      report.issues.push('Missing platform tile');
      report.passed = false;
    }
    
    return report;
  }
}
```

## Batch Processing

### Generate 50 Characters
```bash
bun run scripts/batch-generate.ts \
  --config characters.json \
  --output assets/sprites/ \
  --parallel 5
```

**characters.json**:
```json
[
  { "name": "warrior", "desc": "red hair, blue armor", "platform": "grass" },
  { "name": "mage", "desc": "purple robe, staff", "platform": "stone" },
  { "name": "archer", "desc": "green cloak, bow", "platform": "wood" },
  // ... 47 more
]
```

## Integration with Spatial Worlds

This pipeline generates all sprites for Spatial Worlds:
1. Generate 50 diverse characters
2. Create platform tiles (grass, stone, water)
3. Generate object sprites (chairs, trees, doors)
4. Optimize and pack into atlases
5. Export Phaser-ready assets

Run this on **Day 2-3** to create production art.
