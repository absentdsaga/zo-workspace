# Visual Specification — Spatial Worlds

**What a human SHOULD see when the game loads**

---

## ✅ Expected Visual Elements

### 1. Ground Layer (CRITICAL)
- [ ] **15×15 grid of diamond-shaped tiles** visible
- [ ] **Green color** (#4a6a3f)
- [ ] **Isometric perspective** (diamonds, not squares)
- [ ] **Grid centered** in viewport
- [ ] **Outlines visible** (should see individual tile borders)

**If NOT visible:** Ground rendering failed - major issue

### 2. Elevated Platforms (CRITICAL)
- [ ] **8 platform blocks** visible at different positions
- [ ] **3D effect** - can see grass top + brown earth sides
- [ ] **Different heights** - some higher than others
- [ ] **Colors vary** by level:
  - Level 1: Lighter green (#6a8a5f)
  - Level 2: Medium green (#8aaa7f)
  - Level 3: Bright green (#9aba8f)

**If NOT visible:** Platform rendering failed - major issue

### 3. Character Sprites (MUST HAVE)
- [ ] **51 sprites total** (1 player + 50 NPCs)
- [ ] **Color-coded by elevation:**
  - Green tint = Ground level (L0)
  - Blue tint = Platform 1 (L1)
  - Orange tint = Platform 2 (L2)
  - Pink tint = Platform 3 (L3)
- [ ] **Sprites moving** (NPCs bouncing around)
- [ ] **Player sprite** larger or distinct

**If NOT visible:** Sprite rendering failed

### 4. Depth Sorting (VISUAL QUALITY)
- [ ] **Sprites overlap correctly** (closer ones in front)
- [ ] **No z-fighting** or visual glitches
- [ ] **Platforms appear "elevated"** above ground

### 5. UI Elements
- [ ] **Debug overlay** (top-left corner):
  - FPS counter visible
  - Sprite count: 51
  - Position coordinates
- [ ] **Instruction box** (bottom-right):
  - Blue background
  - Text readable
  - Shows controls and elevation legend

---

## ❌ What You Should NOT See

- ❌ **Solid black screen** (nothing rendering)
- ❌ **Only sprites, no ground** (ground off-screen or not rendering)
- ❌ **Sprites floating in void** (no context/environment)
- ❌ **White/broken textures** (asset loading failed)
- ❌ **Stuck loading screen** (game didn't start)

---

## 🎯 Visual Success Criteria

**PASS if:**
✅ Can clearly see isometric diamond grid
✅ Can clearly see elevated platforms with 3D sides
✅ Can see 51 colored sprites
✅ Sprites appear to stand ON the ground/platforms
✅ Everything is positioned correctly in viewport

**FAIL if:**
❌ Black background with just floating sprites
❌ No grid visible
❌ No platforms visible
❌ Elements off-screen or invisible
❌ User says "I don't see what you described"

---

## 📸 Reference Screenshot Expectations

**When working correctly, screenshot should show:**

```
┌─────────────────────────────────────────────────────────┐
│ FPS: 60  Sprites: 51  Position: 400, 300 [L0]          │ Debug overlay
│                                                         │
│          ◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇                              │
│         ◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇                              │ Diamond grid
│        ◇◇◇◇🟩🟩◇◇◇◇◇◇◇◇◇◇                              │ visible!
│       ◇◇◇◇🟩🟩◇◇◆◆◇◇◇◇◇◇                              │
│      ◇◇◇🔵🟩◇◇◇◆◆◇🟢◇◇◇◇                              │ Elevated
│     ◇◇◇◇◇◇🟢◇◇◇🟠🟢◇◇◇◇                              │ platforms
│    ◇◇◆◆◇🟢🟢◇◇🟠◇◇◇◇◇                               │
│   ◇◇◆◆◇◇🟢◇🟣◇◇◇◇◇                                │
│  ◇◇◇◇◇◇◇◇◇◇◇◇◇                                   │
│                                                         │
│                    🎮 Isometric Prototype               │ Info box
│                    • 8-direction movement               │
│                    • Green=L0  Blue=L1                  │
└─────────────────────────────────────────────────────────┘

Legend:
◇ = Diamond tile (ground)
🟩 = Grass platform (elevated)
◆ = Platform shadow/side
🟢🔵🟠🟣 = Colored sprites at different elevations
```

---

## 🚨 Current Status (User Reported)

**User's screenshot shows:**
- ❌ BLACK background
- ❌ NO grid visible
- ❌ NO platforms visible  
- ✅ Colored squares (sprites) visible
- ✅ UI text visible

**VERDICT:** ❌ **VISUAL VERIFICATION FAILED**

**Issue:** Ground and platforms not rendering or rendering off-screen.

**Action Required:** Fix rendering before claiming completion.

---

*Last updated: 2026-02-09*
*Based on user screenshot feedback*
