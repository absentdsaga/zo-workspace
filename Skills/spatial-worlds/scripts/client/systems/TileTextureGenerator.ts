import Phaser from 'phaser';

/**
 * Generate FFT-style tile textures with visible borders and texture variation
 */
export class TileTextureGenerator {
  /**
   * Generate all tile textures for the game
   */
  static generateTileTextures(scene: Phaser.Scene) {
    const tileWidth = 64;
    const tileHeight = 32;

    // Grass tile (Level 0) - green with darker borders
    this.createIsometricTile(scene, 'tile-grass', tileWidth, tileHeight, {
      baseColor: 0x5a8a4f,
      borderColor: 0x3a5a2f,
      textureType: 'grass',
    });

    // Stone tile (Level 1) - gray stone with darker borders
    this.createIsometricTile(scene, 'tile-stone', tileWidth, tileHeight, {
      baseColor: 0x808080,
      borderColor: 0x505050,
      textureType: 'stone',
    });

    // Marble tile (Level 2) - light gray with white veins
    this.createIsometricTile(scene, 'tile-marble', tileWidth, tileHeight, {
      baseColor: 0xa0a0a0,
      borderColor: 0x707070,
      textureType: 'marble',
    });

    // Gold tile (Level 3) - bright gold with dark borders
    this.createIsometricTile(scene, 'tile-gold', tileWidth, tileHeight, {
      baseColor: 0xf0c040,
      borderColor: 0xa08020,
      textureType: 'gold',
    });
  }

  /**
   * Create a single isometric tile texture with FFT-style borders and patterns
   */
  private static createIsometricTile(
    scene: Phaser.Scene,
    key: string,
    width: number,
    height: number,
    options: {
      baseColor: number;
      borderColor: number;
      textureType: 'grass' | 'stone' | 'marble' | 'gold';
    }
  ) {
    const graphics = scene.make.graphics({ x: 0, y: 0 }, false);
    const { baseColor, borderColor, textureType } = options;

    // Draw diamond shape with fill
    graphics.fillStyle(baseColor, 1);
    graphics.beginPath();
    graphics.moveTo(width / 2, 0); // Top
    graphics.lineTo(width, height / 2); // Right
    graphics.lineTo(width / 2, height); // Bottom
    graphics.lineTo(0, height / 2); // Left
    graphics.closePath();
    graphics.fillPath();

    // Add texture variation based on type
    this.addTexturePattern(graphics, width, height, textureType, baseColor);

    // Draw thick visible borders (FFT style)
    graphics.lineStyle(2, borderColor, 1);
    graphics.beginPath();
    graphics.moveTo(width / 2, 0);
    graphics.lineTo(width, height / 2);
    graphics.lineTo(width / 2, height);
    graphics.lineTo(0, height / 2);
    graphics.closePath();
    graphics.strokePath();

    // Generate the texture
    graphics.generateTexture(key, width, height);
    graphics.destroy();
  }

  /**
   * Add texture patterns based on tile type
   */
  private static addTexturePattern(
    graphics: Phaser.GameObjects.Graphics,
    width: number,
    height: number,
    type: string,
    baseColor: number
  ) {
    const r = (baseColor >> 16) & 0xff;
    const g = (baseColor >> 8) & 0xff;
    const b = baseColor & 0xff;

    switch (type) {
      case 'grass':
        // Grass texture - small random dots
        for (let i = 0; i < 30; i++) {
          const x = Math.random() * width;
          const y = Math.random() * height;
          const brightness = Math.random() * 0.3 - 0.15;
          graphics.fillStyle(
            Phaser.Display.Color.GetColor(
              Math.min(255, r * (1 + brightness)),
              Math.min(255, g * (1 + brightness)),
              Math.min(255, b * (1 + brightness))
            ),
            1
          );
          graphics.fillRect(x, y, 2, 2);
        }
        break;

      case 'stone':
        // Stone texture - rectangular blocks
        for (let i = 0; i < 8; i++) {
          const x = (Math.random() * width * 0.8) + width * 0.1;
          const y = (Math.random() * height * 0.8) + height * 0.1;
          const brightness = Math.random() * 0.2 - 0.1;
          graphics.fillStyle(
            Phaser.Display.Color.GetColor(
              Math.min(255, r * (1 + brightness)),
              Math.min(255, g * (1 + brightness)),
              Math.min(255, b * (1 + brightness))
            ),
            0.5
          );
          graphics.fillRect(x, y, 8, 4);
        }
        // Add mortar lines
        graphics.lineStyle(1, 0x505050, 0.3);
        for (let i = 0; i < 5; i++) {
          const y = (i / 4) * height;
          graphics.lineBetween(0, y, width, y);
        }
        break;

      case 'marble':
        // Marble texture - veins
        graphics.lineStyle(1, 0xffffff, 0.3);
        for (let i = 0; i < 5; i++) {
          const startX = Math.random() * width;
          const startY = Math.random() * height;
          graphics.beginPath();
          graphics.moveTo(startX, startY);
          for (let j = 0; j < 3; j++) {
            const endX = startX + (Math.random() - 0.5) * 20;
            const endY = startY + (Math.random() - 0.5) * 20;
            graphics.lineTo(endX, endY);
          }
          graphics.strokePath();
        }
        break;

      case 'gold':
        // Gold texture - sparkle effect
        for (let i = 0; i < 15; i++) {
          const x = Math.random() * width;
          const y = Math.random() * height;
          const brightness = Math.random() * 0.5;
          graphics.fillStyle(
            Phaser.Display.Color.GetColor(
              Math.min(255, r * (1 + brightness)),
              Math.min(255, g * (1 + brightness)),
              Math.min(255, b * (1 + brightness))
            ),
            0.8
          );
          graphics.fillCircle(x, y, 2);
        }
        break;
    }
  }
}
