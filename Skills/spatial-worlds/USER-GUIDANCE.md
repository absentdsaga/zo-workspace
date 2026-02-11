# User Requirements — Spatial Worlds

**Source**: User feedback and guidance from conversation  
**Last Updated**: 2026-02-09

---

## 🎯 Primary User Requirements

### Visual Style (CRITICAL)
- [ ] **Final Fantasy Tactics camera angle** — 45° isometric view
- [x] **Square tiles on map** like FFT (visible as elevated platforms)
- [ ] **Chrono Trigger-style sprites** — pixel art, high quality
- [x] **48×64px sprite dimensions** (32×48 character + 32×20 platform)
- [ ] **Chrono Trigger color palette** — max 64 colors, SNES aesthetic
- [x] **Visible grass platform sides** — showing depth/elevation

### Isometric World (CRITICAL)
- [x] **Isometric rendering** — diamond tiles at 45° angle
- [x] **Multi-level platforms** — elevation levels 0, 1, 2, 3+
- [x] **Depth sorting** — sprites render in correct order based on Y + elevation
- [x] **8-direction movement** — not 4-direction top-down
- [x] **Elevated square platforms** — characters stand ON platforms, not diamonds

### Performance (REQUIRED)
- [ ] **60 FPS target** — must maintain smooth frame rate
- [x] **50+ NPC stress test** — verify performance with many sprites
- [x] **No loading screen stuck** — game must load fully
- [x] **No JavaScript errors** — clean console

### Multiplayer (PLANNED)
- [ ] **Proximity voice chat** — spatial audio based on character distance
- [ ] **WebSocket multiplayer** — real-time sync
- [ ] **Multiple players** — visible in same world
- [ ] **Daily.co integration** — for spatial audio

### User Feedback Integration (CRITICAL RULE)
- [x] **Always check your work** — verify in browser BEFORE claiming done
- [x] **Never say "this should work"** — test it first
- [x] **Fix issues immediately** — don't deliver broken code
- [x] **Pre-flight validation** — run checks before delivery

---

## 📝 Specific User Quotes

> "i want the world to have square tiles on the map like final fantasy tactics and the camera angle is good and sprites like this but much better quality and more chrono trigger style"

**Requirements extracted:**
- ✅ Square tiles (implemented as elevated platforms)
- ✅ FFT camera angle (45° isometric)
- ⚠️ Better quality sprites (using procedural, need hand-drawn)
- ⚠️ Chrono Trigger style (dimensions correct, palette needs work)

---

> "its stuck on loading did you check your work, always check your work"

**Requirements extracted:**
- ✅ Loading must complete successfully
- ✅ ALWAYS verify before claiming done
- ✅ Test in browser, not assumptions
- ✅ Pre-flight checks mandatory

---

> "stuck loading"

**Requirements extracted:**
- ✅ Fixed: Server must serve /assets/
- ✅ Fixed: TypeScript must compile to JS for browser
- ✅ Build process required before deployment

---

## 🎨 Art Requirements (From User Vision)

### Sprite Specifications
- **Dimensions**: 48×64px total
  - Character: 32×48px (upper portion)
  - Platform: 32×20px (lower portion, grass with earth sides)
- **Style**: Chrono Trigger pixel art
  - Clean pixels, no blur
  - Limited color palette (64 colors max)
  - SNES-era aesthetic
  - Hand-drawn quality
- **Animations** (future):
  - 8 directions × 4 frames = 32 sprites per character
  - Walk cycles for all directions
  - Idle animation

### World Design
- **The Crossroads** (signature world):
  - 50×50 tile map (manageable size)
  - 4 elevation levels clearly visible
  - Tiled map integration
  - Collision layer
  - Spawn points marked
- **Color Coding** (current implementation):
  - Green NPCs = Level 0 (ground)
  - Blue NPCs = Level 1 (elevated 20px)
  - Orange NPCs = Level 2 (elevated 40px)
  - Pink NPCs = Level 3 (elevated 60px)

---

## ⚡ Performance Targets

- **FPS**: 60 (locked, no drops)
- **Load Time**: <3 seconds
- **Sprite Count**: 50+ NPCs without performance loss
- **Memory**: <100MB browser usage
- **Input Lag**: <16ms (sub-frame)

---

## 🔧 Technical Requirements

### Must Have
- [x] Bun runtime for server
- [x] TypeScript compilation with DOM types
- [x] Phaser 3 game engine
- [x] WebGL renderer
- [x] Hot reload for development
- [x] Build pipeline (TS → JS)
- [x] Static file serving (/assets/, /dist/)

### Should Have
- [ ] Tiled map editor integration
- [ ] Sprite animation system
- [ ] Collision detection
- [ ] WebSocket server
- [ ] Spatial audio system

### Nice to Have
- [ ] Mobile touch controls
- [ ] Debug overlay toggle
- [ ] Camera zoom controls
- [ ] Settings UI

---

## 🚫 Anti-Requirements (Don't Do This)

- ❌ **Don't claim something works without testing it**
- ❌ **Don't use top-down view** (must be isometric)
- ❌ **Don't use 4-direction movement** (must be 8-direction)
- ❌ **Don't render diamond ground tiles only** (need elevated platforms)
- ❌ **Don't skip the build step** (browser needs compiled JS)
- ❌ **Don't forget to serve assets** (common failure point)
- ❌ **Don't deliver with console errors**
- ❌ **Don't use low-quality procedural art** as final (placeholder only)

---

## ✅ Definition of Done

A task is ONLY complete when:

1. ✅ **Pre-flight checks pass** (TypeScript, build, artifacts, server)
2. ✅ **Spec validator passes** (requirements met)
3. ✅ **Browser test succeeds** (loads, no errors, works as expected)
4. ✅ **Performance verified** (FPS measured, targets met)
5. ✅ **User requirements satisfied** (matches this spec)
6. ✅ **QA report generated** (documented what works/doesn't)

---

## 📊 Success Metrics

### Current Status (Day 2)
- ✅ Isometric rendering working
- ✅ Multi-level platforms (4 levels)
- ✅ Depth sorting functional
- ✅ 8-direction movement
- ✅ 51 sprites rendering
- ⚠️ FPS at 27 (target: 60)
- ⚠️ Placeholder sprites (need Chrono Trigger quality)
- ❌ No animations
- ❌ No multiplayer
- ❌ No spatial audio

### Next Milestones
1. **Day 3**: Hand-drawn Chrono Trigger sprite, 60 FPS, collision
2. **Day 5**: Walk animations, The Crossroads map
3. **Day 7**: WebSocket multiplayer
4. **Day 10**: Proximity voice chat working

---

## 🎓 Lessons Learned

### From User Feedback
1. **Always test before claiming done** — caught loading failures twice
2. **Fix TypeScript errors** — pre-flight catches them now
3. **Verify in browser** — don't assume it works
4. **Check build output** — make sure files exist
5. **Serve assets properly** — common failure point

### Patterns to Remember
- User says "stuck loading" = check server routes + build output
- User says "check your work" = run pre-flight + browser test
- User provides image = this is the EXACT style they want
- User says "better quality" = current quality insufficient

---

## 🔄 Continuous Validation

**Before every delivery:**
```bash
# 1. Pre-flight technical checks
/home/workspace/Skills/continuous-monitor/scripts/pre-flight.sh $(pwd)

# 2. Spec validation against this file
/home/workspace/Skills/continuous-monitor/scripts/spec-validator.sh $(pwd)

# 3. Browser verification
# Open https://spatial-worlds-dioni.zocomputer.io
# Test movement, check console, verify FPS

# 4. Only then: tell user it's done
```

---

*This document captures the user's exact requirements and feedback. Update it when new guidance is provided.*
