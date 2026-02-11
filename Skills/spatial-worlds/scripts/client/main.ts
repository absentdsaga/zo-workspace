import Phaser from 'phaser';
import { gameConfig } from './config';

// Initialize game when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  const game = new Phaser.Game(gameConfig);

  // Debug info updates
  const updateDebugInfo = () => {
    const scene = game.scene.getScene('GameScene') as any;
    if (scene && scene.player) {
      const fpsEl = document.getElementById('fps');
      const posEl = document.getElementById('position');
      const spriteEl = document.getElementById('sprite-count');

      if (fpsEl) fpsEl.textContent = Math.round(game.loop.actualFps).toString();
      if (posEl && scene.player) {
        posEl.textContent = `${Math.round(scene.player.x)}, ${Math.round(scene.player.y)}`;
      }
      if (spriteEl && scene.npcs) {
        spriteEl.textContent = scene.npcs.length.toString();
      }
    }
    requestAnimationFrame(updateDebugInfo);
  };

  updateDebugInfo();
});

export {};
