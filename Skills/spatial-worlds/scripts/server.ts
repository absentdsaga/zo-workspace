import { ServerWebSocket } from 'bun';

// ============ MULTIPLAYER SERVER ============

interface PlayerState {
  id: string;
  x: number;
  y: number;
  elevation: number;
  direction: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  animState: 'idle' | 'walk';
  timestamp: number;
  lastUpdateTime: number;
}

interface MoveCommand {
  type: 'move';
  input: {
    up: boolean;
    down: boolean;
    left: boolean;
    right: boolean;
  };
  elevation?: number;
  position?: {
    x: number;
    y: number;
  };
  timestamp: number;
}

class MultiplayerServer {
  private players = new Map<string, PlayerState>();
  private sockets = new Map<string, ServerWebSocket>();
  
  handleConnect(ws: ServerWebSocket) {
    const playerId = crypto.randomUUID();
    ws.data = { playerId };
    this.sockets.set(playerId, ws);
    console.log(`✅ Player ${playerId.slice(0, 8)} connected`);
  }
  
  handleDisconnect(ws: ServerWebSocket) {
    const playerId = ws.data?.playerId;
    if (playerId) {
      this.players.delete(playerId);
      this.sockets.delete(playerId);
      
      this.broadcast({
        type: 'player_left',
        playerId,
      });
      
      console.log(`❌ Player ${playerId.slice(0, 8)} disconnected`);
    }
  }
  
  handleMessage(ws: ServerWebSocket, message: string) {
    try {
      const data = JSON.parse(message);
      const playerId = ws.data.playerId;
      
      if (data.type === 'join') {
        this.handleJoin(ws, data);
      } else if (data.type === 'move') {
        this.handleMove(ws, data);
      }
    } catch (e) {
      console.error('Invalid message:', e);
    }
  }
  
  private handleJoin(ws: ServerWebSocket, cmd: any) {
    const playerId = ws.data.playerId;
    
    const now = Date.now();
    const playerState: PlayerState = {
      id: playerId,
      x: 640,
      y: 360,
      elevation: 0,
      direction: 's',
      animState: 'idle',
      timestamp: now,
      lastUpdateTime: now,
    };
    
    this.players.set(playerId, playerState);
    
    ws.send(JSON.stringify({
      type: 'init',
      playerId,
      players: Array.from(this.players.values()),
    }));
    
    this.broadcast({
      type: 'player_joined',
      player: playerState,
    }, playerId);
    
    console.log(`👤 Player ${playerId.slice(0, 8)} joined (${this.players.size} total)`);
  }
  
  private handleMove(ws: ServerWebSocket, cmd: MoveCommand) {
    const playerId = ws.data.playerId;
    const player = this.players.get(playerId);
    if (!player) return;

    const now = Date.now();

    // CLIENT AUTHORITATIVE: Use client's actual position
    if (cmd.position) {
      player.x = cmd.position.x;
      player.y = cmd.position.y;
      
      // DEBUG: Log what server stores
      console.log(`[SERVER] Storing player ${playerId.slice(0,4)}: x=${player.x} y=${player.y} elevation=${player.elevation}`);

      // DEBUG: Log position updates occasionally
      if (Math.random() < 0.01) {
        console.log(`🔄 Player ${playerId.slice(0,8)} position update: (${Math.round(player.x)}, ${Math.round(player.y)})`);
      }
    } else {
      // WARN: Client didn't send position (old client or bug)
      if (Math.random() < 0.05) {
        console.warn(`⚠️  Player ${playerId.slice(0,8)} sent move without position data`);
      }
    }

    // Update elevation if provided
    if (cmd.elevation !== undefined) {
      player.elevation = Math.max(0, Math.min(3, cmd.elevation));
    }

    // Determine animation state and direction from input
    let dirX = 0, dirY = 0;
    if (cmd.input.up) dirY -= 1;
    if (cmd.input.down) dirY += 1;
    if (cmd.input.left) dirX -= 1;
    if (cmd.input.right) dirX += 1;

    const direction = this.getDirectionKey(dirX, dirY);

    if (direction) {
      player.animState = 'walk';
      player.direction = direction as PlayerState['direction'];
    } else {
      player.animState = 'idle';
    }

    player.timestamp = now;
    player.lastUpdateTime = now;
    this.broadcastToProximity(player);
  }

  private getDirectionKey(x: number, y: number): string | null {
    if (x === 0 && y === -1) return 'n';
    if (x === 1 && y === -1) return 'ne';
    if (x === 1 && y === 0) return 'e';
    if (x === 1 && y === 1) return 'se';
    if (x === 0 && y === 1) return 's';
    if (x === -1 && y === 1) return 'sw';
    if (x === -1 && y === 0) return 'w';
    if (x === -1 && y === -1) return 'nw';
    return null;
  }
  
  
  private broadcastToProximity(player: PlayerState) {
    const range = 800;
    let sentTo = 0;

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
          sentTo++;
        }
      }
    });

    // DEBUG: Log broadcasts
    if (sentTo > 0) {
      console.log(`📡 Broadcasted ${player.id.slice(0,8)} position (${Math.round(player.x)},${Math.round(player.y)}) to ${sentTo} players`);
    }
  }
  
  private broadcast(message: any, excludeId?: string) {
    this.sockets.forEach((ws, playerId) => {
      if (playerId !== excludeId) {
        ws.send(JSON.stringify(message));
      }
    });
  }
}

const mp = new MultiplayerServer();

// ============ HTTP + WEBSOCKET SERVER ============

const server = Bun.serve({
  port: 3000,
  
  async fetch(req, server) {
    const url = new URL(req.url);
    
    // WebSocket upgrade
    if (req.headers.get('upgrade') === 'websocket') {
      const success = server.upgrade(req);
      return success ? undefined : new Response('WebSocket upgrade failed', { status: 500 });
    }

    // Serve isometric version at root
    if (url.pathname === '/') {
      return new Response(Bun.file('scripts/client/index-iso.html'));
    }

    // Serve client files
    if (url.pathname.startsWith('/scripts/client/')) {
      const filePath = url.pathname.slice(1);
      const file = Bun.file(filePath);
      if (await file.exists()) return new Response(file);
    }

    // Serve node_modules (for Phaser)
    if (url.pathname.startsWith('/node_modules/')) {
      const filePath = url.pathname.slice(1);
      const file = Bun.file(filePath);
      if (await file.exists()) return new Response(file);
    }

    // Serve assets (sprites, maps, etc.)
    if (url.pathname.startsWith('/assets/')) {
      const filePath = url.pathname.slice(1);
      const file = Bun.file(filePath);
      if (await file.exists()) return new Response(file);
    }

    // Serve dist (compiled JS) with no-cache
    if (url.pathname.startsWith('/dist/')) {
      const filePath = url.pathname.slice(1);
      const file = Bun.file(filePath);
      if (await file.exists()) {
        return new Response(file, {
          headers: {
            'Content-Type': 'application/javascript; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        });
      }
    }

    // Serve favicon.ico
    if (url.pathname === '/favicon.ico') {
      const file = Bun.file('public/favicon.ico');
      if (await file.exists()) {
        return new Response(file, {
          headers: {
            'Content-Type': 'image/x-icon',
          }
        });
      }
    }

    return new Response('Not Found', { status: 404 });
  },
  
  websocket: {
    message(ws, message) {
      mp.handleMessage(ws, message as string);
    },
    open(ws) {
      mp.handleConnect(ws);
    },
    close(ws) {
      mp.handleDisconnect(ws);
    }
  }
});

console.log(`🎮 Spatial Worlds Dev Server (ISOMETRIC + MULTIPLAYER)`);
console.log(`🌐 http://localhost:${server.port}`);
console.log(`🔌 WebSocket: ws://localhost:${server.port}`);
console.log(`\n📋 Features:`);
console.log(`   • 8-direction movement`);
console.log(`   • Depth sorting (elevation-aware)`);
console.log(`   • Real-time multiplayer (WebSocket)`);
console.log(`   • Client-side prediction`);
console.log(`   • 60 FPS target\n`);
