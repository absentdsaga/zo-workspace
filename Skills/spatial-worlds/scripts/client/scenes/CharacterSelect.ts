import Phaser from 'phaser';

interface CharacterData {
  id: string;
  name: string;
  spriteKey: string;
}

export class CharacterSelect extends Phaser.Scene {
  private characters: CharacterData[] = [];
  private selectedCharacter: string | null = null;
  private characterSprites: Phaser.GameObjects.Sprite[] = [];

  constructor() {
    super('CharacterSelect');
  }

  preload() {
    console.log('🎨 Loading NFT character sprites for selection...');

    // Load all 24 NFT character sprites
    const sets = ['set1', 'set2', 'set3', 'set4'];
    const chars = [1, 2, 3, 4, 5, 6];

    sets.forEach(set => {
      chars.forEach(char => {
        const key = `${set}-char${char}`;
        const path = `assets/sprites/nft-characters/${key}/${key}-sheet.png?t=${Date.now()}`;

        this.load.spritesheet(key, path, {
          frameWidth: 32,
          frameHeight: 48
        });

        this.characters.push({
          id: key,
          name: `${set.toUpperCase()} #${char}`,
          spriteKey: key
        });
      });
    });

    console.log(`✅ Loading ${this.characters.length} NFT characters`);
  }

  create() {
    const { width, height } = this.cameras.main;

    // Dark background
    this.add.rectangle(0, 0, width, height, 0x0a0a0a).setOrigin(0);

    // Title
    this.add.text(width / 2, 60, 'Choose Your Character', {
      fontSize: '48px',
      color: '#ffffff',
      fontFamily: 'Arial',
      stroke: '#000000',
      strokeThickness: 4
    }).setOrigin(0.5);

    // Subtitle
    this.add.text(width / 2, 120, 'Select your NFT character sprite', {
      fontSize: '20px',
      color: '#aaaaaa',
      fontFamily: 'Arial'
    }).setOrigin(0.5);

    // Create grid of character sprites (4 rows × 6 cols)
    const gridStartX = 200;
    const gridStartY = 200;
    const cellWidth = 140;
    const cellHeight = 180;
    const cols = 6;

    this.characters.forEach((character, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const x = gridStartX + col * cellWidth;
      const y = gridStartY + row * cellHeight;

      // Create container for each character
      const container = this.add.container(x, y);

      // Background card
      const card = this.add.rectangle(0, 0, 120, 160, 0x1a1a1a);
      card.setStrokeStyle(2, 0x333333);
      card.setInteractive();
      container.add(card);

      // Character sprite (idle pose, facing down)
      try {
        const sprite = this.add.sprite(0, -20, character.spriteKey, 12); // Frame 12 = down idle
        sprite.setScale(3);
        container.add(sprite);
        this.characterSprites.push(sprite);

        // Create walk animation for preview
        if (!this.anims.exists(`${character.id}-preview`)) {
          this.anims.create({
            key: `${character.id}-preview`,
            frames: this.anims.generateFrameNumbers(character.spriteKey, { start: 12, end: 15 }),
            frameRate: 8,
            repeat: -1
          });
        }
      } catch (error) {
        console.error(`Failed to load sprite for ${character.id}:`, error);
        // Fallback: show colored rectangle
        const fallback = this.add.rectangle(0, -20, 32, 48, 0xff0000);
        container.add(fallback);
      }

      // Character name label
      const nameText = this.add.text(0, 60, character.name, {
        fontSize: '12px',
        color: '#ffffff',
        fontFamily: 'Arial',
        backgroundColor: '#000000',
        padding: { x: 4, y: 2 }
      }).setOrigin(0.5);
      container.add(nameText);

      // Hover effect
      card.on('pointerover', () => {
        card.setStrokeStyle(3, 0x4a9eff);
        card.setFillStyle(0x2a2a2a);
        // Play animation on hover
        const spriteIndex = index;
        if (this.characterSprites[spriteIndex]) {
          this.characterSprites[spriteIndex].play(`${character.id}-preview`);
        }
      });

      card.on('pointerout', () => {
        if (this.selectedCharacter !== character.id) {
          card.setStrokeStyle(2, 0x333333);
          card.setFillStyle(0x1a1a1a);
          // Stop animation
          const spriteIndex = index;
          if (this.characterSprites[spriteIndex]) {
            this.characterSprites[spriteIndex].stop();
            this.characterSprites[spriteIndex].setFrame(12);
          }
        }
      });

      // Click to select
      card.on('pointerdown', () => {
        this.selectCharacter(character.id, card, index);
      });

      // Store reference
      card.setData('characterId', character.id);
    });

    // Start button (disabled until character selected)
    const startButton = this.add.rectangle(width / 2, height - 80, 200, 60, 0x333333);
    startButton.setStrokeStyle(3, 0x555555);
    startButton.setInteractive();
    startButton.setData('enabled', false);

    const startText = this.add.text(width / 2, height - 80, 'START GAME', {
      fontSize: '24px',
      color: '#666666',
      fontFamily: 'Arial',
      fontStyle: 'bold'
    }).setOrigin(0.5);

    startButton.on('pointerover', () => {
      if (startButton.getData('enabled')) {
        startButton.setFillStyle(0x5aafff);
      }
    });

    startButton.on('pointerout', () => {
      if (startButton.getData('enabled')) {
        startButton.setFillStyle(0x4a9eff);
      }
    });

    startButton.on('pointerdown', () => {
      if (startButton.getData('enabled') && this.selectedCharacter) {
        this.startGame(this.selectedCharacter);
      }
    });

    // Store button references
    this.registry.set('startButton', startButton);
    this.registry.set('startText', startText);
  }

  private selectCharacter(characterId: string, card: Phaser.GameObjects.Rectangle, index: number) {
    // Clear previous selection
    this.children.list.forEach(child => {
      if (child instanceof Phaser.GameObjects.Rectangle && child.getData('characterId')) {
        if (child.getData('characterId') === this.selectedCharacter) {
          child.setStrokeStyle(2, 0x333333);
          child.setFillStyle(0x1a1a1a);
        }
      }
    });

    // Set new selection
    this.selectedCharacter = characterId;
    card.setStrokeStyle(4, 0x00ff00);
    card.setFillStyle(0x2a4a2a);

    // Keep animation playing
    if (this.characterSprites[index]) {
      this.characterSprites[index].play(`${characterId}-preview`);
    }

    // Enable start button
    const startButton = this.registry.get('startButton') as Phaser.GameObjects.Rectangle;
    const startText = this.registry.get('startText') as Phaser.GameObjects.Text;

    if (startButton && startText) {
      startButton.setData('enabled', true);
      startButton.setFillStyle(0x4a9eff);
      startButton.setStrokeStyle(3, 0x6ac0ff);
      startText.setColor('#ffffff');
    }

    console.log(`✅ Selected character: ${characterId}`);
  }

  private startGame(characterId: string) {
    console.log(`🎮 Starting game with character: ${characterId}`);

    // Store selected character in registry
    this.registry.set('selectedCharacter', characterId);

    // Transition to game scene
    this.scene.start('IsoGameScene');
  }
}
