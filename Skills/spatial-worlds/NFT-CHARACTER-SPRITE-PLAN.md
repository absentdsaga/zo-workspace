# Solana NFT Character → Chrono Trigger Sprite Conversion Plan

## Character Analysis from Reference Images

### Set 1: The Core Crew
1. **Purple Vest Guy** - Streetwear entrepreneur with shades
2. **Skeleton King** - Crown, staff, purple/gold regal undead
3. **Orange Hoodie Bear** - Cozy hypebeast vibes

### Set 2: The Flex Squad
4. **Tie-Dye Penguin** - Hippie/psychedelic rainbow king
5. **Green Vest Character** - Explorer/adventurer energy
6. **Military Bear** - Tactical gear, serious vibe

### Set 3: The Fire Brigade
7. **Flaming Cat/Fox** - Mystical fire warrior
8. **Orange Flame Character** - Fire elemental hero
9. **Skeleton Priest** - Dark magic, staff wielder

### Set 4: Close-up Detail
10. **Black Cat Crypto Trader** - Tactical vest, intense eyes, tech-savvy

### Set 5: The Warriors
11. **Red-haired Fighter** - Martial artist, bandana
12. **Orange Cat Noble** - Royal cape, crown, commander
13. **Skeleton Warrior** - Gold armor, battle-ready

## Chrono Trigger Style Guidelines

### Technical Specs
- **Sprite Size:** 32x48 pixels (body) or 48x64 (with accessories)
- **Color Palette:** 12-16 colors per sprite
- **Animation Frames:** 3-4 per walk cycle
- **Directions:** 4 (down, up, left, right) minimum, 8 for premium

### Color Theory (CT Style)
- **Shadows:** Cool-toned (purple/blue tint, NOT gray)
- **Highlights:** Warm-toned (yellow/orange shift)
- **Outlines:** Black or very dark (not pure black on dark sprites)
- **Saturation:** High, vibrant, no muddy colors
- **Contrast:** High value range (darkest dark, brightest bright)

### Proportions (CT Character Scale)
- **Head:** 1/3 of total height (less chibi than your refs)
- **Body:** 2/3 height
- **Style:** Heroic but cute, not super-deformed

## Character-by-Character Conversion

### 1. Orange Hoodie Bear (Priority 1)
**Personality:** Cozy hypebeast, confident swagger
**Key Features:**
- Orange hoodie (4-5 shades: dark orange → bright highlight)
- Gold chain (2-3 yellows: shadow → shine)
- Bear face (brown gradients, white snout, black eyes/nose)

**Color Palette (16 colors):**
```
Oranges: #8B4513 #B8692B #D9843D #F0A155 #FFB570
Browns: #3E2723 #5D4037 #795548
Golds: #B8860B #FFD700 #FFED4E
Whites: #FFFFFF #E0E0E0
Blacks: #000000 #212121
Pink (nose): #FF6B9D
```

**Animation Notes:**
- Hoodie sways with walk
- Chain bounces slightly
- Head bob on walk cycle

### 2. Skeleton King (Priority 1)
**Personality:** Regal undead ruler, mystical power
**Key Features:**
- Bone texture (dithering for depth)
- Purple vest (rich, saturated purples)
- Gold crown (shiny, regal)
- Glowing staff (animated particle effect)

**Color Palette:**
```
Bones: #E8DCC7 #D4C4A8 #B8A88A #8B7355
Purples: #4A148C #6A1B9A #8E24AA #AB47BC
Golds: #B8860B #FFD700 #FFED4E
Greens (staff): #00E676 #69F0AE (glow)
Blacks: #000000 #1A1A1A
```

### 3. Black Cat Crypto Trader (Priority 2)
**Personality:** Tech-savvy, intense, tactical
**Key Features:**
- Sleek black fur (subtle shading)
- Tactical vest with patches
- Glowing phone/device
- Red/orange eyes (intensity)

**Color Palette:**
```
Blacks: #000000 #1A1A1A #2C2C2C #3D3D3D
Grays (vest): #424242 #616161 #757575
Neons (tech): #00E5FF #1DE9B6 #FF6E40
Eyes: #FF5722 #FF7043
```

### 4. Tie-Dye Penguin Hippie (Priority 2)
**Personality:** Chill, groovy, peace & love
**Key Features:**
- Rainbow tie-dye pattern (simplified for pixels)
- Peace sign necklace
- Round sunglasses (colored lenses)
- Penguin waddle animation

**Color Palette:**
```
Rainbow: #FF1744 #FF6F00 #FFEB3B #00E676 #2979FF #9C27B0
Blacks/whites: #000000 #FFFFFF #E0E0E0
Golds (peace sign): #FFD700
```

### 5. Shiba Doge Biker (Priority 3)
**Personality:** Tough, meme energy, rebel
**Key Features:**
- Tan/cream fur (shiba colors)
- Black leather jacket with spikes
- Red bandana
- Aviator sunglasses

**Color Palette:**
```
Fur: #F5DEB3 #DEB887 #D2691E #8B4513
Leathers: #000000 #1A1A1A #2C2C2C
Reds (bandana): #8B0000 #B22222 #DC143C
Silver (spikes): #C0C0C0 #E8E8E8
```

## Animation Framework

### Walk Cycle (4 frames, down-facing)
```
Frame 1: Left foot forward, right foot back
Frame 2: Both feet center (passing)
Frame 3: Right foot forward, left foot back
Frame 4: Both feet center (passing)
```

**Timing:** 150ms per frame = 600ms full cycle

### Idle Animation (2 frames)
```
Frame 1: Standing neutral
Frame 2: Slight head/body movement
```

**Timing:** 500ms per frame = breathing rhythm

## Production Workflow

### Option A: AI Generation (When Credits Available)
1. Generate base sprites with detailed prompts
2. Import to Aseprite for cleanup
3. Reduce to exact palette
4. Add pixel-perfect details
5. Create animation frames
6. Export sprite sheets

### Option B: Manual Pixel Art (Available Now)
1. Set up Aseprite with CT color palettes
2. Block out silhouette (3 colors)
3. Add mid-tones and highlights
4. Add detail pass (eyes, accessories)
5. Create walk cycle frames
6. Polish and export

### Option C: Hybrid (Recommended)
1. Use existing 3D renders as reference
2. Trace and simplify in Aseprite
3. Apply CT color theory
4. Hand-pixel refinement
5. Animate from scratch

## File Structure
```
/home/workspace/Skills/spatial-worlds/assets/sprites/nft-characters/
├── bear-orange-hoodie/
│   ├── down-walk-0.png
│   ├── down-walk-1.png
│   ├── down-walk-2.png
│   ├── down-walk-3.png
│   ├── up-walk-0.png
│   ├── ...
│   └── sprite-sheet.png
├── skeleton-king/
├── cat-crypto-trader/
└── ...
```

## Next Steps

1. **Set up tools:** Install Aseprite or use Piskel (web-based)
2. **Create master palette:** Extract CT colors from reference screenshots
3. **Start with 1 character:** Orange Hoodie Bear (most iconic)
4. **Test in-game:** Import to spatial-worlds, verify scale/animation
5. **Iterate:** Refine based on gameplay feel
6. **Batch produce:** Once formula works, create full roster

## References to Study

### Chrono Trigger Sprites to Analyze:
- **Crono:** Spiky hair animation, sword movement
- **Marle:** Cape flow, bow details
- **Lucca:** Helmet shine, gun accessories
- **Frog:** Non-human proportions, cape physics
- **Robo:** Metallic shading, mechanical parts

### Extract from: https://www.spriters-resource.com/snes/chronotrigger/

## Color Palette Files (Ready to Import)

Save these as `.pal` or `.gpl` for Aseprite:

```
GIMP Palette
Name: Chrono Trigger - Warm Palette
Columns: 8
#
139  69  19  CT Dark Brown
184 105  43  CT Medium Brown
217 132  61  CT Light Brown
240 161  85  CT Bright Orange
255 181 112  CT Highlight Orange
184 134  11  CT Dark Gold
255 215   0  CT Gold
255 237  78  CT Bright Gold
 62  39  35  CT Shadow
255 255 255  CT White
224 224 224  CT Light Gray
  0   0   0  CT Black
 33  33  33  CT Dark Gray
```

---

**Ready to proceed with manual sprite creation or wait for AI credits?**
