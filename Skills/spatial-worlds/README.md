# Spatial Worlds

**Beautiful proximity voice chat worlds with Chrono Trigger-style pixel art.**

---

## What is this?

A multiplayer social platform where people gather in hand-crafted 2D environments and communicate through proximity-based voice chat. Walk toward someone, their voice gets louder. Walk away, it fades. Natural. Human. Magical.

Think "Gather.town meets Chrono Trigger" with world-class artistry.

---

## Vision

### 5 Signature Launch Worlds

1. **The Crossroads** — Medieval fantasy hub with tavern, market, secret garden
2. **Celestial Library** — Floating temple perfect for conferences and workshops  
3. **Neon Shibuya** — Cyberpunk street crossing with arcade and rooftop bar
4. **Forest Cathedral** — Ancient grove with bioluminescent flora and meditation circles
5. **Airship Deck** — Steampunk vessel soaring through clouds

### Core Experience

- **Instant join** — Click link, pick sprite, you're in (no downloads)
- **Spatial audio** — Voice fades naturally with distance, just like real life
- **Living worlds** — Animated water, flickering torches, swaying trees, day/night cycles
- **Social magic** — Sit in chairs, trigger emotes, discover secrets, feel presence

### Technical Excellence

- **60 FPS** on mid-range devices
- **<100ms input latency**
- **<200ms voice latency**
- **50-100 concurrent** users per world
- **Mobile support** (touch controls)

---

## Quick Start

```bash
# Install dependencies
cd Skills/spatial-worlds
bun install

# Start development server
bun run dev

# Open in browser
open http://localhost:3000
```

You'll drop into The Crossroads. Use WASD to move, click chairs to sit, press E for emotes.

---

## Documentation

- **`SKILL.md`** — Full skill overview and usage guide
- **`references/world-design-bible.md`** — Design principles and world blueprints
- **`references/technical-architecture.md`** — System architecture and implementation details
- **`references/art-direction-guide.md`** — Visual style guide and asset specs

---

## Architecture

```
Frontend: Phaser 3 (2D game engine)
Backend: Bun + WebSocket (game server)
Voice: Daily.co (spatial audio SDK)
State: Redis (position tracking, voice zones)
Assets: Tiled maps, Aseprite sprites
```

### Data Flow

```
Player moves → Server validates → Redis updates → Broadcast positions
                                                        ↓
                                            Calculate voice zones
                                                        ↓
                                            Update Daily.co rooms
```

---

## Development Roadmap

### ✅ Phase 0: Planning (Complete)
- [x] Vision document
- [x] World design bible
- [x] Technical architecture
- [x] Art direction guide

### 🚧 Phase 1: MVP (In Progress)
- [ ] Phaser 3 tilemap rendering
- [ ] WebSocket position sync
- [ ] Basic collision system
- [ ] Daily.co voice integration
- [ ] The Crossroads world (first map)
- [ ] 10 character sprites
- [ ] Deploy to Zo, shareable link

### 📋 Phase 2: Polish (Next)
- [ ] 4 additional worlds
- [ ] Emote system (6 emotes)
- [ ] Mobile touch controls
- [ ] Sitting interactions
- [ ] Admin panel (kick/mute)

### 🔮 Phase 3: Creation Tools (Future)
- [ ] Web-based world editor
- [ ] Custom sprite editor
- [ ] Public world gallery
- [ ] Analytics dashboard

---

## File Structure

```
Skills/spatial-worlds/
├── SKILL.md                   # Skill documentation
├── README.md                  # This file
├── package.json               # Dependencies
├── scripts/
│   ├── server.ts              # Game server (Bun + WebSocket)
│   ├── deploy.ts              # Deployment script
│   └── client/                # Phaser 3 client
│       ├── index.html
│       ├── main.ts
│       ├── scenes/
│       ├── systems/
│       └── config.ts
├── references/                # Documentation
│   ├── world-design-bible.md
│   ├── technical-architecture.md
│   └── art-direction-guide.md
└── assets/                    # Game assets
    ├── tilesets/
    ├── sprites/
    ├── worlds/
    └── audio/
```

---

## Contributing

This is a Zo Computer skill created by **dioni.zo.computer**.

### Want to help?

1. **Art**: Create tilesets or character sprites (see `references/art-direction-guide.md`)
2. **Code**: Implement features from the roadmap
3. **Design**: Craft new worlds in Tiled
4. **Feedback**: Playtest and report bugs

---

## License

MIT — Use freely, give credit, share improvements.

---

## Links

- **Live Demo**: https://worlds.dioni.zo.computer (coming soon)
- **Zo Computer**: https://zocomputer.com
- **Support**: help@zocomputer.com

---

**Let's build worlds where people gather, connect, and feel alive.**
