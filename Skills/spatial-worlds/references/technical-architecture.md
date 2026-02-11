# Spatial Worlds — Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Client (Browser)                     │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  Phaser 3  │  │ WebSocket    │  │  Daily.co        │    │
│  │  Game      │◄─┤  Client      │  │  Voice SDK       │    │
│  │  Engine    │  └──────┬───────┘  └────────┬─────────┘    │
│  └────────────┘         │                   │               │
└────────────────────────┼───────────────────┼───────────────┘
                         │                   │
                    WSS  │              HTTPS│ WebRTC
                         │                   │
┌────────────────────────┼───────────────────┼───────────────┐
│                    Zo Server                │               │
│  ┌─────────────────┐  │         ┌──────────┴────────┐      │
│  │  Game Server    │◄─┘         │  Voice Manager    │      │
│  │  (Bun+WS)       │            │  (Daily.co API)   │      │
│  │                 │            └───────────────────┘      │
│  │ • Position sync │                                       │
│  │ • Collision     │            ┌───────────────────┐      │
│  │ • State mgmt    │            │   Redis           │      │
│  │ • Audio zones   │◄───────────┤   (State store)   │      │
│  └─────────────────┘            └───────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Static Assets (CDN)                            │       │
│  │  • Tilesets, sprites, audio, maps               │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack Decisions

### Frontend: Phaser 3
**Why**: Battle-tested 2D game engine with perfect tooling for this use case
- Canvas/WebGL rendering (hardware accelerated)
- Built-in tilemap support (Tiled integration)
- Sprite animation system
- Input handling (keyboard, mouse, touch)
- Camera system (zoom, pan, follow)
- Active community, extensive plugins

**Alternatives considered**:
- PixiJS: Lower level, more boilerplate
- Three.js: Overkill for 2D
- Custom Canvas: Reinventing the wheel

### Backend: Bun + WebSocket
**Why**: Sub-millisecond performance, modern DX
- Native WebSocket support (no libraries)
- TypeScript first-class
- Fast startup (<100ms cold start)
- Low memory footprint (~50MB baseline)

**Server responsibilities**:
1. Authoritative position tracking (anti-cheat)
2. Collision validation server-side
3. Voice zone calculation
4. Player state (emotes, sitting, AFK)
5. World persistence (who's where)

### Voice: Daily.co
**Why**: Spatial audio out-of-the-box, proven scale
- 3D positional audio API
- Distance-based attenuation
- Automatic bandwidth optimization
- SFU architecture (scales to 100+ participants)
- Fallback to mesh networking for small groups

**Alternative**: Agora (similar features, more complex pricing)

**Integration approach**:
- Game server calculates audio zones
- Clients subscribe to Daily.co rooms per zone
- Dynamic room switching as players move
- Server doesn't proxy audio (peer-to-peer)

### State Management: Redis
**Why**: Fast lookups, pub/sub for real-time updates
- Player positions (spatial index)
- Voice room memberships
- World state (object interactions)
- Session management

**Data structures**:
```typescript
// Player position (GeoHash for spatial queries)
GEOADD world:crossroads 40.7128 -74.0060 player:alice

// Voice zone membership
SADD voice:zone:plaza player:alice player:bob

// Player state
HSET player:alice x 100 y 200 sprite warrior emote wave
```

### Asset Pipeline: Tiled + Custom Tools
**Why**: Industry standard map editor, scriptable export
- Tiled for map creation (.tmx → JSON)
- Aseprite for sprite animation (.ase → sprite sheets)
- Custom Bun scripts for optimization (atlas packing, compression)

---

## Data Flow Diagrams

### Player Movement Flow
```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Client │     │  WSS   │     │ Server │     │ Redis  │
└───┬────┘     └───┬────┘     └───┬────┘     └───┬────┘
    │              │              │              │
    │  move(x,y)   │              │              │
    ├─────────────►│              │              │
    │              │ validate     │              │
    │              ├─────────────►│              │
    │              │              │ checkCollision
    │              │              │ updatePosition
    │              │              ├─────────────►│
    │              │              │◄─────────────┤
    │              │ broadcast    │              │
    │              │◄─────────────┤              │
    │ position     │              │              │
    │◄─────────────┤              │              │
    │ (update sprite)             │              │
    │              │              │              │
```

### Voice Zone Management Flow
```
Player moves → Server calculates distance to all players
                         ↓
           Group into voice zones (clusters within 30 tiles)
                         ↓
           Compare to current zone membership
                         ↓
         If zone changed: Update Daily.co room subscription
                         ↓
           Client switches voice rooms (seamless transition)
```

### Interaction Flow (Sitting in Chair)
```
Click chair → Send interact(chair:5) → Server validates
                                           ↓
                                    Chair available?
                                           ↓
                                    Update state (sitting:true)
                                           ↓
                            Broadcast to nearby players
                                           ↓
              All clients update sprite → sitting pose
```

---

## Performance Budget

### Client-Side (60 FPS target)
| System | Budget | Notes |
|--------|--------|-------|
| Rendering | 12ms | Phaser draw calls |
| Physics | 2ms | Collision checks (client prediction) |
| Network | 1ms | WebSocket send/receive |
| Input | 1ms | Keyboard/mouse handling |
| Audio | 0ms | Offloaded to WebRTC |
| **Total** | **16ms** | (60 FPS = 16.67ms frame budget) |

**Optimizations**:
- Sprite culling (don't render off-screen)
- Dirty rectangle rendering (only redraw changed areas)
- Object pooling (reuse sprite instances)
- Asset lazy loading (stream tiles as needed)

### Server-Side (Sub-100ms latency target)
| Operation | Latency | Throughput |
|-----------|---------|------------|
| Position update | <10ms | 10,000 ops/sec |
| Voice zone calc | <5ms | 1,000 calcs/sec |
| Redis read | <1ms | 100,000 ops/sec |
| Redis write | <2ms | 50,000 ops/sec |

**Scaling strategy**:
- Horizontal: One server per world (50-100 players)
- Vertical: 4 CPU cores, 8GB RAM per server
- Load balancer routes by world ID
- Redis cluster for cross-world state

### Network Budget
| Data | Size | Frequency | Bandwidth |
|------|------|-----------|-----------|
| Position update | 20 bytes | 10 Hz | 200 B/s/player |
| Voice (Daily.co) | N/A | Peer-to-peer | ~50 Kbps/player |
| Asset download | ~10 MB | Once | One-time |

**Total per player**: ~60 Kbps (extremely light)

---

## Implementation Phases

### Phase 0: Proof of Concept (3 days)
**Goal**: Validate core tech stack integration

- [ ] Phaser 3 hello world (render tilemap)
- [ ] WebSocket connection (Bun server)
- [ ] Multi-client position sync
- [ ] Daily.co voice integration (single room)
- [ ] Deploy to Zo, shareable link

**Deliverable**: Barebones multiplayer with voice

---

### Phase 1: MVP (2 weeks)
**Goal**: First playable world

**Week 1: Game Engine**
- [ ] Tile-based collision system
- [ ] Sprite animation (4-direction walk cycles)
- [ ] Camera follow + zoom controls
- [ ] Name tags above players
- [ ] Basic UI (mute button, player list)

**Week 2: World + Voice**
- [ ] The Crossroads map (Tiled → Phaser)
- [ ] 10 character sprites (diverse)
- [ ] Proximity voice zones (15/30 tile ranges)
- [ ] Sitting interaction (chairs)
- [ ] Deploy + stress test (20 concurrent users)

**Deliverable**: The Crossroads world, sharable link, playable

---

### Phase 2: Polish (2 weeks)
**Goal**: Production-ready experience

**Week 3: UX + Assets**
- [ ] 3 more worlds (Library, Shibuya, Forest)
- [ ] Emote system (6 emotes)
- [ ] Mobile touch controls
- [ ] Loading screen + asset preloader
- [ ] Audio ambiance per world

**Week 4: Social Features**
- [ ] Whisper mode (private voice channels)
- [ ] AFK detection (auto-sit after 5 min)
- [ ] Player volume sliders (per-user)
- [ ] Broadcast mode (for presentations)
- [ ] Admin panel (kick/mute)

**Deliverable**: 4 worlds, mobile support, full feature set

---

### Phase 3: Creation Tools (1 month)
**Goal**: User-generated content

**Week 5-6: World Editor**
- [ ] Web-based Tiled integration
- [ ] Drag-drop tile palettes (8 themes)
- [ ] Audio zone painter UI
- [ ] Collision layer editor
- [ ] Publish to gallery

**Week 7-8: Customization**
- [ ] Sprite editor (layered: skin, hair, clothes)
- [ ] Custom sprite upload (validation)
- [ ] World gallery (browse public worlds)
- [ ] Analytics dashboard (traffic, hotspots)

**Deliverable**: World creation tools, public gallery

---

### Phase 4: Scale (Ongoing)
**Goal**: 100+ concurrent per world, global reach

- [ ] Multi-region deployment (US, EU, APAC)
- [ ] Auto-scaling (spawn servers on demand)
- [ ] Voice quality tuning (noise suppression, echo cancellation)
- [ ] Accessibility (captions, colorblind modes, screen reader)
- [ ] Moderation tools (report, auto-mute)

**Deliverable**: Production-scale platform

---

## File Structure

```
Skills/spatial-worlds/
├── SKILL.md                      # Main documentation
├── scripts/
│   ├── server.ts                 # Game server (Bun + WebSocket)
│   ├── deploy.ts                 # Deployment script
│   ├── client/                   # Phaser 3 client
│   │   ├── index.html
│   │   ├── main.ts               # Entry point
│   │   ├── scenes/
│   │   │   ├── Boot.ts           # Asset loading
│   │   │   ├── Game.ts           # Main game loop
│   │   │   └── UI.ts             # HUD overlay
│   │   ├── systems/
│   │   │   ├── Movement.ts       # Player movement
│   │   │   ├── Voice.ts          # Daily.co integration
│   │   │   ├── Collision.ts      # Tilemap collision
│   │   │   └── Animation.ts      # Sprite animations
│   │   └── config.ts             # Phaser config
│   ├── world-editor/             # Map creation UI
│   │   ├── index.html
│   │   ├── editor.ts
│   │   └── TilesetPalette.ts
│   └── sprite-generator.ts       # AI sprite generation
├── references/
│   ├── world-design-bible.md     # Design principles
│   ├── technical-architecture.md # This file
│   ├── phaser-spatial-audio.md   # Integration guide
│   └── chrono-trigger-analysis.md # Art direction
├── assets/
│   ├── tilesets/
│   │   ├── medieval/             # The Crossroads tiles
│   │   ├── library/              # Celestial Library tiles
│   │   ├── cyberpunk/            # Neon Shibuya tiles
│   │   ├── forest/               # Forest Cathedral tiles
│   │   └── steampunk/            # Airship tiles
│   ├── sprites/
│   │   ├── characters/           # 50 sprite sheets
│   │   └── emotes/               # Emote overlays
│   ├── worlds/
│   │   ├── crossroads.json       # Tiled export
│   │   ├── library.json
│   │   ├── shibuya.json
│   │   ├── forest.json
│   │   └── airship.json
│   └── audio/
│       ├── ambiance/             # World soundscapes
│       └── sfx/                  # Interaction sounds
└── package.json                  # Dependencies
```

---

## API Reference

### WebSocket Protocol

**Client → Server**

```typescript
// Join world
{
  type: "join",
  worldId: "crossroads",
  playerId: "alice",
  sprite: "warrior"
}

// Move player
{
  type: "move",
  x: 100,
  y: 200,
  direction: "down"
}

// Emote
{
  type: "emote",
  emote: "wave"
}

// Interact with object
{
  type: "interact",
  objectId: "chair:5"
}
```

**Server → Client**

```typescript
// Player joined
{
  type: "player_joined",
  player: {
    id: "alice",
    x: 100,
    y: 200,
    sprite: "warrior",
    name: "Alice"
  }
}

// Position update (broadcast)
{
  type: "positions",
  players: [
    { id: "alice", x: 105, y: 202, direction: "down" },
    { id: "bob", x: 120, y: 180, direction: "left" }
  ]
}

// Voice zone update
{
  type: "voice_zone",
  roomId: "crossroads-plaza-1",
  players: ["alice", "bob", "charlie"]
}

// Interaction result
{
  type: "interaction",
  objectId: "chair:5",
  success: true,
  state: "occupied"
}
```

### Daily.co Integration

```typescript
import Daily from '@daily-co/daily-js';

// Create call client
const call = Daily.createCallObject();

// Join voice room
await call.join({
  url: `https://dioni.daily.co/${roomId}`,
  userName: playerId
});

// Update spatial audio positions (every frame)
call.updateParticipantAudioLevel(remoteParticipantId, volume);

// Leave room (when changing zones)
await call.leave();
```

### Redis Schema

```bash
# Player position (sorted set for range queries)
ZADD world:crossroads:x {x} player:alice
ZADD world:crossroads:y {y} player:alice

# Player state (hash)
HSET player:alice 
  x 100 
  y 200 
  sprite warrior 
  sitting false 
  voiceRoom crossroads-plaza-1

# Voice room membership (set)
SADD voice:crossroads-plaza-1 player:alice player:bob

# World metadata (hash)
HSET world:crossroads 
  name "The Crossroads"
  maxPlayers 100
  currentPlayers 42
```

---

## Security Considerations

### Client Validation
- Never trust client position (server validates collision)
- Rate limit move commands (max 10 Hz)
- Sanitize emotes and names (XSS prevention)

### Voice Privacy
- Daily.co rooms are ephemeral (auto-delete after 5 min empty)
- No voice recording server-side
- Mute/kick controls for admins

### World Creation
- Validate uploaded tilesets (file size, dimensions)
- Scan custom sprites for inappropriate content (AI moderation)
- Rate limit world publishes (1 per hour)

### DDoS Protection
- WebSocket connection limits (100 per IP)
- Cloudflare proxy (rate limiting, bot detection)
- Graceful degradation (fallback to text chat if voice fails)

---

## Monitoring & Analytics

### Key Metrics
- **Concurrent users** (per world, total)
- **Average session duration**
- **Voice quality** (packet loss, latency)
- **Heatmaps** (where players gather)
- **Interaction rates** (emotes, sits, objects)

### Logging
```typescript
// Server logs (structured JSON)
{
  timestamp: "2026-02-09T20:50:00Z",
  level: "info",
  event: "player_joined",
  worldId: "crossroads",
  playerId: "alice",
  totalPlayers: 42
}
```

### Alerts
- Voice latency >500ms (Slack notification)
- Server CPU >80% (auto-scale trigger)
- Player count >80% capacity (warm up new server)

---

## Deployment

### Zo Hosting
```bash
# Build client
cd Skills/spatial-worlds/scripts/client
bun run build  # → dist/

# Deploy static assets
zo site create --name spatial-worlds --dir dist/

# Start game server
bun run scripts/server.ts  # Port 3000

# Register service
zo service register \
  --name spatial-worlds-server \
  --port 3000 \
  --protocol http
```

### Environment Variables
```bash
DAILY_API_KEY=xxx           # Daily.co API key
REDIS_URL=redis://localhost:6379
NODE_ENV=production
```

### Custom Domain
- `https://worlds.dioni.zo.computer` (static assets)
- `wss://ws.worlds.dioni.zo.computer` (game server)

---

## Next Steps

1. **Phase 0 POC** (Start now)
   - Spin up Bun server with WebSocket echo
   - Phaser 3 tilemap from Tiled JSON
   - Test Daily.co integration locally

2. **Design First World** (Parallel)
   - Create The Crossroads in Tiled
   - Define collision layer
   - Mark audio zones

3. **Sprite Pipeline** (Parallel)
   - Generate 10 diverse character sprites (AI)
   - Export 4-direction walk cycles (Aseprite)
   - Optimize sprite sheets (atlas packing)

4. **User Testing** (Week 2)
   - Dogfood with 10 users
   - Gather feedback on voice quality, UX
   - Iterate on design

Ready to build this. Where should we start?
