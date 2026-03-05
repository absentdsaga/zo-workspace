import Phaser from 'phaser';
import { DepthManager } from '../systems/DepthManager';
import { IsoMovementController } from '../systems/IsoMovement';
import { AnimationController } from '../systems/AnimationController';
import { MapGenerator } from '../systems/MapGenerator';
import { CollisionManager } from '../systems/CollisionManager';
import { MultiplayerManager } from '../MultiplayerManager';
import { VoiceManager } from '../systems/VoiceManager';
import { MobileInput } from '../systems/MobileInput';
import { PlatformElevationManager } from '../systems/PlatformElevation';

// 🎨 Full character pool — each client picks one at random on connect
const CHARACTER_POOL = ['hero_orange', 'hero_blue', 'hero_purple', 'hero_green'];

// Pick local character: use ?char=hero_blue URL param, or random
function pickLocalCharacter(): string {
  const params = new URLSearchParams(window.location.search);
  const forced = params.get('char');
  if (forced && CHARACTER_POOL.includes(forced)) return forced;
  return CHARACTER_POOL[Math.floor(Math.random() * CHARACTER_POOL.length)];
}

const LOCAL_CHARACTER = pickLocalCharacter();

// 🎨 ALL 24 NFT CHARACTERS (used for NPCs)
const NFT_CHARACTERS = [
  'set1-char1', 'set1-char2', 'set1-char3', 'set1-char4', 'set1-char5', 'set1-char6',
  'set2-char1', 'set2-char2', 'set2-char3', 'set2-char4', 'set2-char5', 'set2-char6',
  'set3-char1', 'set3-char2', 'set3-char3', 'set3-char4', 'set3-char5', 'set3-char6',
  'set4-char1', 'set4-char2', 'set4-char3', 'set4-char4', 'set4-char5', 'set4-char6'
];

// All characters that have animations
const ALL_CHARACTERS = [...CHARACTER_POOL];

export class IsoGameScene extends Phaser.Scene {
  private depthManager!: DepthManager;
  private movementController!: IsoMovementController;
  private animationController!: AnimationController;
  private mapGenerator!: MapGenerator;
  private collisionManager!: CollisionManager;
  private platformElevation!: PlatformElevationManager;
  private player!: Phaser.Physics.Arcade.Sprite;
  private npcs: Phaser.Physics.Arcade.Sprite[] = [];
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasd!: any;
  private mapData!: { tiles: any[], spawnPoints: any[] };
  private multiplayerManager!: MultiplayerManager;
  private voiceManager!: VoiceManager;
  private mobileInput?: MobileInput;
  private isMobile = false;
  private frameCounter: number = 0;
  private walkTick: number = 0;
  private playerShadow!: Phaser.GameObjects.Ellipse;
  private debugText!: Phaser.GameObjects.Text;

  constructor() {
    super({ key: 'IsoGameScene' });
  }

  preload() {
    // 🎨 Load all character sprites from pool
    for (const charId of CHARACTER_POOL) {
      this.load.spritesheet(charId, `assets/sprites/nft-characters-xxl/${charId}/${charId}-sheet.png`, {
        frameWidth: 64,
        frameHeight: 64
      });
    }

  }

  create() {
    // Add background sky gradient
    this.add.image(640, 360, 'background-sky').setDepth(-1000).setScrollFactor(0.2);

    // Initialize systems
    this.depthManager = new DepthManager();
    this.movementController = new IsoMovementController();
    this.animationController = new AnimationController();
    this.mapGenerator = new MapGenerator();
    this.collisionManager = new CollisionManager();
    this.platformElevation = new PlatformElevationManager();

    // Initialize multiplayer (server handles character identity)
    this.multiplayerManager = new MultiplayerManager(this, LOCAL_CHARACTER);

    // Connect to multiplayer server
    const wsUrl = window.location.protocol === 'https:'
      ? `wss://${window.location.host}`
      : `ws://${window.location.host}`;
    this.multiplayerManager.connect(wsUrl);
    console.log('🔌 Connecting to multiplayer server:', wsUrl);

    // Initialize voice chat
    this.voiceManager = new VoiceManager();
    this.initializeVoiceChat();

    // 🎨 Create NFT animations for all 24 characters
    this.createNFTAnimations();

    // Create old warrior animations for fallback
    this.animationController.createAnimations(this);

    // Create The Crossroads map (complex 50x50 tile map)
    this.createCrossroadsMap();

    // Create player
    this.createPlayer();
    
    // Create test NPCs (25 for 60 FPS target)
    this.createNPCs(5);
    
    // Setup camera
    this.setupCamera();
    
    // Setup input
    this.setupInput();

    // Setup mobile controls if on mobile device
    this.isMobile = MobileInput.isMobile();
    if (this.isMobile) {
      this.mobileInput = new MobileInput(this);
      console.log('📱 Mobile controls enabled');
    }

    // Instructions
    this.add.text(20, 20, `SPATIAL WORLDS - The Crossroads\nWASD/Arrows: Move | Auto-Elevation: ON\nProximity Voice Chat: ON\n\n🎨 ${NFT_CHARACTERS.length} Diverse NFT Characters!\nWatch them roam across 4 elevation levels`, {
      fontSize: '14px',
      color: '#00ff00',
      backgroundColor: '#000000',
      padding: { x: 10, y: 10 },
    }).setScrollFactor(0).setDepth(100000);

    this.debugText = this.add.text(20, 120, '', { fontSize: '12px', color: '#ffff00', backgroundColor: '#000000', padding: { x: 5, y: 5 } }).setScrollFactor(0).setDepth(200000);
  }

  async initializeVoiceChat() {
    try {
      await this.voiceManager.createRoom();
      console.log('✅ Voice chat initialized');
    } catch (error) {
      console.warn('⚠️ Voice chat failed to initialize:', error);
      console.warn('Continuing without voice chat');
    }
  }

  createCrossroadsMap() {
    // Render The Crossroads using MapGenerator
    const centerX = 640;
    const centerY = 360;
    const { tiles } = this.mapGenerator.generateCrossroads();

    // Render the map
    this.mapGenerator.renderMap(this, centerX, centerY);

    // Register all elevated tiles for automatic elevation detection
    const tileWidth = 64;
    const tileHeight = 32;

    for (const tile of tiles) {
      if (tile.elevation > 0 && tile.walkable) {
        const pos = this.mapGenerator.toIso(tile.row, tile.col, tile.elevation);
        const x = pos.x + centerX;
        const y = pos.y + centerY;

        // Register diamond-shaped collision area for this elevated tile
        this.platformElevation.addPlatform(x, y + tileHeight / 2, tileWidth, tileHeight, tile.elevation);
      }
    }

    console.log(`📍 Registered ${tiles.filter(t => t.elevation > 0).length} elevated platforms`);
  }

  createIsoWorld() {
    const graphics = this.add.graphics();

    // Draw isometric grid (15x15 tiles for larger world)
    const tileWidth = 64;  // Width of isometric tile
    const tileHeight = 32; // Height of isometric tile

    // Ground level (Level 0) - centered at camera/player position
    const centerX = 640;  // Center of 1280px width
    const centerY = 360;  // Center of 720px height

    for (let row = 0; row < 15; row++) {
      for (let col = 0; col < 15; col++) {
        // Calculate isometric position (centered)
        const x = (col - row) * (tileWidth / 2) + centerX;
        const y = (col + row) * (tileHeight / 2) + centerY - 200;  // Offset up

        // Vary ground color based on position
        const variation = Math.sin(row * 0.5) * 0.1 + Math.cos(col * 0.5) * 0.1;
        const baseColor = 0x4a6a3f;

        // Draw isometric tile (diamond shape for ground)
        graphics.lineStyle(2, 0x3a5a2f, 1);  // Thicker, more visible lines
        graphics.fillStyle(baseColor, 1);     // Fully opaque

        graphics.beginPath();
        graphics.moveTo(x, y);                    // Top
        graphics.lineTo(x + tileWidth / 2, y + tileHeight / 2); // Right
        graphics.lineTo(x, y + tileHeight);       // Bottom
        graphics.lineTo(x - tileWidth / 2, y + tileHeight / 2); // Left
        graphics.closePath();
        graphics.fillPath();
        graphics.strokePath();
      }
    }

    // LEVEL 1 PLATFORMS (elevated 20px) - positioned relative to center
    this.drawIsoPlatform(graphics, centerX - 200, centerY - 100, 96, 48, 20, 0x6a8a5f);
    this.drawIsoPlatform(graphics, centerX + 100, centerY - 100, 96, 48, 20, 0x6a8a5f);
    this.drawIsoPlatform(graphics, centerX, centerY, 128, 64, 20, 0x7a9a6f);

    // LEVEL 2 PLATFORMS (elevated 40px)
    this.drawIsoPlatform(graphics, centerX - 300, centerY + 50, 80, 40, 40, 0x8aaa7f);
    this.drawIsoPlatform(graphics, centerX + 200, centerY + 50, 80, 40, 40, 0x8aaa7f);

    // LEVEL 3 PLATFORM (elevated 60px - highest point)
    this.drawIsoPlatform(graphics, centerX, centerY + 150, 96, 48, 60, 0x9aba8f);

    // Add some decorative lower platforms
    this.drawIsoPlatform(graphics, centerX - 350, centerY - 150, 64, 32, 10, 0x5a7a4f);
    this.drawIsoPlatform(graphics, centerX + 250, centerY - 150, 64, 32, 10, 0x5a7a4f);

    graphics.setDepth(0); // Ground layer (render above background, below sprites)

    // Register all platforms for elevation detection
    // LEVEL 1 PLATFORMS
    this.platformElevation.addPlatform(centerX - 200, centerY - 100, 96, 48, 1);
    this.platformElevation.addPlatform(centerX + 100, centerY - 100, 96, 48, 1);
    this.platformElevation.addPlatform(centerX, centerY, 128, 64, 1);

    // LEVEL 2 PLATFORMS
    this.platformElevation.addPlatform(centerX - 300, centerY + 50, 80, 40, 2);
    this.platformElevation.addPlatform(centerX + 200, centerY + 50, 80, 40, 2);

    // LEVEL 3 PLATFORM
    this.platformElevation.addPlatform(centerX, centerY + 150, 96, 48, 3);
  }
  
  drawIsoPlatform(
    graphics: Phaser.GameObjects.Graphics,
    x: number,
    y: number,
    width: number,
    height: number,
    depth: number,
    color: number
  ) {
    // Top face (diamond)
    graphics.fillStyle(color, 1);
    graphics.beginPath();
    graphics.moveTo(x, y);
    graphics.lineTo(x + width / 2, y + height / 2);
    graphics.lineTo(x, y + height);
    graphics.lineTo(x - width / 2, y + height / 2);
    graphics.closePath();
    graphics.fillPath();

    // Left side (darker)
    const leftColor = Phaser.Display.Color.IntegerToColor(color);
    leftColor.darken(30);
    graphics.fillStyle(leftColor.color, 1);
    graphics.beginPath();
    graphics.moveTo(x - width / 2, y + height / 2);
    graphics.lineTo(x, y + height);
    graphics.lineTo(x, y + height + depth);
    graphics.lineTo(x - width / 2, y + height / 2 + depth);
    graphics.closePath();
    graphics.fillPath();

    // Right side (medium)
    const rightColor = Phaser.Display.Color.IntegerToColor(color);
    rightColor.darken(15);
    graphics.fillStyle(rightColor.color, 1);
    graphics.beginPath();
    graphics.moveTo(x, y + height);
    graphics.lineTo(x + width / 2, y + height / 2);
    graphics.lineTo(x + width / 2, y + height / 2 + depth);
    graphics.lineTo(x, y + height + depth);
    graphics.closePath();
    graphics.fillPath();
  }

  createNFTAnimations() {
    // All XXL sheets: 256x256, 64x64 frames, 4x4 grid
    // Row 0 (frames 0-3): south | Row 1 (frames 4-7): north | Row 2 (frames 8-11): west
    // East = west + flipX
    const dirs = ['south', 'north', 'west'];

    for (const charId of CHARACTER_POOL) {
      dirs.forEach((dir, rowIdx) => {
        const base = rowIdx * 4;
        this.anims.create({
          key: `${charId}-walk-${dir}`,
          frames: [
            { key: charId, frame: base },
            { key: charId, frame: base + 1 },
            { key: charId, frame: base + 2 },
            { key: charId, frame: base + 3 },
            { key: charId, frame: base + 2 },
            { key: charId, frame: base + 1 },
          ],
          frameRate: 7,
          repeat: -1
        });
        this.anims.create({
          key: `${charId}-idle-${dir}`,
          frames: [{ key: charId, frame: base + 1 }],
          frameRate: 1
        });
      });
    }

    console.log(`✅ Created animations for ${CHARACTER_POOL.length} characters`);
  }

  createPlayer() {
    console.log(`🎨 Creating player with ${LOCAL_CHARACTER}`);

    // Ground shadow (renders below player)
    this.playerShadow = this.add.ellipse(640, 364, 40, 14, 0x000000, 0.3);
    this.playerShadow.setDepth(-1);

    this.player = this.physics.add.sprite(640, 360, LOCAL_CHARACTER, 1);
    this.player.setScale(2.0);

    // Anchor at feet
    this.player.setOrigin(0.5, 0.9);

    // Initialize physics with acceleration/drag
    this.movementController.initPhysics(this.player);

    // Set isometric data - start at ground level (elevation 0)
    this.depthManager.setIsoData(this.player, 0, 64);

    // Physics - Don't restrict to world bounds (map is larger than initial bounds)
    this.player.setCollideWorldBounds(false);
  }

  createNPCs(count: number) {
    // 🎨 Create NPCs using diverse NFT characters
    console.log(`🎨 Spawning ${count} diverse NFT characters...`);

    for (let i = 0; i < count; i++) {
      const x = Phaser.Math.Between(400, 880);  // Center viewport range
      const y = Phaser.Math.Between(200, 520);

      // Use hero_orange for all NPCs (NFT sheets have incompatible frame sizes)
      const charId = LOCAL_CHARACTER;
      const npc = this.physics.add.sprite(x, y, charId, 0);  // frame 0 = south idle

      // Random elevation (0-3)
      const elevation = Phaser.Math.Between(0, 3);

      npc.setAlpha(0.9);
      npc.setScale(2.0);
      npc.setOrigin(0.5, 0.9);

      // Set elevation data
      this.depthManager.setIsoData(npc, elevation, 64);

      // Random slow movement (bouncing AI)
      const speed = 40;
      npc.setVelocity(
        Phaser.Math.Between(-speed, speed),
        Phaser.Math.Between(-speed, speed)
      );

      npc.setCollideWorldBounds(true);
      npc.setBounce(1, 1);

      this.npcs.push(npc);
    }

    console.log(`✅ Spawned ${this.npcs.length} diverse characters!`);
  }

  setupCamera() {
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
    this.cameras.main.setZoom(1);  // Reduced zoom to see more of the world
    this.cameras.main.setBounds(-1000, -1000, 4000, 3000);
  }

  setupInput() {
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.wasd = {
      w: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      a: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      s: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      d: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
      q: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.Q),
      e: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.E),
    };
  }

  override update() {
    // Get input from keyboard or mobile
    let input;
    if (this.isMobile && this.mobileInput) {
      input = this.mobileInput.getInput();
    } else {
      input = {
        up: this.cursors.up.isDown || this.wasd.w.isDown,
        down: this.cursors.down.isDown || this.wasd.s.isDown,
        left: this.cursors.left.isDown || this.wasd.a.isDown,
        right: this.cursors.right.isDown || this.wasd.d.isDown,
      };
    }

    // Update player movement with input
    this.movementController.updateWithInput(this.player, input);

    // Update logical Y position after movement (for collision detection)
    // This must happen BEFORE elevation detection to avoid feedback loop
    if (this.player.body!.velocity.x !== 0 || this.player.body!.velocity.y !== 0) {
      const currentLogicalY = this.player.getData('logicalY') as number;
      const currentIsoData = this.player.getData('iso');
      const currentElevation = currentIsoData?.elevation || 0;

      // Calculate what logicalY should be based on current visual Y
      // Must match MapGenerator.toIso() offset: elevation * 20px
      const newLogicalY = this.player.y + (currentElevation * 20);
      this.player.setData('logicalY', newLogicalY);
    }

    // AUTOMATIC ELEVATION DETECTION (FFT-style)
    // Use logical Y position for detection to avoid feedback loop
    const logicalY = this.player.getData('logicalY') || this.player.y;
    const targetElevation = this.platformElevation.getElevationAt(this.player.x, logicalY);
    const isoData = this.player.getData('iso');
    const currentElevation = isoData?.elevation || 0;

    // Auto-adjust elevation if player walked onto different level
    if (targetElevation !== currentElevation) {
      this.depthManager.setIsoData(this.player, targetElevation, 48);
      console.log(`🎮 Auto Elevation: ${currentElevation} → ${targetElevation}`);
    }

    // Increment walk tick for bob effect
    const moving = input.up || input.down || input.left || input.right;
    if (moving) this.walkTick++;
    else this.walkTick = 0;

    // Update player animation based on INPUT (not velocity — velocity is isometrically skewed)
    this.updateNFTAnimationFromInput(this.player, input, this.walkTick);

    // Update NPC animations too
    this.npcs.forEach(npc => {
      this.updateNFTAnimation(npc, npc.body!.velocity);
    });

    // Update depth sorting (throttled to every 2 frames for performance)
    if (this.frameCounter % 2 === 0) {
      this.depthManager.updateDepths(this);
    }

    // Send input to server (with current elevation and actual position)
    const updatedIsoData = this.player.getData('iso');
    this.multiplayerManager.sendInput(
      input,
      updatedIsoData?.elevation || 0,
      { x: this.player.x, y: this.player.getData('logicalY') || this.player.y } // Send LOGICAL Y
    );

    // Update remote players
    this.multiplayerManager.update();

    // Update spatial audio (throttled to 10 FPS for performance)
    this.frameCounter++;
    if (this.frameCounter % 6 === 0) {
      this.updateSpatialAudio();
    }

    this.debugText.setText([
      `anim: ${this.player.anims.currentAnim?.key ?? 'none'}`,
      `frame: ${this.player.anims.currentFrame?.index ?? '?'} / ${this.player.anims.currentAnim?.frames.length ?? '?'}`,
      `playing: ${this.player.anims.isPlaying}`,
      `flipX: ${this.player.flipX}`
    ].join('\n'));
  }

  updateSpatialAudio() {
    // Get local player position and elevation
    const localIsoData = this.player.getData('iso');
    const localPos = {
      playerId: this.voiceManager.getLocalPlayerId() || 'local',
      x: this.player.x,
      y: this.player.y,
      elevation: localIsoData?.elevation || 0
    };

    // Get remote player positions from multiplayer manager
    const remotePlayers = this.multiplayerManager.getRemotePlayers().map(({ id, sprite }) => {
      const isoData = sprite.getData('iso');
      return {
        playerId: id,
        x: sprite.x,
        y: sprite.y,
        elevation: isoData?.elevation || 0
      };
    });

    // Update voice manager with positions
    this.voiceManager.updateSpatialAudio(localPos, remotePlayers);
  }

  updateNFTAnimationFromInput(sprite: Phaser.Physics.Arcade.Sprite, input: { up: boolean, down: boolean, left: boolean, right: boolean }, walkTick: number = 0) {
    const charId = sprite.texture.key;
    if (!CHARACTER_POOL.includes(charId)) return;

    const moving = input.up || input.down || input.left || input.right;
    const IDLE_GRACE_FRAMES = 4;
    let graceCounter = sprite.getData('idleGrace') || 0;

    let targetKey: string;
    let flipX = false;

    if (moving) {
      graceCounter = 0;
      sprite.setData('idleGrace', 0);

      // Isometric direction mapping: keys align to grid edges
      let direction: string;
      if (input.right && input.down) direction = 'south';  // SE+SW → screen-down
      else if (input.left && input.up) direction = 'north'; // NW+NE → screen-up
      else if (input.right && input.up) direction = 'east';  // SE+NE → screen-right
      else if (input.left && input.down) direction = 'west'; // NW+SW → screen-left
      else if (input.right) direction = 'south';             // SE grid edge
      else if (input.left) direction = 'north';              // NW grid edge
      else if (input.up) direction = 'east';                 // NE grid edge
      else direction = 'west';                               // SW grid edge

      const animDir = direction === 'east' ? 'west' : direction;
      flipX = direction === 'east';
      targetKey = `${charId}-walk-${animDir}`;

      // Premium walk: subtle Y-only hop synced to step cadence
      // 6-frame ping-pong at 7fps = ~0.86s cycle, each step = 0.43s
      // At 60fps game loop: ~26 frames per step
      // Use smooth step curve: quick lift, hang, soft land
      const stepPhase = (walkTick % 26) / 26; // 0→1 per step
      const lift = Math.sin(stepPhase * Math.PI); // smooth arc
      const hopPx = lift * 0.025; // ~3px hop at scale 2.0 (64*2*0.025 = 3.2px)

      sprite.setOrigin(0.5, 0.9 - hopPx);
      sprite.setScale(2.0, 2.0);
      sprite.setRotation(0);

      // Update shadow if exists
      if (this.playerShadow) {
        this.playerShadow.setPosition(sprite.x, sprite.y + 4);
        this.playerShadow.setScale(1.0 - lift * 0.15, 1.0 - lift * 0.08);
        this.playerShadow.setAlpha(0.3 - lift * 0.1);
      }
    } else {
      graceCounter++;
      sprite.setData('idleGrace', graceCounter);

      // Settle: smooth return to neutral over 4 frames
      const SETTLE_FRAMES = 4;
      if (graceCounter <= SETTLE_FRAMES) {
        const t = graceCounter / SETTLE_FRAMES;
        const currentOriginY = sprite.originY;
        const targetOriginY = 0.9;
        sprite.setOrigin(0.5, currentOriginY + (targetOriginY - currentOriginY) * t);
        sprite.setScale(2.0, 2.0);
        sprite.setRotation(0);

        if (graceCounter < IDLE_GRACE_FRAMES) {
          const prevKey = sprite.getData('lastAnimKey') || '';
          if (prevKey.includes('-walk-')) return;
        }
      } else {
        sprite.setOrigin(0.5, 0.9);
        sprite.setScale(2.0, 2.0);
        sprite.setRotation(0);
      }

      // Update shadow to resting state
      if (this.playerShadow) {
        this.playerShadow.setPosition(sprite.x, sprite.y + 4);
        this.playerShadow.setScale(1.0, 1.0);
        this.playerShadow.setAlpha(0.3);
      }

      const lastKey: string = sprite.getData('lastAnimKey') || `${charId}-idle-south`;
      const idleDir = lastKey.includes('-north') ? 'north'
        : lastKey.includes('-west') ? 'west'
        : 'south';
      targetKey = `${charId}-idle-${idleDir}`;
      flipX = sprite.getData('lastFlipX') || false;
    }

    sprite.setFlipX(flipX);

    const prevKey = sprite.getData('lastAnimKey');
    if (prevKey !== targetKey) {
      sprite.setData('lastAnimKey', targetKey);
      sprite.setData('lastFlipX', flipX);
      sprite.play(targetKey);
    }
  }

  updateNFTAnimation(sprite: Phaser.Physics.Arcade.Sprite, velocity: { x: number, y: number }) {
    const isMoving = velocity.x !== 0 || velocity.y !== 0;
    const charId = sprite.texture.key;
    if (!CHARACTER_POOL.includes(charId)) return;

    if (isMoving) {
      const horizDominant = Math.abs(velocity.x) > Math.abs(velocity.y);
      let direction: string;
      if (horizDominant) direction = velocity.x > 0 ? 'east' : 'west';
      else direction = velocity.y > 0 ? 'south' : 'north';

      const animDir = direction === 'east' ? 'west' : direction;
      sprite.setFlipX(direction === 'east');
      sprite.play(`${charId}-walk-${animDir}`, true);
    } else {
      const frameIdx = parseInt(String(sprite.frame.name), 10);
      let direction = 'south';
      if (frameIdx >= 4 && frameIdx <= 7) direction = 'north';
      else if (frameIdx >= 8) direction = 'west';

      sprite.play(`${charId}-idle-${direction}`, true);
    }
  }
}
