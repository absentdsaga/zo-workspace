import Phaser from 'phaser';

export class GameScene extends Phaser.Scene {
  player!: Phaser.Physics.Arcade.Sprite;
  cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  wasd!: {
    w: Phaser.Input.Keyboard.Key;
    a: Phaser.Input.Keyboard.Key;
    s: Phaser.Input.Keyboard.Key;
    d: Phaser.Input.Keyboard.Key;
  };
  tilemap!: Phaser.Tilemaps.Tilemap;
  npcs: Phaser.Physics.Arcade.Sprite[] = [];

  constructor() {
    super({ key: 'GameScene' });
  }

  create() {
    // Create procedural tilemap (will replace with Tiled JSON)
    this.createProceduralWorld();

    // Create player
    this.createPlayer();

    // Create 1000 NPCs for performance testing
    this.createNPCs(1000);

    // Setup camera
    this.setupCamera();

    // Setup input
    this.setupInput();
  }

  createProceduralWorld() {
    const mapWidth = 100;
    const mapHeight = 100;
    const tileSize = 32;

    // Create tilemap
    this.tilemap = this.make.tilemap({
      tileWidth: tileSize,
      tileHeight: tileSize,
      width: mapWidth,
      height: mapHeight,
    });

    // Add tilesets
    const grassTile = this.tilemap.addTilesetImage('grass', 'grass', tileSize, tileSize);
    const stoneTile = this.tilemap.addTilesetImage('stone', 'stone', tileSize, tileSize);
    const waterTile = this.tilemap.addTilesetImage('water', 'water', tileSize, tileSize);
    const wallTile = this.tilemap.addTilesetImage('wall', 'wall', tileSize, tileSize);

    // Create ground layer
    const groundLayer = this.tilemap.createBlankLayer('ground', [grassTile!, stoneTile!, waterTile!])!;
    
    // Fill with procedural terrain (simple noise-based)
    for (let y = 0; y < mapHeight; y++) {
      for (let x = 0; x < mapWidth; x++) {
        const noise = this.noise(x * 0.1, y * 0.1);
        
        if (noise < 0.3) {
          groundLayer.putTileAt(waterTile!.firstgid, x, y);
        } else if (noise < 0.6) {
          groundLayer.putTileAt(grassTile!.firstgid, x, y);
        } else {
          groundLayer.putTileAt(stoneTile!.firstgid, x, y);
        }
      }
    }

    // Create walls layer (border walls)
    const wallsLayer = this.tilemap.createBlankLayer('walls', wallTile!)!;
    
    // Add border walls
    for (let x = 0; x < mapWidth; x++) {
      wallsLayer.putTileAt(wallTile!.firstgid, x, 0);
      wallsLayer.putTileAt(wallTile!.firstgid, x, mapHeight - 1);
    }
    for (let y = 0; y < mapHeight; y++) {
      wallsLayer.putTileAt(wallTile!.firstgid, 0, y);
      wallsLayer.putTileAt(wallTile!.firstgid, mapWidth - 1, y);
    }

    // Add some random interior walls
    for (let i = 0; i < 50; i++) {
      const x = Phaser.Math.Between(10, mapWidth - 10);
      const y = Phaser.Math.Between(10, mapHeight - 10);
      wallsLayer.putTileAt(wallTile!.firstgid, x, y);
    }

    // Set collision on walls
    wallsLayer.setCollisionByExclusion([-1]);

    // Enable collision with physics
    this.physics.world.setBounds(0, 0, mapWidth * tileSize, mapHeight * tileSize);
  }

  // Simple Perlin-like noise function
  noise(x: number, y: number): number {
    const sin = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
    return sin - Math.floor(sin);
  }

  createPlayer() {
    // Spawn in center of map
    const spawnX = this.tilemap.widthInPixels / 2;
    const spawnY = this.tilemap.heightInPixels / 2;

    this.player = this.physics.add.sprite(spawnX, spawnY, 'player');
    this.player.setCollideWorldBounds(true);
    this.player.setScale(1);

    // Add collision with walls
    const wallsLayer = this.tilemap.getLayer('walls')!.tilemapLayer;
    this.physics.add.collider(this.player, wallsLayer);
  }

  createNPCs(count: number) {
    const wallsLayer = this.tilemap.getLayer('walls')!.tilemapLayer;

    for (let i = 0; i < count; i++) {
      // Random spawn position (avoid edges)
      const x = Phaser.Math.Between(100, this.tilemap.widthInPixels - 100);
      const y = Phaser.Math.Between(100, this.tilemap.heightInPixels - 100);

      const npc = this.physics.add.sprite(x, y, 'player');
      npc.setTint(Phaser.Display.Color.RandomRGB().color);
      npc.setAlpha(0.6);
      npc.setScale(0.8);

      // Random velocity
      const speed = 50;
      npc.setVelocity(
        Phaser.Math.Between(-speed, speed),
        Phaser.Math.Between(-speed, speed)
      );

      // Collide with walls and world bounds
      npc.setCollideWorldBounds(true);
      npc.setBounce(1, 1); // Bounce off walls
      this.physics.add.collider(npc, wallsLayer);

      this.npcs.push(npc);
    }
  }

  setupCamera() {
    // Camera follows player
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
    this.cameras.main.setZoom(2); // Zoom in for pixel art feel

    // Set camera bounds
    this.cameras.main.setBounds(
      0, 0,
      this.tilemap.widthInPixels,
      this.tilemap.heightInPixels
    );
  }

  setupInput() {
    // Arrow keys
    this.cursors = this.input.keyboard!.createCursorKeys();

    // WASD
    this.wasd = {
      w: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      a: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      s: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      d: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };
  }

  override update() {
    this.handlePlayerMovement();
    this.cullSprites();
  }

  handlePlayerMovement() {
    const speed = 200;
    let velocityX = 0;
    let velocityY = 0;

    // Check WASD and arrow keys
    if (this.cursors.left.isDown || this.wasd.a.isDown) velocityX = -speed;
    if (this.cursors.right.isDown || this.wasd.d.isDown) velocityX = speed;
    if (this.cursors.up.isDown || this.wasd.w.isDown) velocityY = -speed;
    if (this.cursors.down.isDown || this.wasd.s.isDown) velocityY = speed;

    // Normalize diagonal movement
    if (velocityX !== 0 && velocityY !== 0) {
      velocityX *= 0.707;
      velocityY *= 0.707;
    }

    this.player.setVelocity(velocityX, velocityY);
  }

  cullSprites() {
    // Only render NPCs visible in camera viewport
    const camera = this.cameras.main;
    const visibleBounds = new Phaser.Geom.Rectangle(
      camera.worldView.x - 100,
      camera.worldView.y - 100,
      camera.worldView.width + 200,
      camera.worldView.height + 200
    );

    this.npcs.forEach(npc => {
      const inView = Phaser.Geom.Rectangle.Contains(visibleBounds, npc.x, npc.y);
      npc.setVisible(inView);
      npc.setActive(inView);
    });
  }
}
