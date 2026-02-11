---
name: phaser-iso-engine
description: Optimized Phaser 3 engine configuration for isometric tactical RPG worlds. Handles depth sorting, multi-level collision, and performance tuning for 100+ concurrent sprites.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: game-engine
  version: 1.0.0
---

# Phaser Isometric Engine

Specialized Phaser 3 configuration and plugins for isometric tactical RPG worlds with proper depth sorting, multi-level terrain, and multiplayer optimization.

## Core Challenge

**Top-down vs Isometric rendering**:
- Top-down: Simple Y-sorting
- Isometric: Y + elevation + tile depth sorting

This skill solves the complex depth sorting required for FFT-style worlds.

## Engine Configuration

### Phaser Config for Isometric
```typescript
import Phaser from 'phaser';

export const isoConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL, // WebGL for better performance
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
      gravity: { x: 0, y: 0 },
      // Custom collision for isometric
      tileBias: 16,
    },
  },
  
  render: {
    // Critical for isometric depth
    batchSize: 4096,
    maxTextures: 16,
    // Disable built-in sorting, we'll handle it
    sortByDepth: false,
  },
  
  scene: [BootScene, IsoGameScene],
  
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
};
```

## Depth Sorting System

### Custom Depth Manager
```typescript
class DepthManager {
  // Z-index formula for isometric
  calculateDepth(x: number, y: number, elevation: number, height: number): number {
    // Sort by: elevation first, then Y, then height
    return (
      elevation * 10000 +  // Elevation layers
      y * 100 +            // Y position within layer
      height               // Object height for overlap
    );
  }
  
  // Update all sprite depths each frame
  updateDepths(scene: Phaser.Scene) {
    const sprites = scene.children.list.filter(
      child => child instanceof Phaser.GameObjects.Sprite
    );
    
    sprites.forEach(sprite => {
      if (sprite.getData('iso')) {
        const { elevation, height } = sprite.getData('iso');
        sprite.setDepth(
          this.calculateDepth(sprite.x, sprite.y, elevation, height)
        );
      }
    });
  }
}
```

## Isometric Camera System

### Custom Camera Controller
```typescript
class IsoCameraController {
  private camera: Phaser.Cameras.Scene2D.Camera;
  private target?: Phaser.GameObjects.Sprite;
  
  constructor(scene: Phaser.Scene) {
    this.camera = scene.cameras.main;
    
    // Isometric optimal zoom
    this.camera.setZoom(1.5);
    
    // Smooth follow
    this.camera.lerp.set(0.1, 0.1);
  }
  
  follow(target: Phaser.GameObjects.Sprite) {
    this.target = target;
    this.camera.startFollow(target, true);
  }
  
  update() {
    // Adjust for elevation (higher = pull camera up slightly)
    if (this.target) {
      const elevation = this.target.getData('iso')?.elevation || 0;
      this.camera.scrollY -= elevation * 4; // Subtle upward shift
    }
  }
}
```

## Multi-Level Collision

### Elevation-Aware Collision
```typescript
class IsoCollisionSystem {
  checkCollision(
    sprite: Phaser.GameObjects.Sprite,
    tilemap: Phaser.Tilemaps.Tilemap,
    targetX: number,
    targetY: number
  ): boolean {
    const elevation = sprite.getData('iso')?.elevation || 0;
    
    // Convert screen coords to tile coords
    const tileX = Math.floor(targetX / 32);
    const tileY = Math.floor(targetY / 16);
    
    // Check layer matching sprite's elevation
    const layer = tilemap.getLayer(`level-${elevation}`);
    if (!layer) return false;
    
    const tile = layer.tilemapLayer.getTileAt(tileX, tileY);
    
    // Check if tile is walkable
    return tile && tile.properties.walkable;
  }
  
  // Check if can move between elevations (stairs)
  canChangeElevation(
    from: { x: number, y: number, elevation: number },
    to: { x: number, y: number, elevation: number }
  ): boolean {
    const elevationDiff = Math.abs(to.elevation - from.elevation);
    
    // Can only change 1 level at a time
    if (elevationDiff > 1) return false;
    
    // Check for stairs/ramps between positions
    // ... (implementation)
    
    return true;
  }
}
```

## Performance Optimizations

### Frustum Culling (Isometric)
```typescript
class IsoFrustumCuller {
  cull(camera: Phaser.Cameras.Scene2D.Camera, sprites: Phaser.GameObjects.Sprite[]) {
    // Get camera bounds in world space
    const bounds = camera.worldView;
    
    // Expand bounds for isometric (objects can extend outside their base)
    const margin = 128; // 2 tiles
    const cullBounds = new Phaser.Geom.Rectangle(
      bounds.x - margin,
      bounds.y - margin,
      bounds.width + margin * 2,
      bounds.height + margin * 2
    );
    
    sprites.forEach(sprite => {
      // Check if sprite's base is in bounds
      const inView = Phaser.Geom.Rectangle.Contains(
        cullBounds,
        sprite.x,
        sprite.y
      );
      
      sprite.setVisible(inView);
      sprite.setActive(inView);
    });
  }
}
```

### Batch Rendering
```typescript
// Group sprites by texture for batching
class SpriteBatcher {
  organize(sprites: Phaser.GameObjects.Sprite[]): Map<string, Phaser.GameObjects.Sprite[]> {
    const batches = new Map<string, Phaser.GameObjects.Sprite[]>();
    
    sprites.forEach(sprite => {
      const texture = sprite.texture.key;
      if (!batches.has(texture)) {
        batches.set(texture, []);
      }
      batches.get(texture)!.push(sprite);
    });
    
    return batches;
  }
}
```

## Isometric Movement System

### 8-Direction Movement
```typescript
class IsoMovementController {
  private velocity = { x: 0, y: 0 };
  private speed = 150;
  
  // Map input to isometric directions
  private directionMap = {
    'N':  { x: -1, y: -0.5, anim: 'n' },
    'NE': { x:  0, y: -1,   anim: 'ne' },
    'E':  { x:  1, y: -0.5, anim: 'e' },
    'SE': { x:  1, y:  0,   anim: 'se' },
    'S':  { x:  1, y:  0.5, anim: 's' },
    'SW': { x:  0, y:  1,   anim: 'sw' },
    'W':  { x: -1, y:  0.5, anim: 'w' },
    'NW': { x: -1, y:  0,   anim: 'nw' },
  };
  
  update(sprite: Phaser.GameObjects.Sprite, cursors: any) {
    let dirX = 0;
    let dirY = 0;
    
    if (cursors.up.isDown) dirY -= 1;
    if (cursors.down.isDown) dirY += 1;
    if (cursors.left.isDown) dirX -= 1;
    if (cursors.right.isDown) dirX += 1;
    
    // Get direction key
    const direction = this.getDirection(dirX, dirY);
    
    if (direction) {
      const dir = this.directionMap[direction];
      
      // Apply isometric velocity
      sprite.setVelocity(
        dir.x * this.speed,
        dir.y * this.speed
      );
      
      // Play animation
      sprite.anims.play(`walk-${dir.anim}`, true);
    } else {
      sprite.setVelocity(0, 0);
      sprite.anims.play('idle', true);
    }
  }
  
  getDirection(x: number, y: number): string | null {
    if (x === 0 && y === -1) return 'N';
    if (x === 1 && y === -1) return 'NE';
    if (x === 1 && y === 0) return 'E';
    if (x === 1 && y === 1) return 'SE';
    if (x === 0 && y === 1) return 'S';
    if (x === -1 && y === 1) return 'SW';
    if (x === -1 && y === 0) return 'W';
    if (x === -1 && y === -1) return 'NW';
    return null;
  }
}
```

## Tile Coordinate Conversion

### Screen ↔ Tile Conversion
```typescript
class IsoCoordinates {
  // Screen to isometric tile
  screenToTile(screenX: number, screenY: number): { x: number, y: number } {
    const tileX = (screenX / 32) + (screenY / 16);
    const tileY = (screenY / 16) - (screenX / 32);
    return { x: Math.floor(tileX), y: Math.floor(tileY) };
  }
  
  // Tile to screen position
  tileToScreen(tileX: number, tileY: number, elevation: number = 0): { x: number, y: number } {
    const screenX = (tileX - tileY) * 16;
    const screenY = (tileX + tileY) * 8 - (elevation * 8);
    return { x: screenX, y: screenY };
  }
  
  // Get tile under mouse
  getTileUnderPointer(pointer: Phaser.Input.Pointer, camera: Phaser.Cameras.Scene2D.Camera): { x: number, y: number } {
    const worldX = pointer.x + camera.scrollX;
    const worldY = pointer.y + camera.scrollY;
    return this.screenToTile(worldX, worldY);
  }
}
```

## Integration Components

### Isometric Scene Template
```typescript
import Phaser from 'phaser';

export class IsoGameScene extends Phaser.Scene {
  private depthManager!: DepthManager;
  private cameraController!: IsoCameraController;
  private collisionSystem!: IsoCollisionSystem;
  private coordinates!: IsoCoordinates;
  
  create() {
    // Initialize systems
    this.depthManager = new DepthManager();
    this.cameraController = new IsoCameraController(this);
    this.collisionSystem = new IsoCollisionSystem();
    this.coordinates = new IsoCoordinates();
    
    // Load isometric tilemap
    const map = this.make.tilemap({ key: 'crossroads' });
    
    // Setup player
    this.player = this.createIsoSprite(400, 300, 'warrior', 0);
    this.cameraController.follow(this.player);
  }
  
  update() {
    // Update depth sorting every frame
    this.depthManager.updateDepths(this);
    
    // Update camera
    this.cameraController.update();
  }
  
  createIsoSprite(x: number, y: number, texture: string, elevation: number) {
    const sprite = this.physics.add.sprite(x, y, texture);
    
    // Store isometric data
    sprite.setData('iso', {
      elevation,
      height: 48, // Sprite height for sorting
    });
    
    return sprite;
  }
}
```

## Performance Benchmarks

### Target Metrics
- **60 FPS** with 100 sprites (8-dir animated)
- **<50ms** depth sort time (per frame)
- **<100MB** memory usage
- **<5ms** collision checks (per sprite)

### Profiling Tools
```bash
# Run performance tests
bun run scripts/profile-iso.ts \
  --sprites 100 \
  --duration 60 \
  --output profile.json

# Analyze results
bun run scripts/analyze-profile.ts \
  --input profile.json
```

## Scripts

- `scripts/setup-iso-project.ts` — Initialize Phaser with isometric config
- `scripts/test-depth-sorting.ts` — Verify depth algorithm
- `scripts/benchmark-rendering.ts` — Measure FPS with N sprites
- `scripts/convert-topdown-to-iso.ts` — Migrate existing top-down code

## Usage

```bash
# Setup isometric engine for Spatial Worlds
bun run Skills/phaser-iso-engine/scripts/setup-iso-project.ts \
  --target /home/workspace/Skills/spatial-worlds \
  --replace-topdown

# Test with 100 sprites
bun run scripts/benchmark-rendering.ts \
  --sprites 100 \
  --map crossroads
```

## Integration with Spatial Worlds

This skill provides the **core engine rewrite** needed to switch Spatial Worlds from top-down to isometric:

1. Replace Phaser config
2. Implement depth sorting
3. Convert movement to 8-direction
4. Update camera controller
5. Rewrite collision system

**Critical**: Run this BEFORE continuing Day 2, as it fundamentally changes the rendering pipeline.
