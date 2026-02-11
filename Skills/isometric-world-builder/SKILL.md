---
name: isometric-world-builder
description: Build beautiful isometric tactical RPG worlds with elevated square tiles, multi-level terrain, and proper depth sorting. Integrates with Tiled for map creation.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: game-design
  version: 1.0.0
---

# Isometric World Builder

Design and build isometric worlds with elevated square tiles (Final Fantasy Tactics style) for multiplayer social spaces.

## Visual Style

**Perspective**: 45° isometric with square tiles (not diamond)
**Elevation**: Multi-level terrain (platforms, stairs, cliffs)
**Depth**: Proper z-sorting (characters behind tall objects)

## Tile System

### Isometric Tile Anatomy
```
     Top Face (32×16px diamond)
    /‾‾‾‾‾‾‾‾‾\
   /          \
  /   [grass]  \
 /              \
|    Left Side   |  Right Side
|    (16×H px)   |  (16×H px)
|                |
└────────────────┘
     Base Edge
```

### Tile Specifications
- **Top face**: 32×16px isometric diamond
- **Height**: 4-16px (1-4 elevation levels)
- **Texture**: Grass, stone, wood, water, etc.
- **Edges**: Darker for depth
- **Corners**: Rounded for organic feel

### Tile Types
1. **Ground tiles** (H=4px) — Walkable flat terrain
2. **Platform tiles** (H=8px) — Elevated areas
3. **Cliff tiles** (H=16px) — Non-walkable heights
4. **Stair tiles** — Connect elevations
5. **Slope tiles** — Gradual height changes

## World Design Patterns

### The Crossroads (Isometric Version)

**Layout**:
```
                 [Tower]
                   |
    [Garden]--[Plaza]--[Market]
         |       |        |
    [Fountain] [Inn] [Rooftops]
```

**Elevation Zones**:
- **Plaza**: Level 0 (ground)
- **Fountain**: Level 1 (raised platform, 8px)
- **Rooftops**: Level 2 (accessible via stairs)
- **Tower**: Level 3 (overlook point)

**Key Features**:
- Multi-level design encourages exploration
- Stairs create natural traffic flow
- Elevated areas = intimate zones
- Ground level = social gathering

### Celestial Library (Floating Islands)

**Elevation Strategy**:
- Each island floats at different heights
- Bridges connect platforms
- Vertical space creates drama
- Cloud layers below (parallax)

### Design Principles

1. **Readable Elevation**
   - Height differences obvious at a glance
   - Use color shifts (higher = lighter)
   - Cast shadows from upper levels

2. **Strategic Intimacy**
   - Alcoves on elevated platforms (2-4 people)
   - Ground plazas for crowds (20-50 people)
   - Rooftops for private chats

3. **Vertical Voice Zones**
   - Voice carries on same level (30 tiles)
   - Reduced volume between levels (-50%)
   - Staircases = transition zones

## Tiled Integration

### Setup Isometric Maps in Tiled

1. **Create New Map**:
   - Orientation: **Isometric**
   - Tile width: 32px
   - Tile height: 16px
   - Map size: 50×50 tiles

2. **Tileset Configuration**:
   - Import isometric tileset
   - Set tile properties (walkable, elevation)
   - Define collision shapes (diamond)

3. **Layer Structure**:
   ```
   [Layer 5] Overhead (roofs, tree tops)
   [Layer 4] Objects-High (tall walls, towers)
   [Layer 3] Platforms-Level2 (elevated terrain)
   [Layer 2] Platforms-Level1 (mid-height)
   [Layer 1] Ground-Level0 (base terrain)
   [Layer 0] Shadows (baked ambient occlusion)
   ```

4. **Object Layers**:
   - **Collision**: Define walkable areas per level
   - **Audio Zones**: Mark voice proximity areas
   - **Spawn Points**: Player entry locations
   - **Interactive**: Chairs, doors, levers

### Export for Phaser

```bash
# Export Tiled map to JSON
bun run scripts/export-tiled.ts \
  --input maps/crossroads.tmx \
  --output assets/worlds/crossroads.json
```

## Depth Sorting

### Z-Index Calculation
```typescript
// Sort sprites by Y position + elevation
sprite.depth = (sprite.y + sprite.elevation * 100);
```

### Layering Rules
1. **Background** (depth: -1000): Sky, distant mountains
2. **Terrain** (depth: 0-1000): Ground tiles sorted by Y
3. **Objects** (depth: 1000-5000): Walls, trees, furniture
4. **Characters** (depth: 5000+): Players, NPCs (always on top)
5. **Overhead** (depth: 10000+): Roofs, tree canopy

## Lighting & Shadows

### Isometric Lighting
- **Light source**: Top-right (45° angle)
- **Highlights**: Top-right edges of tiles
- **Shadows**: Bottom-left edges
- **Ambient occlusion**: Darker corners

### Dynamic Shadows
```typescript
// Cast character shadow on tile below
const shadow = this.add.sprite(player.x, player.y + 8, 'shadow');
shadow.setAlpha(0.3);
shadow.setOrigin(0.5, 0);
shadow.depth = player.depth - 1;
```

## Performance Optimization

### Culling Strategy
```typescript
// Only render tiles in viewport + 1 tile margin
const visibleTiles = getVisibleTiles(camera, map);
visibleTiles.forEach(tile => tile.setVisible(true));
```

### Chunk-Based Loading
- Divide world into 25×25 tile chunks
- Load chunks as player moves
- Unload distant chunks
- Maintain 3×3 chunk grid around player

## Advanced Features

### Multi-Level Pathfinding
```typescript
// A* pathfinding with elevation costs
const path = findPath(start, end, {
  elevationCost: 2, // Stairs cost more
  jumpHeight: 1,    // Can't jump more than 1 level
});
```

### Procedural Elevation
```bash
# Generate heightmap from noise
bun run scripts/generate-heightmap.ts \
  --size 50x50 \
  --octaves 3 \
  --output heightmap.png

# Convert to isometric tiles
bun run scripts/heightmap-to-tiles.ts \
  --input heightmap.png \
  --output crossroads-terrain.tmx
```

### Water & Reflections
- Animated water tiles (shimmer effect)
- Reflect sprites below (flipped, alpha 0.3)
- Parallax scrolling for depth

## Scripts

- `scripts/create-isometric-tileset.ts` — Generate tiles from templates
- `scripts/export-tiled.ts` — Convert Tiled maps to Phaser JSON
- `scripts/optimize-depth.ts` — Pre-compute z-index for tiles
- `scripts/bake-shadows.ts` — Render shadow layer
- `scripts/chunk-map.ts` — Split large maps into chunks

## Usage

```bash
# Create The Crossroads
bun run Skills/isometric-world-builder/scripts/create-world.ts \
  --name crossroads \
  --size 50x50 \
  --style medieval \
  --elevation-levels 3

# Export for Spatial Worlds
bun run scripts/export-tiled.ts \
  --input worlds/crossroads.tmx \
  --output /home/workspace/Skills/spatial-worlds/assets/worlds/crossroads.json
```

## Integration with Spatial Worlds

This skill provides the world-building tools for Spatial Worlds:
1. Generate isometric tilesets
2. Design multi-level maps in Tiled
3. Export with proper depth sorting
4. Optimize for real-time multiplayer

Use this skill on **Day 2** of Spatial Worlds development to create The Crossroads.
