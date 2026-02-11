import { DepthManager } from './systems/DepthManager';

interface PlayerState {
  id: string;
  x: number;
  y: number;
  elevation: number;
  direction: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  animState: 'idle' | 'walk';
  timestamp: number;
}

interface RemotePlayerData {
  sprite: Phaser.GameObjects.Sprite;
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

  private inputBuffer: any[] = [];
  private lastSentInput = { up: false, down: false, left: false, right: false };
  
  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.depthManager = new DepthManager();
  }
  
  connect(url: string) {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('✅ Connected to multiplayer server');
      
      // Send join message
      this.ws!.send(JSON.stringify({
        type: 'join',
        playerName: 'Player',
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

    // Create sprite for remote player using warrior sprite (same as local player)
    const sprite = this.scene.add.sprite(player.x, player.y, 'warrior-south-0');
    sprite.setScale(1.5);
    sprite.setOrigin(0.5, 0.85);
    sprite.setData('iso', { elevation: player.elevation });
    sprite.setData('playerId', player.id);

    // Tint to distinguish from local player (subtle blue tint)
    sprite.setTint(0xaaddff);

    // Play walk animation
    sprite.anims.play(`walk-${player.direction}`, true);

    this.remotePlayers.set(player.id, {
      sprite,
      targetX: player.x,
      targetY: player.y,
      lastUpdate: Date.now()
    });

    console.log(`👥 Remote player ${player.id.slice(0, 8)} spawned at (${player.x}, ${player.y})`);
  }
  
  private updateRemotePlayer(player: PlayerState) {
    let playerData = this.remotePlayers.get(player.id);

    if (!playerData) {
      this.spawnRemotePlayer(player);
      playerData = this.remotePlayers.get(player.id);
      if (!playerData) return;
    }

    const sprite = playerData.sprite;

    // ALWAYS log for debugging
    console.log(`[UPDATE] Player ${player.id.slice(0,4)}: recv(${Math.round(player.x)}, ${Math.round(player.y)}, elev=${player.elevation})`);

    // Store logical Y
    sprite.setData('logicalY', player.y);
    
    // Update target position
    playerData.targetX = player.x;
    playerData.targetY = player.y;
    
    // Set sprite position before calling setIsoData
    console.log(`[BEFORE] sprite at (${Math.round(sprite.x)}, ${Math.round(sprite.y)})`);
    sprite.x = player.x;
    sprite.y = player.y;
    console.log(`[SET] sprite.x=${Math.round(player.x)}, sprite.y=${Math.round(player.y)} (logical)`);
    
    // Let DepthManager convert logical Y to visual Y
    this.depthManager.setIsoData(sprite, player.elevation, 48);
    console.log(`[AFTER] sprite at (${Math.round(sprite.x)}, ${Math.round(sprite.y)}) (visual)`);

    // Update animation
    if (player.animState === 'walk') {
      sprite.anims.play(`walk-${player.direction}`, true);
    } else {
      sprite.anims.stop();
      sprite.setFrame(0);
    }
  }
  
  private removeRemotePlayer(playerId: string) {
    const playerData = this.remotePlayers.get(playerId);
    if (playerData) {
      playerData.sprite.destroy();
      this.remotePlayers.delete(playerId);
      console.log(`👋 Remote player ${playerId.slice(0, 8)} left`);
    }
  }
  
  update() {
    // Update sprite positions and depth sorting
    this.remotePlayers.forEach((playerData, id) => {
      const sprite = playerData.sprite;
      sprite.x = playerData.targetX;  // Update X position every frame
      // Don't touch sprite.y - it's managed by setIsoData() in updateRemotePlayer()
      
      // Update depth sorting
      const iso = sprite.getData('iso');
      const baseDepth = sprite.y + (iso?.elevation || 0) * 100;
      sprite.setDepth(baseDepth);
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
    this.remotePlayers.forEach(playerData => playerData.sprite.destroy());
    this.remotePlayers.clear();
  }
}
