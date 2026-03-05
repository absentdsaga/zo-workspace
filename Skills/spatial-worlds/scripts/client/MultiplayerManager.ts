import { DepthManager } from './systems/DepthManager';

interface PlayerState {
  id: string;
  charId?: string;
  x: number;
  y: number;
  elevation: number;
  direction: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  animState: 'idle' | 'walk';
  timestamp: number;
}

interface RemotePlayerData {
  sprite: Phaser.GameObjects.Sprite;
  shadow: Phaser.GameObjects.Ellipse;
  charId: string;
  targetX: number;
  targetY: number;
  lastUpdate: number;
}

export class MultiplayerManager {
  private ws: WebSocket | null = null;
  private playerId: string | null = null;
  private remotePlayers = new Map<string, RemotePlayerData>();
  private scene: Phaser.Scene;
  private depthManager: DepthManager;
  private localCharId: string;

  private inputBuffer: any[] = [];
  private lastSentInput = { up: false, down: false, left: false, right: false };

  constructor(scene: Phaser.Scene, localCharId: string) {
    this.scene = scene;
    this.depthManager = new DepthManager();
    this.localCharId = localCharId;
  }
  
  connect(url: string) {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('✅ Connected to multiplayer server');
      
      // Send join message with our character identity
      this.ws!.send(JSON.stringify({
        type: 'join',
        playerName: 'Player',
        charId: this.localCharId,
      }));
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'init') {
        this.playerId = data.playerId;
        console.log(`👤 You are player ${this.playerId.slice(0, 8)}`);
        
        // Spawn existing players
        data.players.forEach((player: PlayerState) => {
          if (player.id !== this.playerId) {
            this.spawnRemotePlayer(player);
          }
        });
      } else if (data.type === 'player_joined') {
        console.log(`🎉 New player joined: ${data.player.id.slice(0, 8)}`);
        if (data.player.id !== this.playerId) {
          this.spawnRemotePlayer(data.player);
        }
      } else if (data.type === 'player_left') {
        this.removeRemotePlayer(data.playerId);
      } else if (data.type === 'state') {
        data.players.forEach((player: PlayerState) => {
          if (player.id !== this.playerId) {
            this.updateRemotePlayer(player);
          }
        });
      }
    };
    
    this.ws.onclose = () => {
      console.log('❌ Disconnected from server');
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  sendInput(input: { up: boolean, down: boolean, left: boolean, right: boolean }, elevation?: number, position?: { x: number, y: number }) {
    // Send input every frame when moving, or when input changes
    const isMoving = input.up || input.down || input.left || input.right;
    const inputChanged = (
      input.up !== this.lastSentInput.up ||
      input.down !== this.lastSentInput.down ||
      input.left !== this.lastSentInput.left ||
      input.right !== this.lastSentInput.right
    );

    // Only send if moving OR if input changed (to send "stopped" state)
    if (!isMoving && !inputChanged) {
      return;
    }

    this.lastSentInput = { ...input };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'move',
        input,
        elevation,
        position, // CLIENT AUTHORITATIVE: Send actual position
        timestamp: Date.now(),
      }));
    }
  }
  
  private spawnRemotePlayer(player: PlayerState) {
    if (this.remotePlayers.has(player.id)) return;

    const charId = player.charId || 'hero_orange';

    const sprite = this.scene.add.sprite(player.x, player.y, charId, 1);
    sprite.setScale(2.0);
    sprite.setOrigin(0.5, 0.9);
    sprite.setData('iso', { elevation: player.elevation });
    sprite.setData('playerId', player.id);

    // Shadow under remote player
    const shadow = this.scene.add.ellipse(player.x, player.y + 4, 40, 14, 0x000000, 0.25);
    shadow.setDepth(-1);

    // Play idle animation
    sprite.anims.play(`${charId}-idle-south`, true);

    this.remotePlayers.set(player.id, {
      sprite,
      shadow,
      charId,
      targetX: player.x,
      targetY: player.y,
      lastUpdate: Date.now()
    });

    console.log(`👥 Remote player ${player.id.slice(0, 8)} spawned as ${charId} at (${player.x}, ${player.y})`);
  }
  
  private updateRemotePlayer(player: PlayerState) {
    let playerData = this.remotePlayers.get(player.id);

    if (!playerData) {
      this.spawnRemotePlayer(player);
      playerData = this.remotePlayers.get(player.id);
      if (!playerData) return;
    }

    const sprite = playerData.sprite;
    const charId = playerData.charId;

    // Store logical Y
    sprite.setData('logicalY', player.y);

    // Update target position
    playerData.targetX = player.x;
    playerData.targetY = player.y;

    // Set sprite position
    sprite.x = player.x;
    sprite.y = player.y;

    // Let DepthManager convert logical Y to visual Y
    this.depthManager.setIsoData(sprite, player.elevation, 48);

    // Update shadow position
    playerData.shadow.setPosition(sprite.x, sprite.y + 4);
    playerData.shadow.setDepth(sprite.depth - 1);

    // Map server direction to animation direction
    // Server sends: n, ne, e, se, s, sw, w, nw
    // Our anims: south, north, west (east = west + flipX)
    let animDir = 'south';
    let flipX = false;

    if (player.direction === 's' || player.direction === 'se' || player.direction === 'sw') {
      animDir = 'south';
    } else if (player.direction === 'n' || player.direction === 'ne' || player.direction === 'nw') {
      animDir = 'north';
    } else if (player.direction === 'w') {
      animDir = 'west';
    } else if (player.direction === 'e') {
      animDir = 'west';
      flipX = true;
    }

    sprite.setFlipX(flipX);

    if (player.animState === 'walk') {
      const key = `${charId}-walk-${animDir}`;
      if (sprite.anims.currentAnim?.key !== key) {
        sprite.anims.play(key, true);
      }
    } else {
      const key = `${charId}-idle-${animDir}`;
      if (sprite.anims.currentAnim?.key !== key) {
        sprite.anims.play(key, true);
      }
    }
  }
  
  private removeRemotePlayer(playerId: string) {
    const playerData = this.remotePlayers.get(playerId);
    if (playerData) {
      playerData.sprite.destroy();
      playerData.shadow.destroy();
      this.remotePlayers.delete(playerId);
      console.log(`👋 Remote player ${playerId.slice(0, 8)} left`);
    }
  }
  
  update() {
    this.remotePlayers.forEach((playerData, id) => {
      const sprite = playerData.sprite;
      sprite.x = playerData.targetX;

      // Update depth sorting
      const iso = sprite.getData('iso');
      const baseDepth = sprite.y + (iso?.elevation || 0) * 100;
      sprite.setDepth(baseDepth);

      // Keep shadow under sprite
      playerData.shadow.setPosition(sprite.x, sprite.y + 4);
      playerData.shadow.setDepth(baseDepth - 1);
    });
  }

  getRemotePlayers() {
    const players: Array<{ id: string, sprite: Phaser.GameObjects.Sprite }> = [];
    this.remotePlayers.forEach((playerData, id) => {
      players.push({ id, sprite: playerData.sprite });
    });
    return players;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    // Clean up remote players
    this.remotePlayers.forEach(playerData => {
      playerData.sprite.destroy();
      playerData.shadow.destroy();
    });
    this.remotePlayers.clear();
  }
}
