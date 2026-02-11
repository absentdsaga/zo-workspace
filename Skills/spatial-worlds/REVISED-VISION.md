# Spatial Worlds — REVISED VISION (Isometric)

**Date**: 2026-02-09  
**Status**: Planning → Implementation  
**Perspective Change**: Top-down → **Isometric/Tactical**

---

## What Changed

Based on user feedback showing FFT-style elevated square tiles, we're pivoting from top-down to **isometric tactical perspective**.

### Visual Style Pivot

**Before** (Day 1):
- Flat top-down view (like classic Zelda)
- 4-direction movement
- Simple Y-sorting
- 32×32px sprites on flat tiles

**After** (Now):
- **Isometric 45° elevated view** (like Final Fantasy Tactics)
- **8-direction movement** (N, NE, E, SE, S, SW, W, NW)
- **Complex depth sorting** (Y + elevation + object height)
- **48×64px sprites on elevated square platforms**
- **Multi-level terrain** (platforms, stairs, cliffs)

### Reference Image Analysis

User provided pixel art showing:
- Characters standing on **elevated grass platforms**
- **Square tiles with visible depth** (not diamond-shaped)
- **3-5 pixel vertical sides** showing elevation
- **Chunky Chrono Trigger-style characters**
- **Shadow cast on platform surface**

---

## New Technical Requirements

### 1. Isometric Rendering Engine
**Skill**: `phaser-iso-engine`

- Custom depth sorting algorithm (elevation × 10000 + Y × 100)
- 8-direction sprite system (32 total frames: 8 dirs × 4 walk frames)
- Multi-level collision detection
- Camera controller with elevation compensation

**Impact**: Entire rendering pipeline must be rewritten

### 2. Elevated Tile System
**Skill**: `isometric-world-builder`

- Square platforms (not diamonds)
- 4-16px vertical sides (elevation indicators)
- Multi-layer Tiled maps (ground, platform-1, platform-2, etc.)
- Stairs and ramps between levels

**Impact**: All world maps must use isometric tilesets

### 3. Character Sprites on Platforms
**Skill**: `isometric-sprite-gen`

- 48×64px total canvas (character + platform)
- Character: 32×48px (Chrono Trigger proportions)
- Platform: 32×20px (isometric square with depth)
- Shadow cast on platform surface

**Impact**: All sprite generation must include platform compositing

### 4. 3D Spatial Audio
**Skill**: `spatial-audio-zones`

- Elevation-aware proximity (different levels = quieter)
- Voice attenuation: distance + elevation penalty
- Acoustic zones tied to elevation (intimate rooftops, crowded plazas)

**Impact**: Voice zone calculation must account for Z-axis

### 5. Multiplayer State Sync
**Skill**: `multiplayer-sync-iso`

- Sync elevation in player state
- 8-direction movement commands
- Elevation-aware collision validation
- Pathfinding across multiple levels

**Impact**: WebSocket protocol must include elevation data

---

## Revised World Designs

### The Crossroads (Isometric Version)

**Elevation Levels**:
```
Level 3: Tower Overlook (observation point)
         |
Level 2: Inn Rooftop, Market Balconies (4-6 person zones)
         |
Level 1: Fountain Platform (raised centerpiece, 10-person zone)
         |
Level 0: Plaza Ground (main gathering, 30-person capacity)
```

**Spatial Strategy**:
- **Ground level**: Open, social, energetic
- **Level 1 (fountain)**: Focal point, visible from all sides
- **Level 2 (rooftops)**: Intimate, quieter, panoramic views
- **Level 3 (tower)**: Solo reflection, broadcasts to below

**Voice Zones**:
- Same level: 30-tile range, full volume
- 1 level apart: 30-tile range, -40% volume
- 2+ levels apart: 15-tile range, -70% volume

### Celestial Library (Floating Islands)

**Elevation Strategy**:
- Each island at different height (0-5 levels)
- Stone bridges connect platforms
- Main lecture hall: amphitheater with tiered seating
- Reading nooks: small isolated islands (1-2 levels above main)

**Acoustic Design**:
- Lecture hall: Broadcast mode (speaker → 100 audience)
- Reading nooks: Isolated (elevation + distance = privacy)
- Bridges: Transition zones (voice fades as you cross)

---

## Revised Asset Requirements

### Sprites (Isometric)
- **50 character sprites** (48×64px each)
  - 8 directions × 4 walk frames = 32 frames per character
  - Idle animation (2 frames)
  - Total: 34 frames × 50 characters = 1,700 sprites
  - Atlas size: ~850KB (compressed)

### Tilesets (Isometric)
- **Square platforms** (32×16px top face + depth)
  - Grass (4 elevation levels)
  - Stone (4 elevation levels)
  - Wood (4 elevation levels)
  - Water (animated, 1 level)
- **Stairs** (connecting levels)
- **Objects** (chairs, trees, doors on platforms)

### Maps (Tiled)
- **The Crossroads**: 50×50 tiles, 4 elevation levels
- **Celestial Library**: 60×60 tiles, 6 elevation levels
- **Neon Shibuya**: 70×70 tiles, 3 elevation levels
- **Forest Cathedral**: 50×50 tiles, 5 elevation levels
- **Airship Deck**: 40×60 tiles, 3 elevation levels

---

## Revised Development Roadmap

### Week 1: Isometric Foundation (REVISED)

**Day 1** ✅ (Completed - needs refactor)
- Built top-down prototype (will be replaced)

**Day 2** (NEW FOCUS)
- Implement isometric rendering engine
- Create first isometric sprite (warrior on grass platform)
- Build depth sorting system
- Test 100 sprites at 60 FPS

**Day 3**
- Build The Crossroads in Tiled (isometric)
- Integrate isometric tileset
- Implement multi-level collision
- Create 8-direction movement controller

**Day 4**
- Generate 10 character sprites (with platforms)
- Implement walk animations (8-dir)
- Add sprite depth sorting
- Profile performance (target: 60 FPS with 50 sprites)

**Day 5-7**
- WebSocket multiplayer (elevation sync)
- Client prediction (8-direction)
- Spatial audio zones (3D proximity)
- Deploy beta (shareable link)

### Week 2: Content & Polish

**Day 8-10**
- Generate 50 character sprites
- Build 4 more worlds (isometric)
- Implement stairs/elevation changes

**Day 11-14**
- Mobile touch controls (virtual joystick)
- Emote system
- Sitting interactions
- Admin panel

### Week 3: Creation Tools

**Day 15-17**
- World editor (Tiled integration)
- Sprite customization
- Public gallery

**Day 18-21**
- Analytics dashboard
- Accessibility features
- Performance optimization

---

## New Skill Ecosystem

### Core Skills Created

1. **`isometric-sprite-gen`** — Generate FFT-style sprites on platforms
2. **`isometric-world-builder`** — Design multi-level tactical worlds
3. **`phaser-iso-engine`** — Isometric rendering engine for Phaser 3
4. **`multiplayer-sync-iso`** — Real-time sync with elevation
5. **`spatial-audio-zones`** — 3D spatial audio with elevation
6. **`asset-pipeline-iso`** — Automated sprite/tileset generation
7. **`workflow-orchestrator`** — Coordinate all skills optimally
8. **`self-qa`** — Autonomous testing and feedback

### Skill Dependencies

```
workflow-orchestrator
  ├─ phaser-iso-engine (foundation)
  ├─ isometric-sprite-gen (art)
  ├─ asset-pipeline-iso (automation)
  ├─ isometric-world-builder (maps)
  ├─ multiplayer-sync-iso (networking)
  ├─ spatial-audio-zones (voice)
  └─ self-qa (quality gates)
```

---

## Critical Differences from Original Plan

### Rendering Complexity
**Before**: Simple Y-sorting  
**After**: Y + elevation + height sorting (10× more complex)

### Sprite Count
**Before**: 4 directions × 4 frames = 16 sprites  
**After**: 8 directions × 4 frames = 32 sprites (2× more)

### Collision System
**Before**: Single-layer tile collision  
**After**: Multi-level 3D pathfinding with stairs

### Asset Size
**Before**: 10-20KB per character  
**After**: 30-50KB per character (more frames + platform)

### Camera Complexity
**Before**: Simple follow  
**After**: Elevation-compensated follow with zoom

### Voice Proximity
**Before**: 2D distance only  
**After**: 3D distance (X, Y, Z)

---

## What We Gained

### 1. **Visual Drama**
Isometric elevation creates **verticality** and **depth**:
- Rooftops feel isolated and special
- Descending to plaza feels like entering energy
- Tower overlooks create "on stage" moments

### 2. **Acoustic Realism**
Elevation naturally creates **acoustic intimacy**:
- Elevated platforms = private zones
- Ground level = social energy
- Stairs = natural voice transitions

### 3. **Spatial Strategy**
Multi-level design enables **intentional gathering**:
- Conference halls: Tiered seating with broadcast
- Taverns: Ground floor crowds + balcony booths
- Gardens: Elevated privacy

### 4. **Richer Aesthetic**
FFT-style platforms are **gorgeous**:
- Grass tiles with visible earth sides
- Shadow play (characters cast on platforms)
- Depth perception (behind/in-front clarity)

---

## What We Lost (Trade-offs)

### 1. **Development Speed**
Isometric is **2-3× more complex** than top-down:
- More sprites to generate
- More complex rendering
- More sophisticated collision

**Mitigation**: Automated asset pipeline

### 2. **Performance Overhead**
Depth sorting every frame is **expensive**:
- Must optimize aggressively
- Spatial culling critical
- May need to limit concurrent sprites

**Mitigation**: Pre-compute depths, batch rendering

### 3. **Tiled Complexity**
Multi-level maps are **harder to design**:
- Must think in 3D
- Elevation transitions need planning
- More layers = more work

**Mitigation**: Templates and procedural generation

---

## Success Metrics (Revised)

### Technical
- ✅ 60 FPS with 50 isometric sprites
- ✅ <100ms multiplayer latency (elevation sync)
- ✅ Proper depth sorting (no Z-fighting)
- ✅ Smooth 8-direction movement

### Aesthetic
- ✅ "This looks like Chrono Trigger + FFT!"
- ✅ Platforms show clear elevation
- ✅ Shadows cast correctly
- ✅ Color palette matches CT (64 colors)

### Social
- ✅ Voice volume changes naturally with elevation
- ✅ Rooftops feel intimate
- ✅ Plazas feel energetic
- ✅ 50-100 concurrent users per world

---

## Next Steps (Immediate)

### 1. Refactor Day 1 Work
- ❌ Scrap top-down rendering
- ✅ Implement isometric engine
- ✅ Replace placeholder sprites with platforms

### 2. Generate First Real Assets
- ✅ Create warrior sprite (48×64px, on grass platform)
- ✅ Generate isometric grass tileset
- ✅ Build small test world (10×10 tiles, 2 levels)

### 3. Validate Technical Approach
- ✅ Verify depth sorting works
- ✅ Test 8-direction movement
- ✅ Measure FPS with 50 sprites

### 4. Get User Feedback
- ✅ Deploy isometric demo
- ✅ Share with user
- ✅ Confirm visual direction

---

## Conclusion

The pivot to **isometric elevated square tiles** is the **right decision**. It:
- Matches user's vision (FFT reference)
- Creates more engaging spatial design
- Enables richer acoustic zones
- Looks dramatically better

The trade-off is **increased complexity**, but the new skill ecosystem handles it:
- Automated sprite generation
- Workflow orchestration
- Quality gates at each step

**We're building something magical.**

---

*Updated: 2026-02-09*  
*Skills Created: 8*  
*Ready to Execute: Yes*
