# Spatial Worlds — Art Direction Guide

## Core Aesthetic: "Chrono Trigger Warmth"

The visual language of Chrono Trigger transcends technical constraints. It's about:
- **Emotional resonance** through color
- **Clarity** through composition
- **Life** through subtle animation
- **Discovery** through hidden details

Every pixel serves emotion first, function second.

---

## Color Theory Deep Dive

### The Chrono Trigger Palette Philosophy

**SNES Color Limitations as Strength:**
- 256 colors max on-screen
- Forces intentional palette curation
- Creates visual harmony (everything shares a color family)

**Our Approach:**
1. Define 8 master palettes (one per world theme)
2. Each palette: 64 colors maximum
3. Strict adherence prevents visual chaos

### Master Palette Construction

**Medieval (The Crossroads)**
```
Warm earth tones (golden hour sunset)

Shadows: #2C1810, #4A2818, #6B3820
Browns: #8B4A28, #A85A30, #C67240
Tans: #D99160, #E8B088, #F4D0A0
Greens: #3A5A2F, #5A7A4F, #7A9A6F, #9ABA8F
Blues (water/sky): #4A6A8A, #6A8AAA, #8AAACA
Accents: #CA4540 (red), #E8B040 (gold), #8A5AC0 (purple)
Highlights: #FFFFFF (sparingly!)
```

**Magical (Celestial Library)**
```
Cool mystical tones (eternal twilight)

Deep purples: #1A1A3A, #2A2A5A, #3A3A7A
Royal purples: #5A4A9A, #7A6ABA, #9A8ADA
Golds: #8A6A2A, #AA8A4A, #CA9A6A, #EAC090
Whites: #CACAEA, #DADADF, #EAEAEF, #FAFAFF
Stars: #FFFFAA (bright yellow)
Magic glow: #AA88FF, #CC99FF
```

**Cyberpunk (Neon Shibuya)**
```
Neon contrast (night city)

Darks: #0A0A0A, #1A1A1A, #2A2A2A
Concrete: #4A4A4A, #6A6A6A, #8A8A8A
Neon pink: #FF2A8A, #FF5AAA, #FF8ACA
Neon cyan: #2AFFFF, #5AFFFF, #8AFFFF
Neon purple: #AA2AFF, #CA5AFF, #EA8AFF
Accents: #FFFF2A (yellow signs)
```

### Dithering Patterns

**When to use:**
- Gradients (sky, water, shadows)
- Texture (stone, wood grain)
- Lighting effects (glow, fire)

**Checkerboard (most common):**
```
A B A B
B A B A
A B A B
B A B A
```

**Bayer 4x4 (smooth gradients):**
```
 0  8  2 10
12  4 14  6
 3 11  1  9
15  7 13  5
```
(Numbers represent opacity/color blend order)

**Organic (for nature):**
Random scatter of pixels (avoid patterns)

---

## Tile Design Principles

### Ground Tiles

**The 3x3 No-Repeat Rule:**
Look at any 3x3 grid of tiles. If the same tile appears twice, redesign.

**Why**: Human eye detects patterns instantly. Repetition = artificial.

**Solution**: Create 16+ variations per terrain type
- Grass: light, medium, dark, with flowers, with pebbles, etc.
- Stone: smooth, cracked, mossy, worn, etc.

**Edge Blending:**
When two terrain types meet, create transition tiles.

Example: Grass → Stone
```
[Grass] [75% Grass, 25% Stone] [50/50] [25% Grass, 75% Stone] [Stone]
```

Requires 16 tiles per terrain pair (4 edges × 4 corners).

### Wall Tiles

**Auto-Tiling Template (48 tiles):**
Every possible edge/corner combination for seamless walls.

```
┌─────┬─────┬─────┐
│ ┌─┐ │  ┬  │ ┌─┐ │  (and 45 more variations)
│ └─┘ │  ┴  │ └─┘ │
└─────┴─────┴─────┘
```

**Lighting Consistency:**
- Top surfaces: +30% brightness (sunlight)
- Front faces: Base color
- Side faces: -20% brightness (shade)

**Depth Cues:**
- Minimum 2 tiles tall (player can walk behind)
- Cast shadows on ground (45° angle, 50% opacity)

### Animated Tiles

**Frame Count:**
- Water: 4 frames (ripple cycle)
- Fire: 6 frames (flicker)
- Flags: 3 frames (wave)
- Grass sway: 2 frames (subtle)

**Timing:**
- Water: 4 FPS (smooth flow)
- Fire: 8 FPS (energetic)
- Flags: 3 FPS (lazy wave)
- Grass: 1 FPS (gentle)

**Offset Strategy:**
Don't sync all animations. Stagger start frames for organic feel.

---

## Sprite Design

### Character Proportions (The Chrono Trigger Formula)

**32×32px Canvas:**
- 8px buffer (top/sides) for animation overflow
- 24×24px usable space

**Body Ratios (2.5 heads tall):**
```
Head:  10px  (40%)
Body:   8px  (32%) 
Legs:   6px  (28%)
```

**Why chibi?** Maximizes readability at small size. Emotional expressiveness.

### Walk Cycle Anatomy

**4 Directions × 4 Frames = 16 sprites per character**

**Down (facing camera):**
```
Frame 1: Left foot forward, body tilts left
Frame 2: Center stance, both feet together
Frame 3: Right foot forward, body tilts right
Frame 4: Center stance (mirror of frame 2)
```

**Up (facing away):**
(Same pattern, show back of head/body)

**Left/Right (profile):**
```
Frame 1: Far leg forward
Frame 2: Passing pose (feet together)
Frame 3: Near leg forward
Frame 4: Passing pose (mirror)
```

**Timing:** 8 FPS (looping)

**Polish Details:**
- Head bob (2px up/down with stride)
- Arms swing (opposite leg)
- Hair/clothing sway (1 frame delay)

### Sitting Pose

**Side View Only:**
- Legs bent 90°
- Hands in lap or on armrests
- Slight lean back (relaxed)
- Optional: Idle animation (breathing, 0.5 FPS)

**No front/back sitting sprites** (saves memory, rarely needed)

### Emote Overlays (8×8px)

**Bubble Shapes:**
- Round (speech)
- Heart (love)
- Exclamation (surprise)
- Question (confusion)
- Music note (dance)
- Zzz (sleep)

**Animation:**
1. Appear (scale from 0 → 1, 0.2s)
2. Hold (scale 1, 1s)
3. Fade (opacity 1 → 0, 0.3s)

**Position:** 10px above sprite head

---

## Lighting & Atmosphere

### Light Source Consistency

**Global Rule:** Light always from top-left

**Per-Pixel Shading:**
- Top-left pixels: Highlight color (+20% brightness)
- Bottom-right pixels: Shadow color (-40% brightness, shift toward blue)

**Why blue shadows?** Human perception (warm light = cool shadows)

### Time of Day Palettes

**The Crossroads (Dynamic):**

**Sunrise (6am):**
- Sky: Orange → Pink gradient
- Shadows: Long (6:1 ratio)
- Ambient: Warm (+10% red channel)

**Noon (12pm):**
- Sky: Bright blue
- Shadows: Short (1:1 ratio)
- Ambient: Neutral (true colors)

**Sunset (6pm):**
- Sky: Purple → Orange gradient
- Shadows: Long (6:1 ratio)
- Ambient: Warm (+15% orange)

**Night (12am):**
- Sky: Deep blue-black
- Shadows: Invisible (merge with ground)
- Ambient: Cool (-20% brightness, +10% blue)
- Lights: Torches glow (additive blending)

**Implementation:**
- Palette swap (4 palettes per world)
- Transition over 5 minutes (imperceptible)

### Weather Effects

**Rain (particle system):**
- 100 particles
- Velocity: (2, 10) pixels/frame
- Opacity: 30-60%
- Length: 3-5 pixels
- Color: Light blue (#AACCFF)

**Snow:**
- 50 particles
- Velocity: (0.5, 2) pixels/frame
- Sway: sin(time) * 2 pixels
- Opacity: 50-80%
- Size: 2×2 pixels

**Fog (overlay):**
- Perlin noise texture
- Scroll speed: 0.1 pixels/frame
- Opacity: 20-40%
- Color: Match sky

---

## Environmental Details

### Layering Depth (Parallax)

**5 Layers (back to front):**

1. **Sky (0.2× scroll speed)**
   - Clouds, stars, gradient

2. **Background mountains/buildings (0.5×)**
   - Distant scenery, low detail

3. **Midground (1.0×) [MAIN LAYER]**
   - Terrain, walls, most objects
   - Collision layer

4. **Foreground objects (1.0×)**
   - Trees, pillars (player walks behind)

5. **Overhead (1.2×)**
   - Leaves, awnings (cast shadows on player)

**Depth Sorting:**
- Sort sprites by Y position each frame
- Objects with higher Y render in front

### Animation Philosophy

**Not Everything Moves:**
Motion hierarchy prevents visual overload.

**Always animate:**
- Player sprites
- NPCs (if any)
- Critical objects (fire, water)

**Animate frequently:**
- Flags, curtains, grass (wind)
- Torches, lanterns (light sources)

**Animate occasionally:**
- Tree sway (breeze)
- Cloud drift (sky)

**Animate rarely:**
- Day/night cycle (5 min)
- Seasonal changes (special events)

### Interactive Object Visual Language

**Chairs (sit):**
- Highlight glow when hover (2px, #FFFF00, pulse)
- Darker when occupied (someone sitting)

**Doors (enter):**
- Slight shadow recess (depth cue)
- Light glow from interior (if open)

**Levers/Switches (toggle):**
- Up position = off (shadow below)
- Down position = on (highlight above)

**Books/Signs (read):**
- Hover glow + cursor change
- Page flip animation on interact

---

## World-Specific Art Direction

### The Crossroads (Cozy Medieval)

**Reference Feeling:** Ghibli's Howl's Moving Castle (market scene)

**Key Elements:**
- Warm wood tones (thatched roofs, timber beams)
- Cobblestone streets (hand-laid, irregular)
- Hanging lanterns (orange glow, swaying)
- Flower pots, vines, nature reclaiming
- Smoke from chimneys (particle effect)

**Color Mood:** Golden hour warmth, inviting

**Focal Point:** Central fountain (animated water, gathering spot)

### Celestial Library (Ethereal Wisdom)

**Reference Feeling:** Final Fantasy VI's floating continent

**Key Elements:**
- White marble (clean lines, elegant)
- Floating islands (connected by stone bridges)
- Purple starry void (deep space)
- Glowing books (magical light sources)
- Chandeliers (crystal, prismatic)

**Color Mood:** Cool mystical, inspiring awe

**Focal Point:** Grand statue (knowledge deity, emanating light)

### Neon Shibuya (Retro-Future Energy)

**Reference Feeling:** Akira, Blade Runner, Jet Set Radio

**Key Elements:**
- Dark streets (rain-slicked, reflective)
- LED billboards (cycling ads, kanji text)
- Vending machines (glowing products)
- Alleyway neon (pink, cyan, purple)
- Crowds implied (NPC silhouettes)

**Color Mood:** High contrast, electric, youthful

**Focal Point:** Massive crossing (intersection, all paths converge)

### Forest Cathedral (Spiritual Tranquility)

**Reference Feeling:** Princess Mononoke's forest spirits

**Key Elements:**
- Ancient tree (gnarled roots, massive canopy)
- Bioluminescent flora (mushrooms, flowers)
- Mist particles (volumetric fog)
- Stone ruins (overgrown, mystical)
- Wildlife (deer, birds, ambient)

**Color Mood:** Earthy greens with magical blue-purple accents

**Focal Point:** Sacred tree (center, draws all attention)

### Airship Deck (Adventurous Wonder)

**Reference Feeling:** Castle in the Sky, Treasure Planet

**Key Elements:**
- Brass railings (polished, ornate)
- Wood planks (riveted, worn)
- Spinning propellers (motion blur)
- Billowing clouds (rushing past)
- Steam vents (particle puffs)

**Color Mood:** Bright optimistic, sense of motion

**Focal Point:** Ship's wheel (steering, command)

---

## Technical Asset Specs

### Tileset Export Settings

**Format:** PNG (indexed color, 8-bit)
**Tile Size:** 32×32 pixels
**Spacing:** 0 pixels (no borders)
**Margin:** 0 pixels
**Transparency:** Yes (magic pink #FF00FF = transparent)

**File Naming:**
```
medieval-ground.png
medieval-walls.png
medieval-objects.png
medieval-animated.png (with .json metadata)
```

### Sprite Sheet Format

**Layout:** Grid (4 rows × 4 columns)
```
Row 1: Down walk (frames 1-4)
Row 2: Up walk (frames 1-4)
Row 3: Left walk (frames 1-4)
Row 4: Right walk (frames 1-4)
```

**Metadata JSON:**
```json
{
  "frames": {
    "down": [0, 1, 2, 3],
    "up": [4, 5, 6, 7],
    "left": [8, 9, 10, 11],
    "right": [12, 13, 14, 15]
  },
  "frameWidth": 32,
  "frameHeight": 32,
  "fps": 8
}
```

### Optimization Pipeline

1. **Draw in Aseprite** (or Photoshop with indexed color)
2. **Export sprite sheet** (32×128 PNG)
3. **Run optimizer:**
   ```bash
   pngquant --quality=80-100 input.png -o output.png
   ```
4. **Generate atlas** (combine multiple sprites):
   ```bash
   bun run scripts/pack-atlas.ts sprites/ output-atlas.png
   ```

**Target sizes:**
- Single sprite sheet: <5 KB
- Full tileset: <50 KB
- Complete world assets: <500 KB

---

## Quality Checklist

Before shipping any art asset:

- [ ] Follows color palette (no rogue colors)
- [ ] Dithering used consistently
- [ ] Lighting from top-left (all highlights/shadows match)
- [ ] Readable at 1× zoom (no squinting)
- [ ] Animations loop seamlessly
- [ ] Transparent pixels are magic pink (#FF00FF)
- [ ] File size optimized (PNG crushed)
- [ ] Named correctly (kebab-case)
- [ ] Tested in-game (not just in editor)

---

## Inspirational Reference Library

### Games to Study:
1. **Chrono Trigger** (SNES) — Gold standard
2. **Final Fantasy VI** (SNES) — Epic scale
3. **Secret of Mana** (SNES) — Vibrant colors
4. **Stardew Valley** (Modern) — Cozy warmth
5. **Hyper Light Drifter** (Modern) — Atmospheric depth

### Pixel Artists to Follow:
- **MortMort** (YouTube tutorials)
- **Brandon James Greer** (sprite animations)
- **Waneella** (cyberpunk scenes)
- **1041uuu** (cozy interiors)

### Animation References:
- **Studio Ghibli films** (backgrounds, lighting)
- **Vlambeer's "Art of Screenshake"** (game feel)
- **Pixel Art Tutorials** (lospec.com/articles)

---

## The Golden Rule

**Beauty serves connection.**

Every color choice, every animated tile, every lighting decision asks:
"Does this help people feel present, together, alive?"

If the answer is no, simplify. Cut. Refine.

The pixels are a stage. The players are the show.
