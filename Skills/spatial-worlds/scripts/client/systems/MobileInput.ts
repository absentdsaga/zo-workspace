import Phaser from 'phaser';

/**
 * Mobile touch controls — uses native DOM touch/pointer events directly on
 * the canvas, bypassing Phaser's input manager entirely. This is the most
 * reliable approach across all mobile browsers.
 */
export class MobileInput {
  private scene: Phaser.Scene;
  private joystickBase!: Phaser.GameObjects.Circle;
  private joystickThumb!: Phaser.GameObjects.Circle;
  private buttonUp!: Phaser.GameObjects.Container;
  private buttonDown!: Phaser.GameObjects.Container;

  private joystickTouchId = -1;
  private joystickStartX = 0;
  private joystickStartY = 0;

  private restX = 120;
  private restY = 0;

  public inputVector = { x: 0, y: 0 };
  public elevationUp = false;
  public elevationDown = false;

  // Hysteresis: once moving, use a lower threshold to stop
  private _isMoving = false;

  // Track elevation button touch IDs so they don't interfere with joystick
  private upTouchId = -1;
  private downTouchId = -1;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.createControls();
    this.attachNativeEvents();
  }

  private createControls() {
    const width = this.scene.scale.width;
    const height = this.scene.scale.height;

    this.restX = 120;
    this.restY = height - 120;

    // Joystick visuals
    this.joystickBase = this.scene.add.circle(this.restX, this.restY, 60, 0x000000, 0.3);
    this.joystickBase.setStrokeStyle(3, 0x00ff00, 0.8);
    this.joystickBase.setScrollFactor(0);
    this.joystickBase.setDepth(100000);

    this.joystickThumb = this.scene.add.circle(this.restX, this.restY, 30, 0x00ff00, 0.6);
    this.joystickThumb.setScrollFactor(0);
    this.joystickThumb.setDepth(100001);

    // Elevation Buttons (bottom-right)
    const buttonX = width - 80;

    this.buttonUp = this.scene.add.container(buttonX, height - 180);
    const upCircle = this.scene.add.circle(0, 0, 35, 0x000000, 0.3);
    upCircle.setStrokeStyle(3, 0x00ff00, 0.8);
    const upText = this.scene.add.text(0, 0, '▲', { fontSize: '32px', color: '#00ff00' });
    upText.setOrigin(0.5);
    this.buttonUp.add([upCircle, upText]);
    this.buttonUp.setScrollFactor(0).setDepth(100000).setSize(70, 70).setInteractive();
    this.buttonUp.on('pointerdown', () => { this.elevationUp = true; upCircle.setFillStyle(0x00ff00, 0.5); });
    this.buttonUp.on('pointerup', () => { this.elevationUp = false; upCircle.setFillStyle(0x000000, 0.3); });

    this.buttonDown = this.scene.add.container(buttonX, height - 90);
    const downCircle = this.scene.add.circle(0, 0, 35, 0x000000, 0.3);
    downCircle.setStrokeStyle(3, 0x00ff00, 0.8);
    const downText = this.scene.add.text(0, 0, '▼', { fontSize: '32px', color: '#00ff00' });
    downText.setOrigin(0.5);
    this.buttonDown.add([downCircle, downText]);
    this.buttonDown.setScrollFactor(0).setDepth(100000).setSize(70, 70).setInteractive();
    this.buttonDown.on('pointerdown', () => { this.elevationDown = true; downCircle.setFillStyle(0x00ff00, 0.5); });
    this.buttonDown.on('pointerup', () => { this.elevationDown = false; downCircle.setFillStyle(0x000000, 0.3); });
  }

  private attachNativeEvents() {
    const canvas = this.scene.sys.game.canvas;
    const width = this.scene.scale.width;

    const onTouchStart = (e: TouchEvent) => {
      for (const touch of Array.from(e.changedTouches)) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = this.scene.scale.width / rect.width;
        const scaleY = this.scene.scale.height / rect.height;
        const x = (touch.clientX - rect.left) * scaleX;
        const y = (touch.clientY - rect.top) * scaleY;

        // Joystick: left 60% of screen, not already active
        if (x < width * 0.6 && this.joystickTouchId === -1) {
          this.joystickTouchId = touch.identifier;
          this.joystickStartX = x;
          this.joystickStartY = y;
          // Snap base to touch origin
          this.joystickBase.x = x;
          this.joystickBase.y = y;
          this.joystickThumb.x = x;
          this.joystickThumb.y = y;
        }
      }
    };

    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      for (const touch of Array.from(e.changedTouches)) {
        if (touch.identifier !== this.joystickTouchId) continue;
        const rect = canvas.getBoundingClientRect();
        const scaleX = this.scene.scale.width / rect.width;
        const scaleY = this.scene.scale.height / rect.height;
        const x = (touch.clientX - rect.left) * scaleX;
        const y = (touch.clientY - rect.top) * scaleY;

        const dx = x - this.joystickStartX;
        const dy = y - this.joystickStartY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = 50;

        if (dist > 0) {
          const nx = dx / dist;
          const ny = dy / dist;
          const clamped = Math.min(dist, maxDist);
          this.joystickThumb.x = this.joystickStartX + nx * clamped;
          this.joystickThumb.y = this.joystickStartY + ny * clamped;
          this.inputVector.x = nx * (clamped / maxDist);
          this.inputVector.y = ny * (clamped / maxDist);
        }
      }
    };

    const onTouchEnd = (e: TouchEvent) => {
      for (const touch of Array.from(e.changedTouches)) {
        if (touch.identifier === this.joystickTouchId) {
          this.joystickTouchId = -1;
          this.joystickBase.x = this.restX;
          this.joystickBase.y = this.restY;
          this.joystickThumb.x = this.restX;
          this.joystickThumb.y = this.restY;
          this.inputVector.x = 0;
          this.inputVector.y = 0;
        }
      }
    };

    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd, { passive: false });
    canvas.addEventListener('touchcancel', onTouchEnd, { passive: false });
  }

  static isMobile(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  hide() {
    this.joystickBase.setVisible(false);
    this.joystickThumb.setVisible(false);
    this.buttonUp.setVisible(false);
    this.buttonDown.setVisible(false);
  }

  show() {
    this.joystickBase.setVisible(true);
    this.joystickThumb.setVisible(true);
    this.buttonUp.setVisible(true);
    this.buttonDown.setVisible(true);
  }

  getInput() {
    const onThreshold = 0.15;
    const offThreshold = 0.08;
    const mag = Math.sqrt(this.inputVector.x ** 2 + this.inputVector.y ** 2);

    if (!this._isMoving && mag >= onThreshold) this._isMoving = true;
    else if (this._isMoving && mag < offThreshold) this._isMoving = false;

    const t = this._isMoving ? offThreshold : onThreshold;
    return {
      up:    this.inputVector.y < -t,
      down:  this.inputVector.y > t,
      left:  this.inputVector.x < -t,
      right: this.inputVector.x > t,
    };
  }
}
