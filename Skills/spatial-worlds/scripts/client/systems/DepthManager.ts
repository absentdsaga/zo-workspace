import Phaser from 'phaser';

export interface IsoData {
  elevation: number; // 0, 1, 2, 3...
  height: number;    // Sprite height in pixels
}

/**
 * Manages depth sorting for isometric rendering
 * 
 * Formula: depth = (elevation × 10000) + (y × 100) + height
 * 
 * This ensures:
 * - Higher elevations render in front
 * - Within same elevation, lower Y (farther back) renders behind
 * - Taller objects render in front of shorter ones at same position
 */
export class DepthManager {
  calculateDepth(x: number, y: number, elevation: number, height: number): number {
    return (
      elevation * 10000 +  // Elevation layers (0-30,000)
      y * 100 +            // Y position (0-72,000 for 720px tall screen)
      height               // Object height (0-100 typically)
    );
  }
  
  /**
   * Update all sprite depths in scene
   * Call this every frame in scene.update()
   *
   * OPTIMIZED: Only recalculates depth if sprite moved
   */
  updateDepths(scene: Phaser.Scene) {
    const children = scene.children.list;

    children.forEach(child => {
      if (child instanceof Phaser.GameObjects.Sprite ||
          child instanceof Phaser.Physics.Arcade.Sprite) {

        const isoData = child.getData('iso') as IsoData | undefined;

        if (isoData) {
          // Check if sprite moved (optimization)
          const lastY = child.getData('lastY') as number | undefined;
          const lastElevation = child.getData('lastElevation') as number | undefined;

          if (lastY !== child.y || lastElevation !== isoData.elevation) {
            const depth = this.calculateDepth(
              child.x,
              child.y,
              isoData.elevation,
              isoData.height
            );

            child.setDepth(depth);
            child.setData('lastY', child.y);
            child.setData('lastElevation', isoData.elevation);
          }
        }
      }
    });
  }
  
  /**
   * Set isometric data on sprite and adjust visual Y position for elevation
   *
   * IMPORTANT: We store a "logicalY" for collision detection that doesn't change,
   * and only adjust the visual sprite.y for rendering. This prevents feedback loops.
   */
  setIsoData(sprite: Phaser.GameObjects.Sprite, elevation: number, height: number) {
    const oldData = sprite.getData('iso') as IsoData | undefined;
    const oldElevation = oldData?.elevation || 0;

    // Store logical Y position on first call
    if (!sprite.getData('logicalY')) {
      sprite.setData('logicalY', sprite.y);
    }

    sprite.setData('iso', { elevation, height } as IsoData);

    // Update visual Y based on elevation, but keep logicalY unchanged
    // Must match MapGenerator.toIso() offset: elevation * 20px
    const logicalY = sprite.getData('logicalY') as number;
    sprite.y = logicalY - (elevation * 20); // Visual offset: higher elevation = lower Y on screen
  }
}
