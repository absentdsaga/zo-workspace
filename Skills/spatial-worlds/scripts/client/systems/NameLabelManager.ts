import Phaser from 'phaser';

export class NameLabelManager {
  private labels = new Map<string, Phaser.GameObjects.Text>();
  private scene: Phaser.Scene;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  createLabel(playerId: string, playerName: string, x: number, y: number): void {
    // Remove existing label if any
    this.removeLabel(playerId);

    // Create text label
    const label = this.scene.add.text(x, y - 40, playerName, {
      fontSize: '12px',
      color: '#ffffff',
      backgroundColor: '#000000',
      padding: { x: 6, y: 3 },
      stroke: '#000000',
      strokeThickness: 2
    });

    label.setOrigin(0.5, 1);
    label.setDepth(1000000); // Always on top
    label.setData('playerId', playerId);

    this.labels.set(playerId, label);
  }

  updateLabel(playerId: string, x: number, y: number): void {
    const label = this.labels.get(playerId);
    if (label) {
      label.setPosition(x, y - 40);
    }
  }

  removeLabel(playerId: string): void {
    const label = this.labels.get(playerId);
    if (label) {
      label.destroy();
      this.labels.delete(playerId);
    }
  }

  setLabelName(playerId: string, name: string): void {
    const label = this.labels.get(playerId);
    if (label) {
      label.setText(name);
    }
  }

  destroy(): void {
    this.labels.forEach(label => label.destroy());
    this.labels.clear();
  }
}
