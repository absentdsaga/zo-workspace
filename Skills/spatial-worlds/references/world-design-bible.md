# Spatial Worlds Design Bible

## The Golden Rules

### 1. Every Pixel Serves the Social Graph
Beautiful worlds are useless if they don't facilitate connection. Design FOR gathering:
- Wide spaces encourage crowds (markets, plazas)
- Narrow spaces create intimacy (corridors, alcoves)
- Elevated areas signal importance (stages, podiums)
- Circular arrangements promote equity (campfires, round tables)

### 2. Audio-First Architecture
Voice is the killer feature. Map topology IS audio topology:
- **Barriers**: Walls block line-of-sight AND muffle audio (-20dB)
- **Reverb zones**: Cathedrals echo, forests dampen
- **Distance curves**: Exponential falloff (realistic) vs linear (game-feel)
- **Max range**: 15 tiles = intimate, 30 tiles = public, 50 tiles = amphitheater

### 3. Readability > Realism
Chrono Trigger's genius: you always know where you can walk
- **Contrast**: Walkable areas are 20%+ brighter than walls
- **Shadows**: Cast at 45° angle, consistent light source
- **Edges**: 1px dark outline on all collision objects
- **Depth cues**: Parallax layers, foreground blur

### 4. Animation Hierarchy
Not everything moves at once (causes visual noise):
- **Layer 1 (Always)**: Player sprites, key NPCs
- **Layer 2 (Frequent)**: Water, fire, flags (2-4 FPS)
- **Layer 3 (Occasional)**: Trees sway, clouds drift (0.5-1 FPS)
- **Layer 4 (Rare)**: Day/night cycle, weather events

### 5. Color Psychology
Palette choice shapes social behavior:
- **Warm tones** (oranges, yellows) → Energizing, conversational (taverns, markets)
- **Cool tones** (blues, purples) → Calming, focused (libraries, temples)
- **Saturated** → Playful, casual (festivals, game rooms)
- **Desaturated** → Serious, professional (conference halls, offices)

---

## Signature World Designs

### The Crossroads (Default Spawn)

**Concept**: Medieval fantasy hub. First impression must be WOW.

**Layout**:
```
        [Mountain Path]
              |
    [Forest]--[Plaza]--[Desert Road]
              |
         [Seaside Docks]
```

**Zones**:
- **Central Plaza** (40x40 tiles): Fountain centerpiece, radial benches, quest board, 30-person capacity
- **The Tipsy Griffin Inn** (interior): Fireplace, booths (4-person), bar (8-person), bard stage
- **Market Street**: 8 vendor stalls, Browse-and-chat traffic flow
- **Secret Garden**: Hidden behind inn, 6-person capacity, romantic lighting
- **Rooftop Overlook**: Climb ladder from plaza, 10-person chill zone with view

**Audio Zones**:
- Plaza: 30-tile range, slight reverb
- Inn interior: 20-tile range, warm reverb, muffled exterior
- Garden: 12-tile range, bird ambiance, high privacy

**Aesthetic**:
- Time: Golden hour (warm sunset palette)
- Color: Earth tones (browns, greens) with accent blues (water, sky)
- Animation: Fountain spray, torch flicker, flag ripple, NPC shopkeepers
- Secrets: Black cat NPC that walks random paths, glowing mushrooms in garden

---

### Celestial Library (Conference Mode)

**Concept**: Floating knowledge temple. Perfect for talks, panels, workshops.

**Layout**:
```
    [Reading Nook] [Reading Nook] [Reading Nook]
           \            |            /
            \      [Main Atrium]    /
             \          |          /
              [Lecture Hall (100-seat)]
                     |
              [Workshop Pods (x6)]
```

**Zones**:
- **Main Atrium** (60x60 tiles): Circular, statue centerpiece, 8 bridges to outer islands
- **Lecture Hall**: Tiered seating (5 rows), stage with podium, 100-person capacity, broadcast audio mode
- **Reading Nooks** (x8): 4-person alcoves, bookshelves, cozy chairs
- **Workshop Pods** (x6): 12-person circular rooms, whiteboard objects (clickable)

**Audio Zones**:
- Lecture Hall: Stage has 50-tile broadcast range, audience 15-tile peer range
- Workshop Pods: 15-tile range, soundproof walls (no bleed)
- Atrium: 25-tile range, echo effect

**Aesthetic**:
- Time: Eternal twilight (deep blue sky, stars)
- Color: Purples, golds, whites (magical, scholarly)
- Animation: Floating books, star twinkle, slow cloud drift, chandelier sway
- Secrets: Hidden star constellations spell out messages when players stand on glyphs

---

### Neon Shibuya (Cyberpunk Social)

**Concept**: Retro-future Tokyo crossing. High energy, youth culture.

**Layout**:
```
    [Arcade]--[Crossing]--[Ramen Alley]
                  |
            [Rooftop Bar]
                  |
          [Underground Club]
```

**Zones**:
- **Shibuya Crossing** (50x50 tiles): Massive intersection, neon signs, 40-person capacity
- **Arcade**: Playable cabinets (minigames), 16-person capacity
- **Ramen Alley**: 6 counter seats per stall (24 total), intimate side-by-side chat
- **Rooftop Bar**: City skyline view, lounge furniture, 20-person capacity
- **Underground Club**: Dance floor, DJ booth, strobing lights, 50-person capacity

**Audio Zones**:
- Crossing: 35-tile range, city ambiance (traffic, chatter)
- Club: 25-tile range, bass-boosted, music overlay option
- Ramen Alley: 10-tile range, close conversations

**Aesthetic**:
- Time: Night (always)
- Color: Neon pinks, cyans, purples against dark backgrounds
- Animation: LED billboards cycle ads, traffic lights, rain effect, smoke vents
- Secrets: Glitch effects when players stand in specific spots, hidden vending machines

---

### Forest Cathedral (Meditation Space)

**Concept**: Ancient grove. Tranquil, spiritual, nature-focused.

**Layout**:
```
        [Canopy Platforms]
              |
    [Stream]--[Sacred Tree]--[Meditation Circle]
              |
         [Cave Shrine]
```

**Zones**:
- **Sacred Tree** (massive centerpiece): 50x50 tile trunk, spiraling roots, 30-person capacity
- **Meditation Circle**: Stone seats, 12-person, silence mode (voice disabled)
- **Stream Path**: Linear walk, 2-person width, reflective conversations
- **Canopy Platforms**: Climb rope, 8-person treehouse, bird's-eye view
- **Cave Shrine**: Bioluminescent mushrooms, 6-person, echo chamber

**Audio Zones**:
- Meditation Circle: Voice disabled, ambient nature sounds only
- Cave: 15-tile range, heavy reverb
- Stream Path: 20-tile range, water babble background

**Aesthetic**:
- Time: Dusk (soft purple-orange gradient)
- Color: Deep greens, browns, bioluminescent blues/purples
- Animation: Leaf fall, firefly particles, water ripple, mushroom glow pulse
- Secrets: Hidden animals (deer, fox) that appear when areas are quiet

---

### Airship Deck (Adventure Vibe)

**Concept**: Steampunk vessel in flight. Kinetic, exploratory.

**Layout**:
```
    [Crow's Nest]
          |
    [Main Deck]--[Captain's Quarters]
          |
    [Engine Room]--[Cargo Hold]
```

**Zones**:
- **Main Deck** (40x30 tiles): Railing overlook, clouds rushing past, 25-person capacity
- **Captain's Quarters**: Map table, 6-person strategy discussions
- **Crow's Nest**: Climb mast, 4-person, panoramic view
- **Engine Room**: Clanking machinery, 10-person, industrial aesthetic
- **Cargo Hold**: Crates, 15-person, casual hangout

**Audio Zones**:
- Main Deck: 30-tile range, wind ambiance
- Engine Room: 20-tile range, mechanical noise overlay
- Crow's Nest: 12-tile range, isolated feeling

**Aesthetic**:
- Time: Midday (bright, clear)
- Color: Brass, bronze, wood tones, blue sky
- Animation: Propeller spin, smoke puffs, flag whip, cloud scroll
- Secrets: Interact with telescope to see distant lands, hidden treasure chest

---

## Visual Language

### Tile Grammar

**Ground Tiles** (what you walk on):
- 3x3 variation rule: No tile repeats in a 3x3 grid (prevents patterns)
- Edge blending: 4 transition tiles per terrain pair (grass→stone, stone→water)
- Wear paths: High-traffic areas get subtle dirt trails

**Wall Tiles** (collision objects):
- Auto-tiling: 48-tile template (all edge/corner combos)
- Top faces: Always lighter (lighting from above)
- Depth: Minimum 2-tile height for readability

**Interactive Objects**:
- Glow outline when hover (2px, subtle pulse)
- Animation state change on interact (door opens, lever pulls)
- Sound effect + particle on interaction

### Sprite Design

**Character Proportions**:
- 32x32px total (24px usable, 8px buffer for animations)
- Head: 8-10px (1/3 of body)
- Body: 14-16px
- Legs: 6-8px
- Chrono Trigger uses ~2.5 heads tall (chibi proportions)

**Walk Cycle** (per direction):
- Frame 1: Contact (foot forward)
- Frame 2: Passing (upright)
- Frame 3: Contact (opposite foot)
- Frame 4: Passing return
- Loop at 8 FPS

**Sitting Pose**:
- Side profile only (left/right)
- Legs bent, hands in lap or on armrests
- Slight bob animation (breathing)

**Emote Overlays** (8x8px above head):
- Bubble shapes with icon inside
- Appear + scale up + fade (0.5s total)
- Queue system (one emote at a time)

### Color Palette

**Chrono Trigger Master Palette** (64 colors):
- 16 grayscale (shadows, highlights)
- 12 earth tones (browns, tans)
- 8 greens (foliage)
- 8 blues (water, sky)
- 8 accent colors (reds, purples, golds)
- 12 skin tones (diversity)

**Dithering**:
- Checkerboard pattern for gradients (2x2 alternating pixels)
- Use sparingly (90s JRPG style, not NES constraints)

**Lighting**:
- Light source always top-left (consistency)
- Highlights: +20% brightness
- Shadows: -40% brightness, shift toward blue

---

## Interaction Patterns

### Object Interactions

**Chairs** (most important social object):
- Click to sit → Sprite changes to sitting pose
- Movement disabled, voice still active
- AFK auto-sit after 5 min idle
- Stand up: Any movement input

**Doors**:
- Automatic slide when approached
- Lead to interior spaces (scene transition)
- Can be locked (admin control)

**Quest Board** (The Crossroads):
- Click to open UI panel
- Shows "looking for" posts (players can post topics they want to discuss)
- Pin location on map to find people

**Bookshelves** (Library):
- Click to read random knowledge snippet
- Appears as text bubble
- Easter egg: Rare books trigger effects

### Social Features

**Name Tags**:
- Float above sprite (always visible)
- Scale with zoom level
- Color coded: Green (talking), Gray (muted), Yellow (AFK)

**Proximity List** (UI panel):
- Shows all players within voice range
- Click name to highlight their sprite
- Volume sliders for individual players

**Whisper Mode**:
- Hold Shift + Click player → Private voice channel
- Visual indicator (dotted line between sprites)
- Auto-cancel when distance exceeds threshold

**Broadcast Mode** (admin):
- Speaker on stage can toggle broadcast
- Voice heard by entire room (ignores distance)
- Used for presentations, announcements

---

## Technical Implementation Notes

### Movement System
```typescript
// Smooth interpolation (no grid snap)
player.x = lerp(player.x, targetX, 0.2);
player.y = lerp(player.y, targetY, 0.2);

// Collision detection (tile-based)
const tileX = Math.floor(player.x / TILE_SIZE);
const tileY = Math.floor(player.y / TILE_SIZE);
if (collisionMap[tileY][tileX]) {
  // Prevent movement
}
```

### Voice Attenuation
```typescript
const distance = Math.hypot(
  listener.x - speaker.x,
  listener.y - speaker.y
);

const maxRange = 30 * TILE_SIZE; // 30 tiles
const volume = Math.max(0, 1 - (distance / maxRange));

// Exponential curve (more realistic)
const adjustedVolume = Math.pow(volume, 2);

speaker.setVolume(adjustedVolume);
```

### Performance Optimizations
- Spatial hashing: Only update voice for players in same grid cell
- Culling: Don't render sprites outside viewport
- Asset streaming: Load tile chunks on-demand for large worlds
- WebSocket compression: Delta updates (only send changed positions)

---

## Launch Checklist

### Pre-Launch
- [ ] 5 signature worlds fully playable
- [ ] 50 sprite options (diverse representation)
- [ ] Mobile touch controls tested
- [ ] Voice quality validated (100-person test)
- [ ] Load testing (500 concurrent across worlds)
- [ ] Accessibility audit (screen readers, colorblind modes)

### Day 1
- [ ] Landing page with video demo
- [ ] Public world links shareable
- [ ] Analytics dashboard live
- [ ] Support channel (Discord/email)

### Week 1
- [ ] User feedback → Hotfix patches
- [ ] First community event (100-person gathering)
- [ ] Press outreach (tech, gaming media)

### Month 1
- [ ] World editor beta (10 power users)
- [ ] Custom sprite upload feature
- [ ] Pro tier launch
- [ ] Case study: Conference/meetup usage

---

## Inspirations to Study

### Games
- **Chrono Trigger** (art style, color, animation)
- **Final Fantasy VI** (character sprites, world variety)
- **Secret of Mana** (vibrant colors, readability)
- **Stardew Valley** (modern pixel art, cozy feel)

### Social Platforms
- **Gather.town** (proximity voice UX)
- **VRChat** (social affordances, world variety)
- **Club Penguin** (accessible social gaming)
- **Habbo Hotel** (rooms as social containers)

### Design References
- **Studio Ghibli backgrounds** (layered depth, lighting)
- **Pixel art tutorials** (MortMort, Brandon James Greer)
- **Game feel** (Vlambeer's "Art of Screenshake")
