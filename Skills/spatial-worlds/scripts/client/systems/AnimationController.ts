import Phaser from 'phaser';

/**
 * Handles sprite animations for walking
 */
export class AnimationController {
  private currentDirection: string = 'south';
  private isMoving: boolean = false;

  /**
   * Create animations for a sprite
   */
  createAnimations(scene: Phaser.Scene) {
    const directions = ['south', 'north', 'east', 'west', 'se', 'sw', 'ne', 'nw'];

    // Create walk animation for each direction
    for (const direction of directions) {
      const animKey = `walk-${direction}`;
      if (!scene.anims.exists(animKey)) {
        scene.anims.create({
          key: animKey,
          frames: [
            { key: `warrior-${direction}-0` },
            { key: `warrior-${direction}-1` },
            { key: `warrior-${direction}-0` },
            { key: `warrior-${direction}-3` },
          ],
          frameRate: 8,
          repeat: -1
        });
      }
    }

    // Create idle animation for each direction (first frame of walk cycle)
    for (const direction of directions) {
      const idleKey = `idle-${direction}`;
      if (!scene.anims.exists(idleKey)) {
        scene.anims.create({
          key: idleKey,
          frames: [{ key: `warrior-${direction}-0` }],
          frameRate: 1,
          repeat: -1
        });
      }
    }
  }

  /**
   * Update animation based on movement
   */
  update(sprite: Phaser.Physics.Arcade.Sprite, velocity: { x: number, y: number }) {
    const isMoving = velocity.x !== 0 || velocity.y !== 0;

    if (isMoving) {
      // Determine direction from velocity
      const direction = this.getDirectionFromVelocity(velocity.x, velocity.y);
      const animKey = `walk-${direction}`;

      // Only change animation if direction changed
      if (sprite.anims.currentAnim?.key !== animKey) {
        sprite.play(animKey);
        this.currentDirection = direction;
      }
    } else {
      // Idle - use directional idle animation
      const idleKey = `idle-${this.currentDirection}`;
      if (sprite.anims.currentAnim?.key !== idleKey) {
        sprite.play(idleKey);
      }
    }
  }

  /**
   * Get direction string from velocity vector
   */
  private getDirectionFromVelocity(vx: number, vy: number): string {
    // Normalize velocity to get angle
    const angle = Math.atan2(vy, vx);
    const degrees = angle * (180 / Math.PI);

    // Convert to 0-360 range
    const normalizedDegrees = (degrees + 360) % 360;

    // Map to 8 directions (each direction is 45 degrees)
    // East = 0°, South = 90°, West = 180°, North = 270°
    if (normalizedDegrees >= 337.5 || normalizedDegrees < 22.5) {
      return 'east';
    } else if (normalizedDegrees >= 22.5 && normalizedDegrees < 67.5) {
      return 'se';
    } else if (normalizedDegrees >= 67.5 && normalizedDegrees < 112.5) {
      return 'south';
    } else if (normalizedDegrees >= 112.5 && normalizedDegrees < 157.5) {
      return 'sw';
    } else if (normalizedDegrees >= 157.5 && normalizedDegrees < 202.5) {
      return 'west';
    } else if (normalizedDegrees >= 202.5 && normalizedDegrees < 247.5) {
      return 'nw';
    } else if (normalizedDegrees >= 247.5 && normalizedDegrees < 292.5) {
      return 'north';
    } else {
      return 'ne';
    }
  }
}
