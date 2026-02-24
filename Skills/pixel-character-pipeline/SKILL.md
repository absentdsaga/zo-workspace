---
name: pixel-character-pipeline
description: Zero-cost pipeline for creating pixel art characters for spatial worlds using free AI generation + manual animation tools
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
  category: game-art
  cost: free
  version: 1.0.0
---

# Zero-Cost Pixel Character Pipeline

**No API costs. No subscriptions. Complete creative control.**

This skill gives you a professional pixel art workflow using entirely free tools:
- **ComfyUI** - Free AI image generation (local or RunPod GPU)
- **Aseprite** - Free pixel art editor (compiled from source)
- **Manual animation** - Your artistic touch

## Why This Beats Paid APIs

| Paid APIs (Scenario.com, etc.) | This Pipeline |
|--------------------------------|---------------|
| $29-99/month for API access | $0 forever |
| Generic outputs | Custom style control |
| Rate limits | Unlimited |
| No creative control | Full artistic direction |
| Can't fine-tune | Can fine-tune models |

## The Pipeline

### Stage 1: AI Generation (ComfyUI)

Generate base character sprites using free AI models:

**Option A: RunPod** (pay-per-use, pennies per hour)
- Cost: ~$0.50/hour for GPU time
- Generate 50 sprites in 1 hour = $0.50 total

**Option B: Local** (free, slower)
- Run ComfyUI locally if you have a GPU

**What you generate:**
- Character base poses (idle, walk frames)
- Multiple angles (N, NE, E, SE, S, SW, W, NW)
- Variations (different outfits, colors)

### Stage 2: Cleanup & Animation (Aseprite)

Aseprite is your pixel art workstation:

```bash
# Launch Aseprite (once built):
/home/workspace/Skills/aseprite/build/bin/aseprite
```

**Aseprite Workflow:**
1. Import AI-generated sprite
2. Clean up - Fix pixel imperfections
3. Palette - Reduce to Chrono Trigger 64-color palette
4. Animate - Create walk cycles manually (4-8 frames)
5. Export - Save as sprite sheet with JSON metadata

### Stage 3: Export for Phaser

Export sprite sheet from Aseprite:
- File → Export Sprite Sheet
- Format: PNG
- Layout: By rows (8 directions × 4 frames each)
- JSON: Hash format
- Output: Skills/spatial-worlds/assets/sprites/

## Cost Breakdown

**Total cost for 50 unique characters:**

| Method | Cost |
|--------|------|
| Scenario.com API | $99/month |
| This pipeline | $0.50 (1hr RunPod) |
| **Savings** | **$98.50** |

**Time investment:**
- ComfyUI generation: 1 hour (automated)
- Aseprite cleanup: 10-15 min per character
- First-time setup: 2 hours (one-time)

## Quality Control

✅ Fix AI mistakes - Clean up bad pixels in Aseprite
✅ Consistent style - Fine-tune ComfyUI model on your art
✅ Perfect animation - Hand-craft smooth walk cycles
✅ Palette control - Match Chrono Trigger exactly
✅ No rate limits - Generate unlimited sprites

## Installation Checklist

- [ ] ComfyUI (local or RunPod account)
- [ ] Aseprite compiled from source (currently building)
- [ ] Pixel art reference library
- [ ] ComfyUI workflow configured

## Why This Matters

You're building a **game**, not just using a service. This pipeline gives you:
- **Ownership** - No vendor lock-in
- **Scalability** - Generate 1000s of sprites
- **Quality** - Hand-crafted animation
- **Cost** - Practically free

**Bottom line:** Invest 2 hours in setup, save $1000s in API costs.
