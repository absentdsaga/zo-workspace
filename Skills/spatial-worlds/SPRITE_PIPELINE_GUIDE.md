# Complete Sprite Pipeline Guide
## 2.5D Isometric Tactical RPG - Production Ready

This is your **production-grade pipeline** for creating FFT-quality sprites with Chrono Trigger fluidity.

## 🎯 Goal

Build sprites that:
- Match FFT readability (clear silhouettes, readable at small size)
- Have Chrono Trigger fluidity (smooth animation, grounded movement)
- Fit seamlessly in your isometric tactical world
- Are engine-ready with proper metadata

## 📁 What You Have

### Directory Structure
```
Skills/spatial-worlds/
├── ComfyUI/                    # AI generation engine
│   └── venv/                   # Python environment
├── assets-pipeline/            # Production pipeline
│   ├── pipeline_config.json   # Master configuration
│   ├── batch_orchestrator.py  # Main pipeline controller
│   ├── normalize_sprite.py    # Frame normalization
│   ├── qc_checker.py          # Quality control automation
│   ├── atlas_assembler.py     # Texture atlas packing
│   ├── jobs/                  # Character job specs
│   │   ├── hero_orange.json
│   │   └── npc_bear.json
│   ├── input/refs/            # Reference images
│   ├── output_*/              # Pipeline stages
│   └── README.md              # Technical docs
└── SPRITE_PIPELINE_GUIDE.md   # This file
```

### Core Scripts

1. **batch_orchestrator.py** - Runs the full pipeline
   - Calls ComfyUI for generation
   - Processes through cutout → normalize → QC
   - Generates metadata
   - Logs everything

2. **normalize_sprite.py** - Frame standardization
   - 128x128 canvas
   - Foot baseline at y=108
   - Pivot at (64, 108)
   - Palette quantization
   - Pixel-perfect scaling

3. **qc_checker.py** - Quality gates
   - Box artifact detection
   - Feet alignment check
   - Scale drift validation
   - Palette overflow detection
   - Jitter analysis
   - Silhouette consistency

4. **atlas_assembler.py** - Texture packing
   - Creates sprite atlases
   - Generates UV coordinates
   - Optimizes for engine loading

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd Skills/spatial-worlds/assets-pipeline
pip3 install -r requirements.txt --break-system-packages
```

### 2. Test the Pipeline
```bash
./test_pipeline.sh
```

This will:
- Find an existing sprite
- Normalize it to spec
- Run QC checks
- Show you the output

### 3. Start ComfyUI (for generation)
```bash
./start_comfyui.sh
```

Access at: http://localhost:8188

## 📋 Production Workflow

### Phase 1: Style Calibration (DO THIS FIRST)

Before batch production, you need to lock your style:

1. **Create Reference Board**
   ```bash
   # Gather your best examples
   cp path/to/hero_sprite.png input/refs/hero_ref_01.png
   cp path/to/style_example.png input/refs/style_board_01.png
   ```

2. **Generate Test Batch** (12 frames)
   - 3 characters × 4 key poses
   - idle, walk_contact, attack_anticipation, hit

3. **Validate in Scene**
   - Place beside existing NPCs
   - Check scale consistency
   - Verify grounding with shadows
   - Look for box artifacts

4. **Lock Parameters**
   Once validated, DO NOT change:
   - `pipeline_config.json` → `comfy` section
   - `normalization` settings
   - Seed strategy

### Phase 2: Character Production

1. **Create Character Job**
   ```bash
   cd assets-pipeline
   cp jobs/hero_orange.json jobs/your_character.json
   ```

   Edit job file:
   ```json
   {
     "character_id": "npc_monkey",
     "states": ["idle", "walk", "attack", "hit"],
     "color_theme": "blue agile",
     "reference_images": [
       "input/refs/npc_monkey_ref.png",
       "input/refs/style_board_01.png"
     ]
   }
   ```

2. **Run Pipeline**
   ```bash
   python3 batch_orchestrator.py jobs/your_character.json
   ```

3. **Monitor Progress**
   ```bash
   tail -f logs/your_character.log
   ```

4. **Check Results**
   ```bash
   cat logs/your_character_results.json
   ```

5. **Review Failures**
   ```bash
   ls output_qc_fail/your_character/
   cat output_qc_fail/your_character/*_reason.json
   ```

### Phase 3: Atlas Assembly

After QC pass:

```bash
# Build atlas for specific animation
python3 atlas_assembler.py npc_monkey walk

# Or build for all animations
python3 atlas_assembler.py npc_monkey
```

Output:
- `atlas/npc_monkey_walk_atlas.png` - Texture atlas
- `atlas/npc_monkey_walk_atlas.json` - UV coordinates

## 🎨 ComfyUI Integration

### Current Status: PLACEHOLDER

The `batch_orchestrator.py` has a placeholder for ComfyUI API calls (line ~78).

### What You Need to Implement:

1. **Create Workflow JSON**
   - Use ComfyUI web UI to design workflow
   - Save as `comfy/workflow_character_base.json`
   - Key nodes:
     - Load Checkpoint
     - CLIP Text Encode (positive/negative)
     - Load Image (reference)
     - IP-Adapter or ControlNet
     - KSampler
     - VAE Decode
     - Save Image

2. **API Integration**
   ```python
   def run_comfy_generation(character_id, state, frame_num, seed_offset, config, job):
       import requests

       # Load workflow template
       with open("comfy/workflow_character_base.json") as f:
           workflow = json.load(f)

       # Inject prompts
       prompts = generate_comfy_prompt(character_id, state, pose, config, job)
       workflow["3"]["inputs"]["text"] = prompts["positive"]
       workflow["4"]["inputs"]["text"] = prompts["negative"]

       # Set seed
       workflow["5"]["inputs"]["seed"] = config["comfy"]["base_seed"] + seed_offset

       # POST to ComfyUI
       response = requests.post(
           "http://localhost:8188/prompt",
           json={"prompt": workflow}
       )

       # Poll for completion and download
       # ... (see ComfyUI API docs)
   ```

3. **Download Models**
   - SD 1.5 checkpoint (or SDXL if preferred)
   - IP-Adapter weights
   - ControlNet weights (optional)

   Place in `ComfyUI/models/`

## ⚙️ Configuration Reference

### pipeline_config.json Sections

#### comfy
```json
{
  "steps": 28,              // Generation steps
  "cfg": 6.0,               // CFG scale
  "sampler": "dpmpp_2m_karras",
  "gen_canvas": {
    "width": 768,
    "height": 768
  },
  "img2img_denoise": 0.45   // Refine pass strength
}
```

#### normalization
```json
{
  "canvas_w": 128,
  "canvas_h": 128,
  "target_char_height_px": 84,  // Character height in pixels
  "baseline_y": 108,             // Foot position (y coordinate)
  "pivot": [64, 108],            // Pivot point (x, y)
  "palette_max_colors": 36
}
```

#### qc_gates
```json
{
  "box_artifact_threshold": 5,      // Max opaque border pixels
  "feet_baseline_tolerance": 2,     // ±px from baseline
  "scale_drift_percent": 5,         // Height variance %
  "palette_overflow_threshold": 36, // Max unique colors
  "jitter_tolerance_px": 2,         // Frame-to-frame shift
  "silhouette_delta_percent": 18    // Area change %
}
```

#### prompts
Master prompt templates used for all generation:

```json
{
  "global_style": "isometric 3/4 tactical RPG character sprite...",
  "negative": "rectangular frame, border, poster...",
  "poses": {
    "idle": "neutral idle pose, weight balanced...",
    "walk_contact": "walk cycle contact pose..."
  }
}
```

#### animation_spec
Frame counts and timing for each state:

```json
{
  "walk": {
    "frames": 10,
    "frame_rate": 12,
    "loop": true
  },
  "attack": {
    "frames": 12,
    "frame_rate": 15,
    "loop": false,
    "events": {
      "hit_start": 6,    // Frame number for hit event
      "hit_end": 8
    }
  }
}
```

## 🎮 Engine Integration

### Loading Sprites in Your Game

```typescript
// Load metadata
const metadata = await fetch('metadata/hero_orange_walk.json').then(r => r.json());

// Load atlas
const atlas = await loadTexture('atlas/hero_orange_walk_atlas.png');

// Create sprite
const sprite = new Sprite(atlas);
sprite.pivot.set(metadata.pivot_px[0], metadata.pivot_px[1]);

// Depth sorting
sprite.sortKey = sprite.y + sprite.elevation * 1000 + metadata.sort_bias;

// Add shadow
const shadow = new Shadow({
  type: metadata.shadow.type,
  radiusX: metadata.shadow.radius_x,
  radiusY: metadata.shadow.radius_y,
  alpha: metadata.shadow.alpha
});
shadow.position = sprite.pivot;

// Animate
playAnimation(sprite, metadata.frames, metadata.frame_rate);
```

## 🔧 Troubleshooting

### All Frames Failing QC

**Problem**: Every frame goes to `output_qc_fail/`

**Check**:
1. Inspect failure reasons: `cat output_qc_fail/*/reason.json | jq`
2. Common issues:
   - **Feet not aligned**: Adjust `baseline_y` in config
   - **Scale drift**: Adjust `target_char_height_px`
   - **Palette overflow**: Reduce colors in generation or increase limit

### ComfyUI Generation Issues

**Problem**: Raw frames not generating

**Check**:
1. ComfyUI server running: `curl http://localhost:8188`
2. Workflow JSON valid
3. Models loaded in `ComfyUI/models/`
4. Check ComfyUI terminal for errors

### Jitter Between Frames

**Problem**: QC fails on jitter check

**Solutions**:
1. Use fixed seed strategy (deterministic generation)
2. Increase `jitter_tolerance_px` if acceptable
3. Post-process with motion smoothing

### Box Artifacts

**Problem**: Opaque pixels on frame borders

**Cause**: Generation not respecting transparency

**Fix**:
1. Strengthen negative prompt
2. Add "no border, no frame" to global style
3. Adjust cutout stage to be more aggressive

## 📊 Quality Standards

### What PASSES QC:

✅ Clean alpha edges (no halos)
✅ Feet within ±2px of baseline
✅ Height 84px ±5%
✅ Colors ≤ 36 unique
✅ Center-of-mass shift ≤ 2px between frames
✅ Silhouette area change ≤ 18%
✅ No opaque border pixels

### What FAILS QC:

❌ "Pasted card" look (box artifacts)
❌ Floating or clipped feet
❌ Scale drift (too big/small)
❌ Too many colors (palette overflow)
❌ Jittery animation (position jumps)
❌ Silhouette breaks (sudden size changes)

## 🎯 Next Steps

1. **Complete ComfyUI Integration**
   - Design workflow in UI
   - Export JSON
   - Implement API calls in `batch_orchestrator.py`

2. **Style Calibration Pass**
   - Generate 12 test frames
   - Validate in-scene
   - Lock parameters

3. **Batch Production**
   - Create job files for all characters
   - Run pipeline
   - Build atlases

4. **Engine Integration**
   - Load metadata in game
   - Implement depth sorting
   - Add shadows
   - Test animations

## 📚 Resources

- **ComfyUI API**: https://github.com/comfyanonymous/ComfyUI (see API examples)
- **Pipeline Config**: `assets-pipeline/pipeline_config.json`
- **Technical README**: `assets-pipeline/README.md`
- **Job Templates**: `assets-pipeline/jobs/`

---

**Pipeline Status**: ✅ Infrastructure complete, ⏳ ComfyUI integration pending

All automation, QC, normalization, and atlas assembly is **production-ready**.

The only remaining piece is connecting ComfyUI's API for the generation step.
