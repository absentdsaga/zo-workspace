import Phaser from 'phaser';
import { TileData } from './MapGenerator';

/**
 * Manages collision detection for isometric maps
 */
export class CollisionManager {
  private tiles: TileData[] = [];
  private tileWidth = 64;
  private tileHeight = 32;
  private mapOffsetX = 0;
  private mapOffsetY = 0;

  /**
   * Set the map tiles for collision detection
   */
  setTiles(tiles: TileData[], mapOffsetX: number = 640, mapOffsetY: number = 360) {
    this.tiles = tiles;
    this.mapOffsetX = mapOffsetX;
    this.mapOffsetY = mapOffsetY;
  }

  /**
   * Check if a position is walkable at a given elevation
   */
  isWalkable(x: number, y: number, elevation: number): boolean {
    const tile = this.getTileAt(x, y);

    if (!tile) return false;
    if (!tile.walkable) return false;

    // Can only walk on tiles at the same elevation
    return tile.elevation === elevation;
  }

  /**
   * Get tile at screen coordinates
   */
  private getTileAt(screenX: number, screenY: number): TileData | null {
    // Convert screen coordinates to isometric grid coordinates
    const gridPos = this.screenToGrid(screenX, screenY);

    // Find tile at grid position
    return this.tiles.find(
      t => t.col === gridPos.col && t.row === gridPos.row
    ) || null;
  }

  /**
   * Get elevation at screen coordinates
   */
  getElevationAt(screenX: number, screenY: number): number {
    const tile = this.getTileAt(screenX, screenY);

    // DEBUG: Log what we're checking
    if (Math.random() < 0.01) { // Log 1% of the time to avoid spam
      const gridPos = this.screenToGrid(screenX, screenY);
      console.log(`🗺️ Elevation check: screen(${Math.round(screenX)},${Math.round(screenY)}) → grid(${gridPos.row},${gridPos.col}) → tile:`, tile ? `elevation=${tile.elevation}` : 'NOT FOUND');
    }

    return tile?.elevation ?? 0;
  }

  /**
   * Convert screen coordinates to grid coordinates
   */
  private screenToGrid(screenX: number, screenY: number): { row: number, col: number } {
    // Account for map offset
    const x = screenX - this.mapOffsetX;
    const y = screenY - this.mapOffsetY;

    // Inverse isometric transformation
    // x = (col - row) * (tileWidth / 2)
    // y = (col + row) * (tileHeight / 2)

    const col = Math.round((x / (this.tileWidth / 2) + y / (this.tileHeight / 2)) / 2);
    const row = Math.round((y / (this.tileHeight / 2) - x / (this.tileWidth / 2)) / 2);

    return { row, col };
  }

  /**
   * Constrain sprite to walkable tiles
   */
  constrainToWalkable(sprite: Phaser.Physics.Arcade.Sprite, elevation: number) {
    const x = sprite.x;
    const y = sprite.y;

    // Check if current position is valid
    if (!this.isWalkable(x, y, elevation)) {
      // Find nearest walkable tile
      const nearest = this.findNearestWalkable(x, y, elevation);
      if (nearest) {
        sprite.setPosition(nearest.x, nearest.y);
      }
    }
  }

  /**
   * Find nearest walkable tile to a position
   */
  private findNearestWalkable(x: number, y: number, elevation: number): { x: number, y: number } | null {
    let nearestDist = Infinity;
    let nearest: { x: number, y: number } | null = null;

    for (const tile of this.tiles) {
      if (tile.walkable && tile.elevation === elevation) {
        // Convert tile grid position to screen position
        const tileX = (tile.col - tile.row) * (this.tileWidth / 2);
        const tileY = (tile.col + tile.row) * (this.tileHeight / 2) - tile.elevation * 20;

        const dist = Phaser.Math.Distance.Between(x, y, tileX, tileY);
        if (dist < nearestDist) {
          nearestDist = dist;
          nearest = { x: tileX, y: tileY };
        }
      }
    }

    return nearest;
  }

  /**
   * Create Phaser physics bodies for platforms
   */
  createPlatformBodies(scene: Phaser.Scene): Phaser.Physics.Arcade.StaticGroup {
    const platforms = scene.physics.add.staticGroup();

    // Group tiles by elevation
    const elevationGroups = new Map<number, TileData[]>();
    for (const tile of this.tiles) {
      if (!tile.walkable) continue;

      if (!elevationGroups.has(tile.elevation)) {
        elevationGroups.set(tile.elevation, []);
      }
      elevationGroups.get(tile.elevation)!.push(tile);
    }

    // Create platform bodies for each elevation
    for (const [elevation, tiles] of elevationGroups) {
      // Find bounding box for this elevation
      const minCol = Math.min(...tiles.map(t => t.col));
      const maxCol = Math.max(...tiles.map(t => t.col));
      const minRow = Math.min(...tiles.map(t => t.row));
      const maxRow = Math.max(...tiles.map(t => t.row));

      // Create a rectangle for the platform
      const centerCol = (minCol + maxCol) / 2;
      const centerRow = (minRow + maxRow) / 2;

      const width = (maxCol - minCol + 1) * this.tileWidth;
      const height = (maxRow - minRow + 1) * this.tileHeight;

      const x = (centerCol - centerRow) * (this.tileWidth / 2);
      const y = (centerCol + centerRow) * (this.tileHeight / 2) - elevation * 20;

      const platform = scene.add.rectangle(x, y, width, height, 0x000000, 0);
      platforms.add(platform);
      platform.setData('elevation', elevation);
    }

    return platforms;
  }
}
