# Learning Curriculum — Spatial Worlds Engineering

## 30-Day Intensive Training Program

A structured curriculum to acquire all necessary skills for world-class execution. Each day builds on the previous, culminating in a fully functional MVP.

---

## Week 1: Core Game Engine & Networking (Critical Path)

### Day 1: Phaser 3 Fundamentals + Tilemap Mastery
**Goal**: Render a large tilemap at 60 FPS with smooth camera

**Morning (4h): Study**
- Read: [Phaser 3 Tilemap Tutorial](https://phaser.io/tutorials/making-your-first-phaser-3-game)
- Watch: Phaser 3 tilemap examples (official docs)
- Study: Tiled map editor basics (create simple map)

**Afternoon (4h): Build**
- Create: 100×100 tile map in Tiled (mix terrain types)
- Implement: Phaser scene that loads map
- Add: Camera follow with WASD movement
- Optimize: Measure FPS, ensure 60 FPS locked

**Deliverable**: Playable tilemap demo with smooth scrolling

**Resources**:
- https://phaser.io/examples/v3/category/tilemap
- https://www.mapeditor.org/
- Phaser Discord: https://discord.gg/phaser

---

### Day 2: Collision Detection & Spatial Optimization
**Goal**: Implement tile-based collision + sprite culling

**Morning (4h): Study**
- Read: "Real-Time Collision Detection" (Chapter 7: Spatial Partitioning)
- Study: Phaser collision examples
- Research: Spatial hash grids (technique for fast neighbor queries)

**Afternoon (4h): Build**
- Implement: Tile-based collision (prevent walking through walls)
- Add: 1000 NPCs moving randomly
- Optimize: Spatial culling (only render on-screen sprites)
- Profile: Use Chrome DevTools to identify bottlenecks

**Deliverable**: 1000 sprites at 60 FPS with working collision

**Resources**:
- Phaser Arcade Physics: https://photonstorm.github.io/phaser3-docs/Phaser.Physics.Arcade.html
- Spatial Hash Grid Tutorial: https://conkerjo.wordpress.com/2009/06/13/spatial-hashing-implementation-for-fast-2d-collisions/

---

### Day 3: WebSocket Real-Time Multiplayer Foundation
**Goal**: Sync player positions across multiple clients

**Morning (4h): Study**
- Read: Gabriel Gambetta's "Fast-Paced Multiplayer" (Parts 1-3)
  - https://www.gabrielgambetta.com/client-server-game-architecture.html
- Study: Bun WebSocket API
- Review: Authoritative server patterns

**Afternoon (4h): Build**
- Create: Bun WebSocket server (position broadcast)
- Implement: Client sends move commands (10 Hz)
- Add: Server validates + broadcasts to all clients
- Test: Run 10 browser tabs, verify sync

**Deliverable**: Multi-client position synchronization

**Resources**:
- Bun WebSocket docs: https://bun.sh/docs/api/websockets
- Gabriel Gambetta's series: https://www.gabrielgambetta.com/client-server-game-architecture.html

---

### Day 4: Client-Side Prediction & Lag Compensation
**Goal**: Smooth movement even with 100ms latency

**Morning (4h): Study**
- Read: Gabriel Gambetta's "Fast-Paced Multiplayer" (Part 4)
- Study: Source engine networking (Valve's approach)
- Watch: GDC talk "I Shot You First" (lag compensation)

**Afternoon (4h): Build**
- Implement: Client-side prediction (move immediately)
- Add: Server reconciliation (rollback on mismatch)
- Simulate: 100ms artificial latency, test smoothness
- Tune: Interpolation parameters (find sweet spot)

**Deliverable**: Responsive movement with simulated lag

**Resources**:
- Source networking: https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
- GDC Talk: https://www.youtube.com/watch?v=h47zZrqjgLc

---

### Day 5: Redis Spatial Indexing & Voice Zones
**Goal**: Efficiently query nearby players for voice grouping

**Morning (4h): Study**
- Read: Redis geospatial documentation
- Study: GeoHash algorithm (how spatial indexing works)
- Research: Clustering algorithms (K-means, DBSCAN)

**Afternoon (4h): Build**
- Implement: Redis GEOADD for player positions
- Add: GEORADIUS query (find players within 30 tiles)
- Create: Voice zone clustering (group into <50 player rooms)
- Benchmark: 10,000 player positions, measure query speed

**Deliverable**: Voice zone algorithm (<10ms per update)

**Resources**:
- Redis Geo commands: https://redis.io/commands/geoadd
- GeoHash explanation: https://www.movable-type.co.uk/scripts/geohash.html

---

### Day 6-7: Daily.co Spatial Audio Integration
**Goal**: Working proximity voice with distance attenuation

**Day 6 Morning (4h): Study**
- Read: Daily.co spatial audio documentation
- Watch: Daily.co tutorial videos
- Study: Audio attenuation curves (linear vs exponential)
- Research: 3D audio positioning (panning, reverb)

**Day 6 Afternoon (4h): Build**
- Setup: Daily.co account + API key
- Implement: Join voice room on world enter
- Add: Basic voice chat (no spatial audio yet)
- Test: 5 users in same room, verify audio works

**Day 7 Morning (4h): Study**
- Read: Web Audio API documentation
- Study: Spatial audio examples (Three.js audio)
- Research: Distance attenuation formulas

**Day 7 Afternoon (4h): Build**
- Implement: Calculate distance between players
- Add: Exponential volume attenuation (volume = 1 - (dist/maxRange)²)
- Implement: Dynamic room switching (change rooms as players move)
- Test: Walk toward/away from speakers, verify fade

**Deliverable**: Proximity voice chat prototype

**Resources**:
- Daily.co docs: https://docs.daily.co/
- Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

---

## Week 2: Pixel Art, World Building & Polish

### Day 8: Chrono Trigger Art Analysis
**Goal**: Extract exact style rules from the source

**Morning (4h): Study**
- Find: Chrono Trigger sprite rips (Spriters Resource)
- Analyze: Color palettes (extract hex codes)
- Study: Dithering patterns (screenshot analysis)
- Note: Tile grammar rules (how tiles connect)

**Afternoon (4h): Practice**
- Hand-draw: 1 character sprite (32×32px)
- Create: 4-direction walk cycle (4 frames each)
- Apply: Chrono Trigger palette + dithering
- Export: Sprite sheet (16 frames, 32×128px)

**Deliverable**: Hand-crafted character sprite matching CT style

**Resources**:
- Spriters Resource: https://www.spriters-resource.com/snes/chronotrigger/
- Aseprite tutorial: https://www.aseprite.org/docs/
- MortMort pixel art: https://www.youtube.com/c/MortMort

---

### Day 9: AI-Assisted Sprite Generation Pipeline
**Goal**: Generate 50 diverse character sprites efficiently

**Morning (4h): Study**
- Research: AI pixel art generation (Midjourney, Stable Diffusion)
- Study: Color quantization algorithms (median cut, octree)
- Review: Sprite sheet packing (TexturePacker)

**Afternoon (4h): Build**
- Create: Bun script to generate sprites via AI
- Implement: Post-processing (quantize to 64-color palette)
- Add: Dithering pass (checkerboard pattern)
- Batch: Generate 50 character variations

**Deliverable**: 50 sprites matching Chrono Trigger aesthetic

**Script outline**:
```typescript
// scripts/generate-sprites.ts
import { generateImage } from './ai-client';
import sharp from 'sharp'; // Image processing

const prompt = `
16-bit SNES pixel art character sprite, 32x32px,
Chrono Trigger style, 4-direction walk cycle,
[warrior/mage/archer], warm palette, dithered shadows
`;

const image = await generateImage(prompt);
const quantized = await sharp(image)
  .png({ palette: true, colors: 64 })
  .toBuffer();

// Apply dithering + export
```

---

### Day 10: Tiled Map Creation — The Crossroads
**Goal**: Design the first signature world

**Morning (4h): Design**
- Sketch: The Crossroads layout (paper wireframe)
- Define: Audio zones (plaza, inn, garden)
- Plan: Object placement (chairs, doors, decorations)
- Reference: Medieval town references (Google Images)

**Afternoon (4h): Build**
- Create: The Crossroads in Tiled (100×100 tiles)
- Paint: Terrain layers (grass, cobblestone, water)
- Add: Wall tiles (auto-tiling)
- Place: Objects (chairs, fountains, trees)
- Mark: Collision layer + audio zones (custom properties)

**Deliverable**: The Crossroads map (playable in Phaser)

**Resources**:
- Tiled documentation: https://doc.mapeditor.org/
- Free tilesets: https://opengameart.org/

---

### Day 11: Sprite Animation System
**Goal**: Smooth walk cycles with direction switching

**Morning (4h): Study**
- Read: Animation principles (12 principles of animation)
- Study: Phaser animation API
- Watch: Walk cycle breakdowns (YouTube)

**Afternoon (4h): Build**
- Implement: Sprite animation manager (Phaser)
- Add: 4-direction walk cycles (8 FPS)
- Create: Idle animations (breathing)
- Polish: Direction switching (instant vs blended)

**Deliverable**: Animated characters moving smoothly

**Resources**:
- Phaser animations: https://photonstorm.github.io/phaser3-docs/Phaser.Animations.html
- Walk cycle tutorial: https://blog.studiominiboss.com/pixelart

---

### Day 12: Interactive Objects & Sitting System
**Goal**: Click chairs to sit, visual state changes

**Morning (4h): Study**
- Review: Phaser input system (pointer events)
- Study: Object interaction patterns (hover, click)
- Research: State management (sitting, AFK, emoting)

**Afternoon (4h): Build**
- Implement: Object hover detection (glow outline)
- Add: Click handler (send interact command to server)
- Create: Sitting sprite poses (side view)
- Sync: Server broadcasts sitting state to all clients

**Deliverable**: Working chair interaction system

---

### Day 13: Emote System
**Goal**: Express emotions (wave, dance, laugh)

**Morning (4h): Design**
- Create: 6 emote icons (8×8px bubbles)
- Design: Emote wheel UI (radial menu)
- Plan: Animation timing (appear, hold, fade)

**Afternoon (4h): Build**
- Implement: Emote wheel (hold E to open)
- Add: Emote animations (scale up, fade out)
- Sync: Broadcast emotes to nearby players
- Polish: Particle effects (hearts, stars)

**Deliverable**: Emote system with 6 expressions

---

### Day 14: Mobile Touch Controls
**Goal**: Virtual joystick + gesture support

**Morning (4h): Study**
- Review: Phaser touch input examples
- Study: Virtual joystick libraries
- Research: Mobile game UX (Supercell games)

**Afternoon (4h): Build**
- Implement: Dynamic virtual joystick (spawns on touch)
- Add: Drag-to-move (angle + distance = velocity)
- Create: Touch-friendly UI (large buttons)
- Test: On real mobile device (iPhone/Android)

**Deliverable**: Mobile-playable version

**Resources**:
- Phaser virtual joystick: https://rexrainbow.github.io/phaser3-rex-notes/docs/site/virtualjoystick/

---

## Week 3: Integration & System Testing

### Day 15: Full System Integration
**Goal**: All systems working together

**All Day (8h): Build + Debug**
- Integrate: Phaser + WebSocket + Redis + Daily.co
- Connect: The Crossroads map with multiplayer + voice
- Add: All features (movement, voice, emotes, sitting)
- Test: 2-player session, verify everything works

**Deliverable**: End-to-end playable prototype

---

### Day 16-17: Performance Optimization
**Goal**: Locked 60 FPS with 50 concurrent users

**Day 16: Client-side**
- Profile: Chrome DevTools (identify bottlenecks)
- Optimize: Sprite culling (only render visible)
- Reduce: Draw calls (sprite batching)
- Tune: Garbage collection (object pooling)

**Day 17: Server-side**
- Load test: Simulate 100 concurrent users
- Optimize: Redis queries (pipeline commands)
- Reduce: WebSocket broadcast frequency (10 Hz → 20 Hz adaptive)
- Monitor: CPU/memory usage (stay under 50%)

**Deliverable**: Performance benchmarks (60 FPS, <100ms latency)

---

### Day 18: Mobile Optimization & Testing
**Goal**: Smooth experience on mobile devices

**Morning (4h): Optimize**
- Reduce: Asset sizes (compress sprites)
- Implement: Adaptive quality (lower res on mobile)
- Add: Touch latency optimization (<50ms)

**Afternoon (4h): Test**
- Test: On iPhone (Safari)
- Test: On Android (Chrome)
- Test: On tablet (landscape + portrait)
- Fix: Platform-specific bugs

**Deliverable**: Mobile-ready build

---

### Day 19: Admin Panel & Moderation Tools
**Goal**: Kick/mute controls for world hosts

**Morning (4h): Design**
- Plan: Admin UI (player list, controls)
- Design: Permission system (who can admin?)

**Afternoon (4h): Build**
- Implement: Player list UI (show all in world)
- Add: Kick button (disconnect player)
- Add: Mute button (disable voice for player)
- Sync: Broadcast moderation actions

**Deliverable**: Basic moderation tools

---

### Day 20: Deploy to Zo + Public Beta
**Goal**: Shareable link, live on the internet

**Morning (4h): Deploy**
- Build: Production bundle (minified, optimized)
- Deploy: Static assets to Zo site
- Register: Game server as Zo service
- Configure: Redis + Daily.co credentials

**Afternoon (4h): Test + Share**
- Test: Public URL (https://worlds.dioni.zo.computer)
- Invite: 10 beta testers
- Monitor: Logs (errors, performance)
- Collect: Feedback (Google Form)

**Deliverable**: Live public beta

---

## Week 4: Additional Worlds & Creation Tools

### Day 21-23: Build 4 More Worlds
**Day 21: Celestial Library**
- Design in Tiled (floating islands, lecture hall)
- Create custom tileset (marble, stars, magic)
- Add unique mechanics (broadcast audio in lecture hall)

**Day 22: Neon Shibuya**
- Design cyberpunk map (crossing, arcade, rooftop)
- Create neon tileset (LED signs, rain effects)
- Add animated billboards

**Day 23: Forest Cathedral + Airship Deck**
- Design forest map (sacred tree, meditation circle)
- Design airship map (deck, engine room, crow's nest)
- Create nature + steampunk tilesets

**Deliverable**: 5 total playable worlds

---

### Day 24-25: World Editor (Phase 1)
**Goal**: Users can create simple worlds

**Day 24: Tiled Web Integration**
- Research: Tiled web editor options
- Implement: Upload Tiled JSON to server
- Add: Validation (map size, collision layer)

**Day 25: World Gallery**
- Create: Gallery UI (browse public worlds)
- Implement: Publish workflow (make world public)
- Add: Search + filter (by theme, size)

**Deliverable**: User-generated world system

---

### Day 26: Custom Sprite Editor
**Goal**: Users can customize avatars

**Morning (4h): Design**
- Plan: Layered sprite system (base + hair + clothes)
- Create: Color palette selector
- Design: Preview UI (see changes live)

**Afternoon (4h): Build**
- Implement: Sprite layer editor
- Add: Color picker (swap palette)
- Export: Custom sprite sheet
- Save: User preferences (persist avatar)

**Deliverable**: Avatar customization tool

---

### Day 27: Analytics & Heatmaps
**Goal**: Understand where players gather

**Morning (4h): Design**
- Plan: Metrics to track (positions, voice zones, interactions)
- Design: Heatmap visualization (density map)

**Afternoon (4h): Build**
- Implement: Position logging (every 10s)
- Create: Heatmap generator (aggregate positions)
- Visualize: Overlay on map (show hotspots)
- Add: Dashboard (concurrent users, session duration)

**Deliverable**: Analytics dashboard

---

### Day 28-29: Accessibility & Inclusive Design
**Day 28: Visual Accessibility**
- Implement: Color blindness modes (3 types)
- Add: High contrast mode
- Ensure: WCAG AA compliance (color ratios)

**Day 29: Input Accessibility**
- Add: Keyboard-only navigation (no mouse required)
- Implement: Screen reader support (ARIA labels)
- Add: Configurable controls (rebind keys)

**Deliverable**: Accessible for diverse users

---

### Day 30: Polish, Documentation & Launch Prep
**Morning (4h): Polish**
- Fix: Top 10 bugs from beta feedback
- Add: Loading screen (branded, animated)
- Polish: UI animations (smooth transitions)
- Record: Demo video (30-second trailer)

**Afternoon (4h): Documentation**
- Write: User guide (how to join, interact)
- Create: FAQ (common questions)
- Document: API (for world creators)
- Prepare: Launch post (social media)

**Deliverable**: Production-ready launch

---

## Ongoing Skills (Post-Launch)

### Advanced Topics (Continuous Learning)
- **AI NPCs**: Procedural behavior trees
- **Voice effects**: Spatial reverb, occlusion
- **Procedural generation**: Infinite worlds
- **Blockchain integration**: NFT avatars, land ownership
- **VR support**: Spatial audio in 3D

### Community Building
- **Discord server**: Gather community
- **World creator program**: Showcase best creations
- **Regular events**: Weekly gatherings
- **Feedback loops**: Iterate based on user input

---

## Learning Resources Master List

### Books
- "Real-Time Collision Detection" by Christer Ericson
- "Multiplayer Game Programming" by Joshua Glazer
- "Game Programming Patterns" by Robert Nystrom

### Articles
- Gabriel Gambetta's Fast-Paced Multiplayer series
- Valve's Source networking documentation
- Phaser 3 official examples

### Videos
- GDC talks (game networking, audio, animation)
- MortMort pixel art tutorials
- Phaser 3 crash courses

### Communities
- Phaser Discord
- Pixel Art subreddit (r/PixelArt)
- Game Dev subreddit (r/gamedev)
- Daily.co developer community

### Tools
- Aseprite (pixel art editor)
- Tiled (map editor)
- TexturePacker (sprite atlas)
- Chrome DevTools (profiling)

---

## Success Metrics

By Day 30, you should have:
- ✅ 5 beautiful playable worlds
- ✅ 50+ character sprites
- ✅ Smooth 60 FPS performance
- ✅ Working proximity voice (50+ concurrent)
- ✅ Mobile support (touch controls)
- ✅ User-generated content tools
- ✅ Analytics dashboard
- ✅ 100+ beta testers
- ✅ Public launch ready

**Total skill acquisition**: 240 hours (30 days × 8 hours)

**Expected outcome**: Top 0.01% execution, magical multiplayer experience, passionate early community.

Let's build this, one day at a time.
