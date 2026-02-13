import Phaser from 'phaser';
import { BootScene } from './scenes/Boot';
import { IsoGameScene } from './scenes/IsoGame-NFT-TEST';  // TEST VERSION

export const isoConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
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
      debugShowBody: false,
      debugShowVelocity: false,
      debugShowStaticBody: false,
      gravity: { x: 0, y: 0 },
      tileBias: 16,
    },
  },

  render: {
    batchSize: 2048,
    maxTextures: 8,
    antialias: false,
    pixelArt: true,
  },

  scene: [BootScene, IsoGameScene],

  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },

  fps: {
    target: 60,
    forceSetTimeOut: true,
  },
};
