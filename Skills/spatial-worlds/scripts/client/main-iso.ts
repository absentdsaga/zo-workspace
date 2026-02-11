import Phaser from 'phaser';
import { isoConfig } from './config-iso';

// Initialize isometric game
window.addEventListener('DOMContentLoaded', () => {
  const game = new Phaser.Game(isoConfig);

  // Expose game instance for testing
  (window as any).game = game;

  // Debug info updates
  const updateDebugInfo = () => {
    const scene = game.scene.getScene('IsoGameScene') as any;
    if (scene && scene.player) {
      const fpsEl = document.getElementById('fps');
      const posEl = document.getElementById('position');
      const spriteEl = document.getElementById('sprite-count');

      if (fpsEl) fpsEl.textContent = Math.round(game.loop.actualFps).toString();
      if (posEl && scene.player) {
        const isoData = scene.player.getData('iso');
        posEl.textContent = `${Math.round(scene.player.x)}, ${Math.round(scene.player.y)} [L${isoData?.elevation || 0}]`;
      }
      if (spriteEl && scene.npcs) {
        spriteEl.textContent = (scene.npcs.length + 1).toString();
      }
    }
    requestAnimationFrame(updateDebugInfo);
  };

  updateDebugInfo();
});

export {};
