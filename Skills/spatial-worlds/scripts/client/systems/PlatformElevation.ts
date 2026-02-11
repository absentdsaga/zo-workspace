/**
 * Manages automatic elevation changes based on player position
 * Similar to Final Fantasy Tactics - walking onto a platform auto-adjusts elevation
 */

interface Platform {
  x: number;      // Center X of platform (isometric)
  y: number;      // Center Y of platform (isometric)
  width: number;  // Width in isometric space
  height: number; // Height in isometric space
  elevation: number;
}

export class PlatformElevationManager {
  private platforms: Platform[] = [];

  /**
   * Register a platform for elevation detection
   */
  addPlatform(x: number, y: number, width: number, height: number, elevation: number) {
    this.platforms.push({ x, y, width, height, elevation });
  }

  /**
   * Get the elevation level at a given position
   * Returns the highest elevation platform the position is on
   */
  getElevationAt(x: number, y: number): number {
    let maxElevation = 0;

    for (const platform of this.platforms) {
      if (this.isPointOnPlatform(x, y, platform)) {
        maxElevation = Math.max(maxElevation, platform.elevation);
      }
    }

    return maxElevation;
  }

  /**
   * Check if a point is within an isometric diamond (platform bounds)
   */
  private isPointOnPlatform(x: number, y: number, platform: Platform): boolean {
    // Convert to local coordinates relative to platform center
    const localX = x - platform.x;
    const localY = y - platform.y;

    // Isometric diamond hit test
    // A point is inside if: |localX / halfWidth| + |localY / halfHeight| <= 1
    const halfWidth = platform.width / 2;
    const halfHeight = platform.height / 2;

    const normalizedDistance = Math.abs(localX / halfWidth) + Math.abs(localY / halfHeight);

    return normalizedDistance <= 1.0;
  }

  /**
   * Clear all platforms
   */
  clear() {
    this.platforms = [];
  }
}
