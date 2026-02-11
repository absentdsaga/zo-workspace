import { ServerWebSocket } from 'bun';

export interface PlayerState {
  id: string;
  x: number;
  y: number;
  elevation: number;
  direction: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  animState: 'idle' | 'walk';
  timestamp: number;
}

export interface MoveCommand {
  type: 'move';
  input: {
    up: boolean;
    down: boolean;
    left: boolean;
    right: boolean;
  };
  timestamp: number;
}

export interface JoinCommand {
  type: 'join';
  playerName: string;
}

export class MultiplayerServer {
  private players = new Map<string, PlayerState>();
  private sockets = new Map<string, ServerWebSocket>();
  
  handleConnect(ws: ServerWebSocket) {
    const playerId = crypto.randomUUID();
    ws.data = { playerId };
    this.sockets.set(playerId, ws);
    
    console.log(`Player ${playerId} connected`);
  }
  
  handleDisconnect(ws: ServerWebSocket) {
    const playerId = ws.data?.playerId;
    if (playerId) {
      this.players.delete(playerId);
      this.sockets.delete(playerId);
      
      // Broadcast player left
      this.broadcast({
        type: 'player_left',
        playerId,
      });
      
      console.log(`Player ${playerId} disconnected`);
    }
  }
  
  handleMessage(ws: ServerWebSocket, message: string) {
    const data = JSON.parse(message);
    const playerId = ws.data.playerId;
    
    if (data.type === 'join') {
      this.handleJoin(ws, data as JoinCommand);
    } else if (data.type === 'move') {
      this.handleMove(ws, data as MoveCommand);
    }
  }
  
  private handleJoin(ws: ServerWebSocket, cmd: JoinCommand) {
    const playerId = ws.data.playerId;
    
    // Create player state (spawn at center)
    const playerState: PlayerState = {
      id: playerId,
      x: 640,
      y: 360,
      elevation: 0,
      direction: 's',
      animState: 'idle',
      timestamp: Date.now(),
    };
    
    this.players.set(playerId, playerState);
    
    // Send initial state to new player (all existing players)
    ws.send(JSON.stringify({
      type: 'init',
      playerId,
      players: Array.from(this.players.values()),
    }));
    
    // Broadcast new player to all others
    this.broadcast({
      type: 'player_joined',
      player: playerState,
    }, playerId);
    
    console.log(`Player ${playerId} joined as ${cmd.playerName}`);
  }
  
  private handleMove(ws: ServerWebSocket, cmd: any) {
    const playerId = ws.data.playerId;
    const player = this.players.get(playerId);
    if (!player) return;

    // CLIENT AUTHORITATIVE: Use position from client if provided
    if (cmd.position) {
      player.x = cmd.position.x;
      player.y = cmd.position.y;
    } else {
      // Fallback: Server-side calculation (legacy)
      const delta = 1 / 60;
      const speed = 150;

      let dirX = 0, dirY = 0;
      if (cmd.input.up) dirY -= 1;
      if (cmd.input.down) dirY += 1;
      if (cmd.input.left) dirX -= 1;
      if (cmd.input.right) dirX += 1;

      // Normalize diagonal
      if (dirX !== 0 && dirY !== 0) {
        dirX *= 0.707;
        dirY *= 0.707;
      }

      // Isometric velocity
      const isoX = (dirX - dirY) * speed * delta;
      const isoY = (dirX + dirY) * 0.5 * speed * delta;

      // Update position
      player.x += isoX;
      player.y += isoY;
    }

    // Update elevation if provided
    if (cmd.elevation !== undefined) {
      player.elevation = cmd.elevation;
    }

    player.timestamp = Date.now();

    // Determine direction and animation state from input
    let dirX = 0, dirY = 0;
    if (cmd.input.up) dirY -= 1;
    if (cmd.input.down) dirY += 1;
    if (cmd.input.left) dirX -= 1;
    if (cmd.input.right) dirX += 1;

    if (dirX !== 0 || dirY !== 0) {
      player.animState = 'walk';
      player.direction = this.getDirection(dirX, dirY);
    } else {
      player.animState = 'idle';
    }

    // Broadcast to nearby players (within 800px)
    this.broadcastToProximity(player);
  }
  
  private getDirection(dirX: number, dirY: number): PlayerState['direction'] {
    const angle = Math.atan2(dirY, dirX);
    const degrees = (angle * 180 / Math.PI + 360) % 360;
    
    // 8 directions (45° each)
    if (degrees >= 337.5 || degrees < 22.5) return 'e';
    if (degrees >= 22.5 && degrees < 67.5) return 'se';
    if (degrees >= 67.5 && degrees < 112.5) return 's';
    if (degrees >= 112.5 && degrees < 157.5) return 'sw';
    if (degrees >= 157.5 && degrees < 202.5) return 'w';
    if (degrees >= 202.5 && degrees < 247.5) return 'nw';
    if (degrees >= 247.5 && degrees < 292.5) return 'n';
    return 'ne';
  }
  
  private broadcastToProximity(player: PlayerState) {
    // Find players within 800px (voice/render range)
    const range = 800;
    
    this.players.forEach((other, otherId) => {
      if (other.id === player.id) return;
      
      const dx = other.x - player.x;
      const dy = other.y - player.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < range) {
        const ws = this.sockets.get(otherId);
        if (ws) {
          ws.send(JSON.stringify({
            type: 'state',
            players: [player],
            timestamp: Date.now(),
          }));
        }
      }
    });
  }
  
  private broadcast(message: any, excludeId?: string) {
    this.sockets.forEach((ws, playerId) => {
      if (playerId !== excludeId) {
        ws.send(JSON.stringify(message));
      }
    });
  }
}
