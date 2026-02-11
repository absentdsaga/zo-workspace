---
name: spatial-worlds
description: Create beautiful proximity voice chat worlds with Chrono Trigger-style pixel art. Players gather in hand-crafted 2D environments where voice fades naturally with distance.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: multiplayer-social
  version: 1.0.0
---

# Spatial Worlds

A multiplayer social platform where people gather in gorgeous pixel art worlds and communicate through proximity-based voice chat. Think "Gather.town meets Chrono Trigger" with world-class artistry and game feel.

## Vision

### The Magic
- **Voice flows like water** — Walk toward someone, their voice gets louder. Walk away, it fades. Natural, intuitive, human.
- **Worlds that breathe** — Animated waterfalls, flickering torches, swaying trees, day/night cycles. Every pixel hand-crafted.
- **Effortless gathering** — No downloads, no accounts (optional). Click a link, pick a sprite, you're in.
- **Emergent spaces** — Each world has distinct zones: quiet garden corners for 1:1s, amphitheaters for presentations, taverns for group hangouts.

### Design Principles
1. **Beauty first** — 16-bit JRPG aesthetic done RIGHT. Study Chrono Trigger, Final Fantasy VI, Secret of Mana.
2. **Instant legibility** — You know where to go, what's interactable, who's talking within 3 seconds.
3. **Tactile feel** — Smooth movement (no grid-lock), subtle animations, satisfying collision, responsive controls.
4. **Social affordances** — Chairs to sit, objects to interact with, emotes, layers of expression beyond voice.
5. **Scale thoughtfully** — 50-100 concurrent users per world. Quality over quantity.

## World Design Philosophy

### Spatial Audio Zones
Worlds are designed with acoustic intention:

- **Intimacy zones** (2-4 people) — Garden alcoves, private booths, rooftop corners
- **Small group zones** (5-10 people) — Tavern tables, workshop clusters, campfire circles  
- **Medium group zones** (10-25 people) — Town squares, lecture halls, market streets
- **Amphitheater zones** (25-100 people) — Stages with tiered seating, natural audio dropoff

### Environmental Storytelling
Every world tells a story through:
- **Layered depth** — Foreground grass, midground architecture, background mountains/sky
- **Lighting** — Warm tavern glow, cool moonlight, dappled forest sun
- **Animation** — Water ripples, flag flutter, NPC routines, particle effects
- **Secrets** — Hidden paths, Easter eggs, discoverable lore

### Signature Worlds (Launch Collection)

1. **The Crossroads** — Medieval fantasy hub with inn, market, quest board
2. **Celestial Library** — Floating islands connected by bridges, perfect for conferences  
3. **Neon Shibuya** — Cyberpunk street scene, retro-future aesthetics
4. **Forest Cathedral** — Ancient grove with bioluminescent flora, tranquil acoustics
5. **Airship Deck** — Steampunk vessel sailing through clouds, kinetic energy

## Technical Architecture

### Stack
- **Frontend**: Phaser 3 (battle-tested 2D game engine)
- **Backend**: Bun + WebSocket (sub-millisecond performance)
- **Voice**: Daily.co or Agora SDK (spatial audio with distance attenuation)
- **Hosting**: Zo-hosted with global edge caching

### Data Flow
```
Player Movement → WebSocket → Server (authoritative) → Broadcast positions
                                    ↓
                         Calculate audio zones
                                    ↓
                         Update voice peer groups
```

### Voice Implementation
- **Distance-based volume**: `volume = clamp(1 - (distance / maxHearingRange), 0, 1)`
- **Directional audio**: Optional stereo panning based on relative position
- **Dynamic groups**: Only stream audio from players within hearing range (optimize bandwidth)
- **Voice zones**: Mark areas as "quiet zones" (library) or "broadcast zones" (stage)

### Performance Budget
- 60 FPS on mid-range devices
- <100ms input latency
- <200ms voice latency
- <50MB initial bundle size

## User Experience Flow

### Joining a World
1. Click invite link → Instant preview (no login)
2. Choose sprite from gallery (or randomize)
3. Optional: Set display name
4. Drop into world at spawn point
5. WASD to move, hover over players to see names

### Interactions
- **Voice**: Auto-enabled, push-to-talk option, mute toggle
- **Emotes**: Quick wheel (wave, thumbs up, laugh, think, dance)
- **Sitting**: Click chairs to sit (disables movement, enables AFK state)
- **Objects**: Interact with bookshelves, levers, doors (trigger events)
- **Text chat**: Fallback for voice issues, also for sharing links

### World Creation (Phase 2)
- Tiled map editor integration
- Drag-drop tile palettes
- Audio zone painter
- Spawn point placement
- Publish to gallery

## Asset Pipeline

### Sprite Requirements
- 32x32px character sprites
- 4-direction walk cycles (down, up, left, right)
- 3 frames per direction minimum
- Idle animations
- Sitting pose
- Emote overlays

### Tileset Requirements  
- 16x16px or 32x32px tiles
- Terrain (grass, stone, water, wood)
- Walls and edges with auto-tiling
- Animated tiles (water, fire, magic)
- Collision layer metadata

### Generation Strategy
1. Hand-craft master palettes (8 terrain themes)
2. Generate variations with AI for infinite tilesets
3. Sprite customization: skin tones, hair, clothing layers
4. Maintain strict style guide (Chrono Trigger color palette, dithering patterns)

## Monetization (Optional)

### Free Tier
- Join any public world
- 10 custom sprite slots
- Standard emotes

### Pro Tier ($10/mo)
- Host private worlds (up to 100 concurrent)
- Custom domain mapping
- Advanced sprite editor
- Priority support

### Enterprise
- White-label deployment
- SSO integration
- Custom world development
- Dedicated instances

## Launch Roadmap

### Phase 1: MVP (Week 1-2)
- Single world (The Crossroads)
- Basic movement + collision
- Proximity voice (Daily.co integration)
- 10 sprite options
- Web client only

### Phase 2: Polish (Week 3-4)
- 3 more worlds
- Emote system
- Sitting interactions
- Mobile support (touch controls)
- Admin panel (kick/mute)

### Phase 3: Creation Tools (Month 2)
- World editor
- Custom sprite upload
- Public world gallery
- Analytics dashboard

### Phase 4: Scale (Month 3)
- Multi-region hosting
- 100+ concurrent per world
- Voice quality improvements
- Accessibility features (captions, colorblind modes)

## Usage

```bash
# Start development server
cd Skills/spatial-worlds
bun run dev

# Build production bundle
bun run build

# Deploy to Zo
bun run deploy
```

Access at: `https://worlds.dioni.zo.computer`

## Scripts

- `scripts/server.ts` — WebSocket game server
- `scripts/client/` — Phaser 3 game client
- `scripts/world-editor/` — Map creation tools
- `scripts/sprite-generator.ts` — AI sprite generation

## References

- `references/phaser-spatial-audio.md` — Phaser 3 + voice integration patterns
- `references/tiled-integration.md` — Importing Tiled maps
- `references/chrono-trigger-analysis.md` — Art direction deep dive

## Assets

- `assets/tilesets/` — Master tile palettes
- `assets/sprites/` — Character sprite sheets
- `assets/worlds/` — Pre-built map JSONs
- `assets/audio/` — Ambient soundscapes (optional)
