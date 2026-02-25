import Phaser from 'phaser';

/**
 * Handles 8-direction isometric movement with smooth acceleration
 *
 * Provides tight, responsive controls with physics-based feel
 */
export class IsoMovementController {
  private speed = 200; // Max speed - tuned for responsive feel

  // Isometric grid axes in screen pixels:
  // col+ = (32, 16), row+ = (-32, 16)
  // Normalized: col+ = (0.894, 0.447), row+ = (-0.894, 0.447)
  private static readonly ISO_COL = { x: 0.89443, y: 0.44721 };  // (2,1)/sqrt(5)
  private static readonly ISO_ROW = { x: -0.89443, y: 0.44721 }; // (-2,1)/sqrt(5)

  /**
   * Initialize physics properties on sprite
   * Call this once when creating the player
   */
  initPhysics(sprite: Phaser.Physics.Arcade.Sprite) {
    sprite.setDrag(0, 0);
    sprite.setMaxVelocity(9999, 9999);
  }

  update(
    sprite: Phaser.Physics.Arcade.Sprite,
    cursors: Phaser.Types.Input.Keyboard.CursorKeys,
    wasd: any
  ) {
    const input = {
      up: cursors.up.isDown || wasd.w.isDown,
      down: cursors.down.isDown || wasd.s.isDown,
      left: cursors.left.isDown || wasd.a.isDown,
      right: cursors.right.isDown || wasd.d.isDown,
    };
    this.updateWithInput(sprite, input);
  }

  updateWithInput(
    sprite: Phaser.Physics.Arcade.Sprite,
    input: { up: boolean; down: boolean; left: boolean; right: boolean }
  ) {
    // Build target velocity from isometric grid axes
    let tx = 0, ty = 0;
    const C = IsoMovementController.ISO_COL;
    const R = IsoMovementController.ISO_ROW;

    // Right = +col (SE grid edge), Left = -col (NW grid edge)
    // Down = +row (SW grid edge), Up = -row (NE grid edge)
    if (input.right) { tx += C.x; ty += C.y; }
    if (input.left)  { tx -= C.x; ty -= C.y; }
    if (input.down)  { tx += R.x; ty += R.y; }
    if (input.up)    { tx -= R.x; ty -= R.y; }

    // Normalize so diagonals aren't faster
    const len = Math.sqrt(tx * tx + ty * ty);
    if (len > 0.001) {
      tx = (tx / len) * this.speed;
      ty = (ty / len) * this.speed;
    }

    // Smooth acceleration/deceleration via lerp
    const smoothing = 0.25;
    const vx = sprite.body!.velocity.x;
    const vy = sprite.body!.velocity.y;
    sprite.setVelocity(
      vx + (tx - vx) * smoothing,
      vy + (ty - vy) * smoothing
    );
  }

  getDirection(x: number, y: number): string | null {
    if (x === 0 && y === -1) return 'n';
    if (x === 1 && y === -1) return 'ne';
    if (x === 1 && y === 0) return 'e';
    if (x === 1 && y === 1) return 'se';
    if (x === 0 && y === 1) return 's';
    if (x === -1 && y === 1) return 'sw';
    if (x === -1 && y === 0) return 'w';
    if (x === -1 && y === -1) return 'nw';
    return null;
  }
}
