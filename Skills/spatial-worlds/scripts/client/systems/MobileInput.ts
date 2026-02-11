import Phaser from 'phaser';

/**
 * Mobile touch controls with virtual joystick + buttons
 */
export class MobileInput {
  private scene: Phaser.Scene;
  private joystickBase!: Phaser.GameObjects.Circle;
  private joystickThumb!: Phaser.GameObjects.Circle;
  private buttonUp!: Phaser.GameObjects.Container;
  private buttonDown!: Phaser.GameObjects.Container;

  private joystickActive = false;
  private joystickStartX = 0;
  private joystickStartY = 0;

  public inputVector = { x: 0, y: 0 };
  public elevationUp = false;
  public elevationDown = false;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.createControls();
  }

  private createControls() {
    const width = this.scene.scale.width;
    const height = this.scene.scale.height;

    // Virtual Joystick (bottom-left)
    const joystickX = 120;
    const joystickY = height - 120;

    this.joystickBase = this.scene.add.circle(joystickX, joystickY, 60, 0x000000, 0.3);
    this.joystickBase.setStrokeStyle(3, 0x00ff00, 0.8);
    this.joystickBase.setScrollFactor(0);
    this.joystickBase.setDepth(100000);

    this.joystickThumb = this.scene.add.circle(joystickX, joystickY, 30, 0x00ff00, 0.6);
    this.joystickThumb.setScrollFactor(0);
    this.joystickThumb.setDepth(100001);

    // Joystick touch handling
    this.joystickBase.setInteractive();
    this.joystickBase.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      this.joystickActive = true;
      this.joystickStartX = pointer.x;
      this.joystickStartY = pointer.y;
    });

    this.scene.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (this.joystickActive && pointer.isDown) {
        const dx = pointer.x - this.joystickStartX;
        const dy = pointer.y - this.joystickStartY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const maxDistance = 50;

        if (distance > maxDistance) {
          const angle = Math.atan2(dy, dx);
          this.joystickThumb.x = this.joystickStartX + Math.cos(angle) * maxDistance;
          this.joystickThumb.y = this.joystickStartY + Math.sin(angle) * maxDistance;

          this.inputVector.x = Math.cos(angle);
          this.inputVector.y = Math.sin(angle);
        } else {
          this.joystickThumb.x = pointer.x;
          this.joystickThumb.y = pointer.y;

          this.inputVector.x = dx / maxDistance;
          this.inputVector.y = dy / maxDistance;
        }
      }
    });

    this.scene.input.on('pointerup', () => {
      this.joystickActive = false;
      this.joystickThumb.x = joystickX;
      this.joystickThumb.y = joystickY;
      this.inputVector.x = 0;
      this.inputVector.y = 0;
    });

    // Elevation Buttons (bottom-right)
    const buttonX = width - 80;
    const buttonUpY = height - 180;
    const buttonDownY = height - 90;

    // UP button (E)
    this.buttonUp = this.scene.add.container(buttonX, buttonUpY);
    const upCircle = this.scene.add.circle(0, 0, 35, 0x000000, 0.3);
    upCircle.setStrokeStyle(3, 0x00ff00, 0.8);
    const upText = this.scene.add.text(0, 0, '▲', {
      fontSize: '32px',
      color: '#00ff00',
    });
    upText.setOrigin(0.5);
    this.buttonUp.add([upCircle, upText]);
    this.buttonUp.setScrollFactor(0);
    this.buttonUp.setDepth(100000);
    this.buttonUp.setSize(70, 70);
    this.buttonUp.setInteractive();

    this.buttonUp.on('pointerdown', () => {
      this.elevationUp = true;
      upCircle.setFillStyle(0x00ff00, 0.5);
    });

    this.buttonUp.on('pointerup', () => {
      this.elevationUp = false;
      upCircle.setFillStyle(0x000000, 0.3);
    });

    // DOWN button (Q)
    this.buttonDown = this.scene.add.container(buttonX, buttonDownY);
    const downCircle = this.scene.add.circle(0, 0, 35, 0x000000, 0.3);
    downCircle.setStrokeStyle(3, 0x00ff00, 0.8);
    const downText = this.scene.add.text(0, 0, '▼', {
      fontSize: '32px',
      color: '#00ff00',
    });
    downText.setOrigin(0.5);
    this.buttonDown.add([downCircle, downText]);
    this.buttonDown.setScrollFactor(0);
    this.buttonDown.setDepth(100000);
    this.buttonDown.setSize(70, 70);
    this.buttonDown.setInteractive();

    this.buttonDown.on('pointerdown', () => {
      this.elevationDown = true;
      downCircle.setFillStyle(0x00ff00, 0.5);
    });

    this.buttonDown.on('pointerup', () => {
      this.elevationDown = false;
      downCircle.setFillStyle(0x000000, 0.3);
    });
  }

  /**
   * Check if device is mobile
   */
  static isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  /**
   * Hide mobile controls
   */
  hide() {
    this.joystickBase.setVisible(false);
    this.joystickThumb.setVisible(false);
    this.buttonUp.setVisible(false);
    this.buttonDown.setVisible(false);
  }

  /**
   * Show mobile controls
   */
  show() {
    this.joystickBase.setVisible(true);
    this.joystickThumb.setVisible(true);
    this.buttonUp.setVisible(true);
    this.buttonDown.setVisible(true);
  }

  /**
   * Get input as WASD-like object
   */
  getInput() {
    const threshold = 0.15;  // Lowered from 0.3 for better sensitivity
    return {
      up: this.inputVector.y < -threshold,
      down: this.inputVector.y > threshold,
      left: this.inputVector.x < -threshold,
      right: this.inputVector.x > threshold,
    };
  }
}
