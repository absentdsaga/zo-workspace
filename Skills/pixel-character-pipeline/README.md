# Pixel Character Pipeline

**Zero-cost pipeline for creating pixel art game characters**

Use free AI generation for key poses → animate manually in GIMP → automate sprite sheet creation.

## Why This Approach?

✅ **$0/month** - Free tier AI + open source tools  
✅ **Full control** - Manual animation for quality  
✅ **Professional results** - Chrono Trigger / Final Fantasy Tactics quality  
✅ **50+ characters/month** - With free Scenario.com credits  

## Quick Links

- **[Quick Start](QUICKSTART.md)** - Create your first character in 15 min
- **[SKILL.md](SKILL.md)** - Complete documentation and advanced techniques
- **Scripts:**
  - `scripts/generate-key-poses.ts` - AI pose generation
  - `scripts/gif-to-spritesheet.ts` - GIF → sprite sheet
  - `scripts/palette-quantize.ts` - Retro palette reduction

## The Philosophy

**Aseprite is great but costs $20.** If you want to avoid that:

1. ✅ **Compile it yourself** (free, but complex build process)
2. ✅ **Use this workflow** (free, simple, production-ready)

We combine:
- **Scenario.com free tier** (100 credits/mo) for AI key poses
- **GIMP** (free, open source) for manual animation
- **ImageMagick** (free, CLI) for sprite sheet assembly
- **Automation scripts** for the boring parts

## What You Get

```
Skills/pixel-character-pipeline/
├── scripts/               # Automation tools
│   ├── generate-key-poses.ts    # AI generation
│   ├── gif-to-spritesheet.ts    # GIF converter
│   └── palette-quantize.ts      # Color reduction
├── Assets/
│   ├── key-poses/        # AI-generated starts
│   └── animations/       # GIMP .gif exports
└── Spritesheets/
    └── final/            # Game-ready sprite sheets
```

## Installation

```bash
# Install GIMP (for animation)
apt install -y gimp

# ImageMagick (auto-installed by scripts if needed)
apt install -y imagemagick

# Set up Scenario.com API key
# 1. Sign up at https://scenario.com (free)
# 2. Get API key from Settings
# 3. Add to Zo at /?t=settings&s=developers
```

## Example Workflow

```bash
# 1. Generate key pose with AI (1 credit)
bun scripts/generate-key-poses.ts \
  --character "pixel art mage, blue robes, staff" \
  --output Assets/key-poses/mage-idle.png

# 2. Animate in GIMP (manual - 5-10 minutes)
gimp Assets/key-poses/mage-idle.png
# → Create walk cycle
# → Export as mage-walk.gif

# 3. Convert to sprite sheet (automated)
bun scripts/gif-to-spritesheet.ts \
  --input Assets/animations/mage-walk.gif \
  --output Spritesheets/final/mage-walk.png \
  --frame-width 32 --frame-height 32

# 4. Optional: Reduce to retro palette
bun scripts/palette-quantize.ts \
  --input Spritesheets/final/mage-walk.png \
  --palette nes \
  --output Spritesheets/final/mage-walk-nes.png
```

## Comparison to Alternatives

| Tool | One-Time Cost | Monthly Cost | Automation | Quality |
|------|--------------|--------------|------------|---------|
| **This Pipeline** | $0 | $0 | High | Excellent |
| Compile Aseprite | $0 | $0 | High | Excellent |
| Buy Aseprite | $20 | $0 | High | Excellent |
| Piskel (web) | $0 | $0 | Low | Good |
| Midjourney | $0 | $10-60 | Medium | Variable |
| Pure manual | $0 | $0 | None | Excellent |

## Integration with Spatial Worlds

Works perfectly with:
- `Skills/spatial-worlds` - Isometric multiplayer engine
- `Skills/phaser-iso-engine` - Phaser 3 optimization
- `Skills/multiplayer-sync-iso` - Real-time sync

Load sprite sheets:
```typescript
this.load.spritesheet('character', 'character-walk.png', {
  frameWidth: 32,
  frameHeight: 32
});
```

## Tips for Success

1. **Start simple** - 4-frame walk cycles, not 8-frame
2. **Use references** - Study Chrono Trigger, FFT sprite sheets
3. **Batch generate** - Create all key poses first, animate later
4. **Test early** - Load in game engine after first animation
5. **Reuse palettes** - Consistent colors across all characters

## Support

- Read `SKILL.md` for detailed docs
- Check `QUICKSTART.md` for step-by-step guide
- Scripts have `--help` for usage info

## Credits

Built for Zo Computer by dioni.zo.computer
