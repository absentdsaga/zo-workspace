import Phaser from 'phaser';
import { TileTextureGenerator } from '../systems/TileTextureGenerator';

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' });
  }

  preload() {
    // Create loading bar
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

    this.load.on('progress', (value: number) => {
      progressBar.clear();
      progressBar.fillStyle(0x4a9eff, 1);
      progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
    });

    this.load.on('complete', () => {
      progressBar.destroy();
      progressBox.destroy();
      
      // Hide loading screen
      const loadingEl = document.getElementById('loading');
      if (loadingEl) loadingEl.classList.add('hidden');
    });

    // Load placeholder assets (will replace with real art)
    this.loadPlaceholderAssets();
  }

  loadPlaceholderAssets() {
    // Load Chrono Trigger-style sprites (48×64px)
    console.log('🎨 Loading sprites...');

    // Static sprite
    this.load.image('player', 'assets/sprites/warrior-chrono.png?v=5');

    this.load.on('filecomplete-image-player', () => {
      console.log('✅ Player sprite loaded successfully');
    });

    this.load.on('loaderror', (file: any) => {
      console.error('❌ Failed to load:', file.key, file.url);
    });

    // Walk animation frames (8 directions × 4 frames = 32 sprites)
    const directions = ['south', 'north', 'east', 'west', 'se', 'sw', 'ne', 'nw'];
    for (const direction of directions) {
      for (let i = 0; i < 4; i++) {
        this.load.image(`warrior-${direction}-${i}`, `assets/sprites/warrior-${direction}-${i}.png?v=3`);
      }
    }

    // Generate FFT-style tile textures procedurally
    console.log('🗺️ Generating tile textures...');
    TileTextureGenerator.generateTileTextures(this);

    // Load background
    console.log('🌌 Loading background...');
    this.load.image('background-sky', 'assets/background-sky.png');
  }

  createPlaceholderTiles() {
    const tileSize = 32;
    const colors = {
      grass: 0x5a7a4f,
      stone: 0x6b6b6b,
      water: 0x4a6a8a,
      wall: 0x4a3820,
    };

    Object.entries(colors).forEach(([name, color]) => {
      const graphics = this.make.graphics({}, false);
      graphics.fillStyle(color);
      graphics.fillRect(0, 0, tileSize, tileSize);
      
      // Add subtle texture
      for (let i = 0; i < 10; i++) {
        const brightness = Math.random() * 0.2 - 0.1;
        graphics.fillStyle(Phaser.Display.Color.GetColor(
          ((color >> 16) & 0xff) * (1 + brightness),
          ((color >> 8) & 0xff) * (1 + brightness),
          (color & 0xff) * (1 + brightness)
        ));
        graphics.fillRect(
          Math.random() * tileSize,
          Math.random() * tileSize,
          2, 2
        );
      }

      graphics.generateTexture(name, tileSize, tileSize);
      graphics.destroy();
    });
  }

  createPlaceholderPlayer() {
    const size = 32;
    const graphics = this.make.graphics({}, false);

    // Simple character (circle head + body)
    graphics.fillStyle(0xf4d0a0); // Skin tone
    graphics.fillCircle(size / 2, size / 3, 8); // Head

    graphics.fillStyle(0x4a9eff); // Blue shirt
    graphics.fillRect(size / 2 - 6, size / 3 + 4, 12, 14); // Body

    graphics.fillStyle(0x2c2c2c); // Dark pants
    graphics.fillRect(size / 2 - 5, size / 3 + 16, 4, 10); // Left leg
    graphics.fillRect(size / 2 + 1, size / 3 + 16, 4, 10); // Right leg

    graphics.generateTexture('player', size, size);
    graphics.destroy();
  }

  create() {
    // Move to isometric game scene
    this.scene.start('IsoGameScene');
  }
}
