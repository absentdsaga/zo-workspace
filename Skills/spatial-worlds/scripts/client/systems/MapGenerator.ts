import Phaser from 'phaser';

/**
 * The Crossroads - Signature world map
 * 50×50 tiles with 4 elevation levels
 */
export class MapGenerator {
  private tileWidth = 64;
  private tileHeight = 32;

  /**
   * Generate The Crossroads map
   * Returns: { tiles: TileData[], spawnPoints: SpawnPoint[] }
   */
  generateCrossroads() {
    const mapSize = 50;
    const tiles: TileData[] = [];
    const spawnPoints: SpawnPoint[] = [];

    // Create base terrain
    for (let row = 0; row < mapSize; row++) {
      for (let col = 0; col < mapSize; col++) {
        const elevation = this.getElevationAt(row, col, mapSize);
        const tileType = this.getTileTypeAt(row, col, elevation);

        tiles.push({
          row,
          col,
          elevation,
          type: tileType,
          walkable: tileType !== 'void',
        });
      }
    }

    // Add spawn points at different elevations
    spawnPoints.push(
      { x: 25, y: 25, elevation: 0, name: 'center-ground' },
      { x: 10, y: 10, elevation: 1, name: 'nw-platform' },
      { x: 40, y: 10, elevation: 1, name: 'ne-platform' },
      { x: 10, y: 40, elevation: 2, name: 'sw-platform' },
      { x: 40, y: 40, elevation: 2, name: 'se-platform' },
      { x: 25, y: 10, elevation: 3, name: 'north-tower' },
      { x: 25, y: 40, elevation: 3, name: 'south-tower' },
    );

    return { tiles, spawnPoints };
  }

  /**
   * Determine elevation based on position (creates interesting terrain)
   */
  private getElevationAt(row: number, col: number, size: number): number {
    const centerX = size / 2;
    const centerY = size / 2;
    const distFromCenter = Math.sqrt(
      Math.pow(col - centerX, 2) + Math.pow(row - centerY, 2)
    );

    // Center area is ground level (0)
    if (distFromCenter < 8) {
      return 0;
    }

    // Four quadrants with different elevations
    const quadrant = this.getQuadrant(row, col, centerY, centerX);

    // Create elevated platforms in corners
    if (distFromCenter > 15 && distFromCenter < 20) {
      switch (quadrant) {
        case 'nw':
        case 'ne':
          return 1;
        case 'sw':
        case 'se':
          return 2;
      }
    }

    // Towers in north/south
    if (Math.abs(col - centerX) < 3) {
      if (row < centerY - 10) return 3; // North tower
      if (row > centerY + 10) return 3; // South tower
    }

    // Default ground level
    return 0;
  }

  /**
   * Determine tile type based on position and elevation
   */
  private getTileTypeAt(row: number, col: number, elevation: number): TileType {
    // Void tiles at map edges
    if (row < 2 || row > 47 || col < 2 || col > 47) {
      return 'void';
    }

    // Different tile types based on elevation
    switch (elevation) {
      case 0:
        return 'grass';
      case 1:
        return 'stone';
      case 2:
        return 'marble';
      case 3:
        return 'gold';
      default:
        return 'grass';
    }
  }

  /**
   * Get quadrant (nw, ne, sw, se)
   */
  private getQuadrant(
    row: number,
    col: number,
    centerY: number,
    centerX: number
  ): 'nw' | 'ne' | 'sw' | 'se' {
    if (row < centerY) {
      return col < centerX ? 'nw' : 'ne';
    } else {
      return col < centerX ? 'sw' : 'se';
    }
  }

  /**
   * Convert grid position to isometric screen position
   */
  toIso(row: number, col: number, elevation: number = 0) {
    const x = (col - row) * (this.tileWidth / 2);
    const y = (col + row) * (this.tileHeight / 2) - elevation * 20;
    return { x, y };
  }

  /**
   * Render the map to a Phaser scene
   */
  renderMap(scene: Phaser.Scene, centerX: number, centerY: number) {
    const { tiles } = this.generateCrossroads();
    const graphics = scene.add.graphics();
    const container = scene.add.container(0, 0);

    // Texture names for different tile types
    const textureMap = {
      grass: 'tile-grass',
      stone: 'tile-stone',
      marble: 'tile-marble',
      gold: 'tile-gold',
      void: null,
    };

    // Color palette for elevation walls (FFT-style - brighter, more visible)
    const colors = {
      grass: 0x5a8a4f,      // Brighter green
      stone: 0x8a8a8a,      // Lighter gray
      marble: 0xb0b0b0,     // Bright gray
      gold: 0xf0c040,       // Bright gold
      void: 0x1a1a1a,
    };

    // Render tiles
    for (const tile of tiles) {
      if (!tile.walkable) continue; // Skip void tiles

      const pos = this.toIso(tile.row, tile.col, tile.elevation);
      const x = pos.x + centerX;
      const y = pos.y + centerY;

      // Use textured sprite for tile surface
      const textureName = textureMap[tile.type];
      if (textureName && scene.textures.exists(textureName)) {
        const tileSprite = scene.add.image(x, y + this.tileHeight / 2, textureName);
        tileSprite.setOrigin(0.5, 0.5);
        tileSprite.setDepth(0);
        container.add(tileSprite);
      } else {
        // Fallback to graphics if texture not loaded (FFT-style grid)
        // Brighter, more visible borders like Final Fantasy Tactics
        graphics.lineStyle(2, 0x2a4a2f, 0.8);  // Darker green border, visible
        graphics.fillStyle(colors[tile.type], 1);
        graphics.beginPath();
        graphics.moveTo(x, y);
        graphics.lineTo(x + this.tileWidth / 2, y + this.tileHeight / 2);
        graphics.lineTo(x, y + this.tileHeight);
        graphics.lineTo(x - this.tileWidth / 2, y + this.tileHeight / 2);
        graphics.closePath();
        graphics.fillPath();
        graphics.strokePath();
      }

      // Draw elevation walls (if elevated)
      if (tile.elevation > 0) {
        const wallHeight = tile.elevation * 20;

        // Left wall (darker)
        graphics.fillStyle(colors[tile.type] * 0.7, 1);
        graphics.beginPath();
        graphics.moveTo(x - this.tileWidth / 2, y + this.tileHeight / 2);
        graphics.lineTo(x, y + this.tileHeight);
        graphics.lineTo(x, y + this.tileHeight + wallHeight);
        graphics.lineTo(
          x - this.tileWidth / 2,
          y + this.tileHeight / 2 + wallHeight
        );
        graphics.closePath();
        graphics.fillPath();

        // Right wall (medium)
        graphics.fillStyle(colors[tile.type] * 0.5, 1);
        graphics.beginPath();
        graphics.moveTo(x, y + this.tileHeight);
        graphics.lineTo(x + this.tileWidth / 2, y + this.tileHeight / 2);
        graphics.lineTo(
          x + this.tileWidth / 2,
          y + this.tileHeight / 2 + wallHeight
        );
        graphics.lineTo(x, y + this.tileHeight + wallHeight);
        graphics.closePath();
        graphics.fillPath();
      }
    }

    graphics.setDepth(0);
    container.setDepth(0);
    return { graphics, container };
  }
}

// Type definitions
export interface TileData {
  row: number;
  col: number;
  elevation: number;
  type: TileType;
  walkable: boolean;
}

export interface SpawnPoint {
  x: number;
  y: number;
  elevation: number;
  name: string;
}

export type TileType = 'grass' | 'stone' | 'marble' | 'gold' | 'void';
