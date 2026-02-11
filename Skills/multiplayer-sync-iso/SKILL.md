---
name: multiplayer-sync-iso
description: Real-time multiplayer synchronization optimized for isometric tactical worlds. Handles 8-direction movement, elevation changes, and efficient state broadcasting for 100+ concurrent players.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: multiplayer
  version: 1.0.0
---

# Multiplayer Sync (Isometric)

Optimized WebSocket protocol and client-side prediction for isometric multiplayer worlds with elevation, 8-direction movement, and proximity voice zones.

## Challenges Unique to Isometric

1. **More movement data**: 8 directions vs 4
2. **Elevation sync**: Vertical position matters for rendering
3. **Complex collision**: Multi-level pathfinding
4. **Depth sorting**: All clients must sort identically
5. **Voice zones**: Elevation affects audio proximity

## Network Protocol

### Player State Packet
```typescript
interface PlayerState {
  id: string;
  x: number;          // World X
  y: number;          // World Y
  elevation: number;  // 0, 1, 2, 3 (level)
  direction: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  animState: 'idle' | 'walk' | 'sit';
  timestamp: number;  // Server time
}
```

### Movement Command (Client → Server)
```typescript
interface MoveCommand {
  type: 'move';
  input: {
    up: boolean;
    down: boolean;
    left: boolean;
    right: boolean;
  };
  timestamp: number;  // Client time for lag compensation
}
```

### State Update (Server → Clients)
```typescript
interface StateUpdate {
  type: 'state';
  players: PlayerState[];
  timestamp: number;  // Server authoritative time
}
```

## Client-Side Prediction

### Prediction System
```typescript
class IsoPredictionSystem {
  private inputBuffer: MoveCommand[] = [];
  private lastServerState?: PlayerState;
  private localPrediction?: PlayerState;
  
  // Predict movement immediately
  predictMove(input: MoveCommand, sprite: Phaser.GameObjects.Sprite) {
    // Apply input locally
    const velocity = this.inputToVelocity(input.input);
    sprite.setVelocity(velocity.x, velocity.y);
    
    // Store for reconciliation
    this.inputBuffer.push(input);
    this.localPrediction = this.getCurrentState(sprite);
  }
  
  // When server state arrives, check prediction
  reconcile(serverState: PlayerState, sprite: Phaser.GameObjects.Sprite) {
    // Find matching timestamp in buffer
    const serverTime = serverState.timestamp;
    
    // Remove acknowledged inputs
    this.inputBuffer = this.inputBuffer.filter(
      cmd => cmd.timestamp > serverTime
    );
    
    // Check if prediction was correct
    const error = {
      x: Math.abs(serverState.x - this.localPrediction!.x),
      y: Math.abs(serverState.y - this.localPrediction!.y),
      elevation: Math.abs(serverState.elevation - this.localPrediction!.elevation),
    };
    
    // If error > threshold, snap to server state
    if (error.x > 5 || error.y > 5 || error.elevation > 0) {
      sprite.setPosition(serverState.x, serverState.y);
      sprite.setData('iso', { elevation: serverState.elevation });
    }
    
    // Re-apply unacknowledged inputs
    this.inputBuffer.forEach(cmd => {
      const velocity = this.inputToVelocity(cmd.input);
      sprite.setVelocity(velocity.x, velocity.y);
    });
  }
  
  inputToVelocity(input: any): { x: number, y: number } {
    let dirX = 0, dirY = 0;
    if (input.up) dirY -= 1;
    if (input.down) dirY += 1;
    if (input.left) dirX -= 1;
    if (input.right) dirX += 1;
    
    // Isometric velocity (diagonal compensation)
    const speed = 150;
    const isoX = (dirX - dirY) * 0.707 * speed;
    const isoY = (dirX + dirY) * 0.5 * 0.707 * speed;
    
    return { x: isoX, y: isoY };
  }
}
```

## Server-Side Authority

### Authoritative Server
```typescript
import { ServerWebSocket } from 'bun';

interface GameServer {
  players: Map<string, PlayerState>;
  world: IsoWorld;
  
  handleMove(ws: ServerWebSocket, cmd: MoveCommand) {
    const player = this.players.get(ws.data.playerId);
    if (!player) return;
    
    // Validate movement (anti-cheat)
    const newPos = this.calculatePosition(player, cmd);
    
    // Check collision server-side
    const canMove = this.world.isWalkable(
      newPos.x,
      newPos.y,
      player.elevation
    );
    
    if (!canMove) {
      // Reject movement, send correction
      this.sendState(ws, player);
      return;
    }
    
    // Check elevation change (stairs)
    const newElevation = this.world.getElevationAt(newPos.x, newPos.y);
    if (Math.abs(newElevation - player.elevation) > 1) {
      // Can't jump more than 1 level
      return;
    }
    
    // Apply movement
    player.x = newPos.x;
    player.y = newPos.y;
    player.elevation = newElevation;
    player.direction = this.getDirection(cmd.input);
    player.timestamp = Date.now();
    
    // Broadcast to nearby players only (optimization)
    this.broadcastToProximity(player);
  }
  
  broadcastToProximity(player: PlayerState) {
    // Find players within voice range (accounting for elevation)
    const nearbyPlayers = Array.from(this.players.values()).filter(p => {
      if (p.id === player.id) return false;
      
      // Calculate 3D distance (x, y, elevation)
      const dx = p.x - player.x;
      const dy = p.y - player.y;
      const dz = (p.elevation - player.elevation) * 32; // Elevation weight
      
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
      return distance < 500; // Voice range
    });
    
    // Send state update to nearby players
    nearbyPlayers.forEach(p => {
      const ws = this.getWebSocket(p.id);
      if (ws) {
        ws.send(JSON.stringify({
          type: 'state',
          players: [player],
          timestamp: Date.now(),
        }));
      }
    });
  }
}
```

## Interpolation (Remote Players)

### Smooth Remote Movement
```typescript
class RemotePlayerInterpolation {
  private stateBuffer: PlayerState[] = [];
  private renderTime = 100; // 100ms behind server (interpolation delay)
  
  addState(state: PlayerState) {
    // Keep last 1 second of states
    this.stateBuffer.push(state);
    this.stateBuffer = this.stateBuffer.filter(
      s => s.timestamp > Date.now() - 1000
    );
  }
  
  update(sprite: Phaser.GameObjects.Sprite) {
    const now = Date.now() - this.renderTime;
    
    // Find two states to interpolate between
    const states = this.stateBuffer;
    let before: PlayerState | null = null;
    let after: PlayerState | null = null;
    
    for (let i = 0; i < states.length - 1; i++) {
      if (states[i].timestamp <= now && states[i + 1].timestamp >= now) {
        before = states[i];
        after = states[i + 1];
        break;
      }
    }
    
    if (!before || !after) {
      // No interpolation data, use latest
      const latest = states[states.length - 1];
      if (latest) {
        sprite.setPosition(latest.x, latest.y);
        sprite.setData('iso', { elevation: latest.elevation });
      }
      return;
    }
    
    // Interpolate position
    const t = (now - before.timestamp) / (after.timestamp - before.timestamp);
    const x = Phaser.Math.Linear(before.x, after.x, t);
    const y = Phaser.Math.Linear(before.y, after.y, t);
    
    sprite.setPosition(x, y);
    
    // Elevation change is discrete (snap)
    sprite.setData('iso', { elevation: after.elevation });
    
    // Play animation
    sprite.anims.play(`walk-${after.direction}`, true);
  }
}
```

## Voice Zone Calculation

### 3D Proximity (Elevation-Aware)
```typescript
class VoiceZoneManager {
  calculateZones(players: PlayerState[]): Map<string, string[]> {
    const zones = new Map<string, string[]>();
    const maxRange = 500; // Pixels
    const elevationPenalty = 0.5; // Volume reduction per level
    
    players.forEach(player => {
      const nearby = players.filter(other => {
        if (other.id === player.id) return false;
        
        // Calculate distance (with elevation weight)
        const dx = other.x - player.x;
        const dy = other.y - player.y;
        const dz = Math.abs(other.elevation - player.elevation) * 64;
        
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        return distance < maxRange;
      });
      
      // Assign to voice room
      const roomId = this.assignRoom(player, nearby);
      
      if (!zones.has(roomId)) {
        zones.set(roomId, []);
      }
      zones.get(roomId)!.push(player.id);
    });
    
    return zones;
  }
  
  assignRoom(player: PlayerState, nearby: PlayerState[]): string {
    // Create room ID based on spatial cluster
    const tileX = Math.floor(player.x / 256); // 8 tiles = 1 zone
    const tileY = Math.floor(player.y / 256);
    const elevation = player.elevation;
    
    return `room-${tileX}-${tileY}-${elevation}`;
  }
  
  calculateVolume(listener: PlayerState, speaker: PlayerState): number {
    // Distance-based attenuation
    const dx = speaker.x - listener.x;
    const dy = speaker.y - listener.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    const baseVolume = Math.max(0, 1 - (distance / 500));
    
    // Elevation penalty
    const elevationDiff = Math.abs(speaker.elevation - listener.elevation);
    const elevationMultiplier = Math.pow(0.5, elevationDiff);
    
    return baseVolume * elevationMultiplier;
  }
}
```

## Optimization: Delta Compression

### Send Only Changes
```typescript
class DeltaCompressor {
  private lastState = new Map<string, PlayerState>();
  
  compress(players: PlayerState[]): any {
    const delta: any = { added: [], updated: [], removed: [] };
    
    players.forEach(player => {
      const last = this.lastState.get(player.id);
      
      if (!last) {
        // New player
        delta.added.push(player);
      } else if (this.hasChanged(last, player)) {
        // Player moved
        delta.updated.push({
          id: player.id,
          x: player.x !== last.x ? player.x : undefined,
          y: player.y !== last.y ? player.y : undefined,
          elevation: player.elevation !== last.elevation ? player.elevation : undefined,
          direction: player.direction !== last.direction ? player.direction : undefined,
        });
      }
      
      this.lastState.set(player.id, player);
    });
    
    // Check for removed players
    this.lastState.forEach((_, id) => {
      if (!players.find(p => p.id === id)) {
        delta.removed.push(id);
        this.lastState.delete(id);
      }
    });
    
    return delta;
  }
  
  hasChanged(a: PlayerState, b: PlayerState): boolean {
    return (
      a.x !== b.x ||
      a.y !== b.y ||
      a.elevation !== b.elevation ||
      a.direction !== b.direction ||
      a.animState !== b.animState
    );
  }
}
```

## Scripts

- `scripts/test-prediction.ts` — Simulate lag, verify prediction accuracy
- `scripts/benchmark-sync.ts` — Measure bandwidth with N players
- `scripts/test-voice-zones.ts` — Verify 3D proximity calculation

## Usage

```typescript
// Client-side setup
const prediction = new IsoPredictionSystem();
const interpolation = new RemotePlayerInterpolation();

// Server-side setup
const gameServer = new GameServer();
const voiceZones = new VoiceZoneManager();
const compressor = new DeltaCompressor();
```

## Integration with Spatial Worlds

This skill provides multiplayer synchronization for isometric Spatial Worlds:
1. Client prediction (responsive movement)
2. Server authority (anti-cheat)
3. Remote interpolation (smooth other players)
4. Voice zones (elevation-aware proximity)
5. Delta compression (bandwidth optimization)

Use this on **Day 3-4** after isometric engine is working.
