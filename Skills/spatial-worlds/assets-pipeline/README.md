# Sprite Pipeline - 2.5D Isometric Tactical RPG

Repeatable pipeline for FFT-quality + Chrono-fluidity sprites.

## Directory Structure

```
assets-pipeline/
├── input/
│   ├── refs/          # Reference images and style boards
│   └── masks/         # Optional masks for generation
├── comfy/             # ComfyUI workflow JSON files
├── output_raw/        # Raw ComfyUI generation output
├── output_cut/        # Background removed frames
├── output_norm/       # Normalized frames (128x128, baseline-aligned)
├── output_qc_pass/    # Frames that passed QC
├── output_qc_fail/    # Failed frames with reason JSONs
├── atlas/             # Packed texture atlases
├── metadata/          # Engine-ready animation metadata
├── logs/              # Job execution logs
└── jobs/              # Character job specifications
```

## Pipeline Stages

### 1. ComfyUI Generation
- **Input**: Reference images + pose descriptions
- **Output**: 768x768 transparent PNGs
- **Config**: `pipeline_config.json` → `comfy` section

### 2. Cutout & Cleanup
- Background removal (even if "transparent" requested)
- Alpha threshold cleanup
- Edge halo decontamination

### 3. Normalization
- Resize to 128x128 canvas
- Enforce foot baseline at y=108
- Pivot at (64, 108) - bottom-center
- Palette quantization (max 36 colors)
- Nearest-neighbor scaling (pixel-perfect)

### 4. Quality Control
Automated pass/fail gates:
- **Box artifacts**: No opaque pixels on outer 2px border
- **Feet visibility**: Lowest pixel within ±2px of baseline
- **Scale drift**: Height within ±5% of target (84px)
- **Palette overflow**: Colors ≤ max palette size
- **Jitter check**: Center-of-mass shift ≤ 2px between frames
- **Silhouette break**: Area delta ≤ 18% between adjacent frames

Failed frames go to `output_qc_fail/` with reason JSON.

### 5. Metadata Generation
Creates engine-ready JSON per animation:
```json
{
  "character_id": "hero_orange",
  "state": "walk",
  "frame_rate": 12,
  "loop": true,
  "pivot_px": [64, 108],
  "baseline_y": 108,
  "frames": [...],
  "shadow": {"type": "blob", "radius_x": 10, "radius_y": 4, "alpha": 0.28}
}
```

### 6. Atlas Assembly
Packs sprites into texture atlas with position metadata.

## Usage

### Setup
```bash
# Install Python dependencies
pip3 install pillow numpy scipy

# Start ComfyUI server (in separate terminal)
cd ../ComfyUI
source venv/bin/activate
python main.py --listen
```

### Run a Job
```bash
# Process a character through full pipeline
python3 batch_orchestrator.py jobs/hero_orange.json

# Check logs
tail -f logs/hero_orange.log

# View results
cat logs/hero_orange_results.json
```

### Individual Tools

#### Normalize a single sprite
```bash
python3 normalize_sprite.py input.png output.png
```

#### QC check a frame
```bash
python3 qc_checker.py frame.png [prev_frame.png]
```

#### Build atlas
```bash
python3 atlas_assembler.py hero_orange walk
```

## Configuration

Edit `pipeline_config.json` to adjust:
- ComfyUI parameters (steps, CFG, sampler)
- Normalization spec (canvas size, baseline, palette)
- QC thresholds
- Animation frame counts and rates
- Prompting templates

## Creating a New Character Job

1. Add reference images to `input/refs/`
2. Create job file in `jobs/`:
```json
{
  "character_id": "npc_monkey",
  "style_profile": "saga_iso_v1",
  "size_class": "humanoid_m",
  "states": ["idle", "walk", "attack", "hit"],
  "color_theme": "blue agile",
  "reference_images": [
    "input/refs/npc_monkey_ref.png",
    "input/refs/style_board_01.png"
  ]
}
```
3. Run: `python3 batch_orchestrator.py jobs/npc_monkey.json`

## Style Calibration

Before full batch production:
1. Generate 12 test frames (3 characters × 4 key poses)
2. Check in-scene fit beside placeholder NPCs
3. Verify no box artifacts, consistent scale, clean grounding
4. Lock profile parameters once validated

## ComfyUI Integration

**TODO**: Implement actual ComfyUI API calls in `batch_orchestrator.py`

Current placeholder at line ~78 needs:
1. POST to `http://localhost:8188/prompt`
2. Workflow JSON with proper node wiring
3. Poll for completion
4. Download result to `output_raw/`

Reference: ComfyUI API docs

## Engine Integration

For Phaser/Babylon/Three.js:
1. Load atlas image + metadata JSON
2. Render sprite as quad with pivot at feet
3. Depth sort: `sortKey = y + elevation * elevationWeight + sortBias`
4. Add blob shadow under pivot
5. Use nearest filtering for pixel-perfect rendering

## Troubleshooting

**All frames failing QC:**
- Check normalization parameters in config
- Verify baseline_y matches your world scale
- Inspect `output_qc_fail/` reason JSONs

**ComfyUI generation issues:**
- Ensure server running on port 8188
- Check workflow JSON is valid
- Verify checkpoint/models loaded

**Palette overflow:**
- Reduce `palette_max_colors` in config
- Or adjust source generation prompts for simpler colors

**Jitter between frames:**
- Increase `jitter_tolerance_px` if acceptable
- Or use fixed seed strategy for better consistency
