# Sprite Pipeline - Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPRITE GENERATION PIPELINE                      │
│                         (saga_iso_v1 preset)                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: STYLE CALIBRATION (One-time setup)                        │
└─────────────────────────────────────────────────────────────────────┘

  📁 input/refs/
    ├─ hero_ref_01.png
    ├─ npc_monkey_ref_01.png
    ├─ npc_bear_ref_01.png
    └─ style_board_01.png
           │
           ├──► Configure ComfyUI workflow
           │      └─ Export workflow JSON to comfy/
           │
           ├──► Generate 12 test frames
           │      └─ 3 characters × 4 key poses
           │
           ├──► Validate in-scene
           │      ├─ Check scale consistency
           │      ├─ Verify grounding
           │      └─ Look for artifacts
           │
           └──► LOCK pipeline_config.json
                  └─ No changes after this point


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: BATCH PRODUCTION (Per character)                          │
└─────────────────────────────────────────────────────────────────────┘

  📄 jobs/hero_orange.json
    ├─ character_id: "hero_orange"
    ├─ states: [idle, walk, attack, hit]
    └─ reference_images: [...]
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 1: ComfyUI Generation (⏳ PENDING INTEGRATION)     │
  └───────────────────────────────────────────────────────────┘
           │
           │  For each state (idle, walk, attack, hit):
           │    For each frame (1..N):
           │
           ├──► Load workflow JSON
           │      └─ comfy/workflow_character_base.json
           │
           ├──► Inject prompts + seed
           │      ├─ Global style: "isometric 3/4 tactical..."
           │      ├─ Pose: "walk cycle contact pose..."
           │      ├─ Negative: "rectangular frame, border..."
           │      └─ Seed: base_seed + frame_offset
           │
           ├──► POST to ComfyUI API
           │      └─ http://localhost:8188/prompt
           │
           ├──► Poll for completion
           │
           └──► Download result
                  └─ 📁 output_raw/hero_orange/walk/
                       ├─ hero_orange_walk_f01_raw.png (768×768)
                       ├─ hero_orange_walk_f02_raw.png
                       └─ ...
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 2: Cutout & Cleanup (✅ READY)                      │
  └───────────────────────────────────────────────────────────┘
           │
           ├──► Background removal
           │      └─ Even if "transparent" requested
           │
           ├──► Alpha threshold cleanup
           │      └─ Remove pixels with alpha < 10
           │
           └──► Edge halo decontamination
                  └─ 1px edge blur reduction
                       └─ 📁 output_cut/hero_orange/
                            ├─ hero_orange_walk_f01_cut.png
                            └─ ...
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 3: Normalization (✅ READY)                         │
  │   Script: normalize_sprite.py                             │
  └───────────────────────────────────────────────────────────┘
           │
           ├──► Trim transparent margins
           │
           ├──► Scale to target height (84px)
           │      └─ Method: nearest-neighbor (pixel-perfect)
           │
           ├──► Quantize palette
           │      └─ Max colors: 36
           │
           ├──► Recenter to canvas
           │      ├─ Canvas: 128×128 px
           │      ├─ Baseline (feet): y=108
           │      └─ Pivot: (64, 108) bottom-center
           │
           └──► Save normalized frame
                  └─ 📁 output_norm/hero_orange/
                       ├─ hero_orange_walk_f01.png (128×128)
                       └─ ...
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 4: Quality Control (✅ READY)                       │
  │   Script: qc_checker.py                                   │
  └───────────────────────────────────────────────────────────┘
           │
           ├──► CHECK 1: Box artifacts
           │      └─ Pass if opaque border pixels ≤ 5
           │
           ├──► CHECK 2: Feet visibility
           │      └─ Pass if lowest pixel at y=108±2
           │
           ├──► CHECK 3: Scale drift
           │      └─ Pass if height = 84px ±5%
           │
           ├──► CHECK 4: Palette overflow
           │      └─ Pass if colors ≤ 36
           │
           ├──► CHECK 5: Jitter
           │      └─ Pass if center-of-mass shift ≤ 2px
           │
           └──► CHECK 6: Silhouette break
                  └─ Pass if area change ≤ 18%
                       │
           ┌───────────┴───────────┐
           │                       │
         PASS                   FAIL
           │                       │
           ▼                       ▼
    📁 output_qc_pass/      📁 output_qc_fail/
       hero_orange/            hero_orange/
       ├─ hero_*.png           ├─ hero_*.png
       └─ ...                  └─ hero_*_reason.json
                                     └─ {"check": "feet_visibility",
                                          "reason": "at y=112, expected 108±2"}
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 5: Metadata Generation (✅ READY)                   │
  └───────────────────────────────────────────────────────────┘
           │
           └──► Generate animation JSON
                  └─ 📁 metadata/hero_orange/
                       ├─ hero_orange_idle.json
                       ├─ hero_orange_walk.json
                       ├─ hero_orange_attack.json
                       └─ hero_orange_hit.json

                       Example (hero_orange_walk.json):
                       {
                         "character_id": "hero_orange",
                         "state": "walk",
                         "frame_rate": 12,
                         "loop": true,
                         "pivot_px": [64, 108],
                         "baseline_y": 108,
                         "frames": [
                           {"file": "hero_orange_walk_f01.png", "duration_ms": 83},
                           {"file": "hero_orange_walk_f02.png", "duration_ms": 83},
                           ...
                         ],
                         "shadow": {"type": "blob", "radius_x": 10, "radius_y": 4}
                       }
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ STAGE 6: Logging & Results (✅ READY)                     │
  └───────────────────────────────────────────────────────────┘
           │
           └──► Write results
                  └─ 📁 logs/
                       ├─ hero_orange.log (execution log)
                       └─ hero_orange_results.json

                       Example (results.json):
                       {
                         "character_id": "hero_orange",
                         "states": {
                           "idle": {"passed_frames": 8, "total_frames": 8},
                           "walk": {"passed_frames": 10, "total_frames": 10},
                           "attack": {"passed_frames": 12, "total_frames": 12},
                           "hit": {"passed_frames": 5, "total_frames": 5}
                         }
                       }


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ATLAS ASSEMBLY (After QC pass)                            │
└─────────────────────────────────────────────────────────────────────┘

  📁 output_qc_pass/hero_orange/
    ├─ hero_orange_walk_f01.png
    ├─ hero_orange_walk_f02.png
    └─ ...
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Atlas Packing (✅ READY)                                  │
  │   Script: atlas_assembler.py                              │
  └───────────────────────────────────────────────────────────┘
           │
           ├──► Collect sprites for state
           │      └─ hero_orange_walk_*.png
           │
           ├──► Pack into grid
           │      ├─ Calculate grid dimensions
           │      └─ Place sprites with padding
           │
           ├──► Generate UV coordinates
           │      └─ Frame positions in atlas
           │
           └──► Save atlas + metadata
                  └─ 📁 atlas/
                       ├─ hero_orange_walk_atlas.png
                       └─ hero_orange_walk_atlas.json

                       Example (atlas.json):
                       {
                         "character_id": "hero_orange",
                         "state": "walk",
                         "atlas_image": "hero_orange_walk_atlas.png",
                         "frames": {
                           "hero_orange_walk_f01.png": {"x": 0, "y": 0, "width": 128, "height": 128},
                           "hero_orange_walk_f02.png": {"x": 130, "y": 0, "width": 128, "height": 128},
                           ...
                         }
                       }


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: ENGINE INTEGRATION (Your game engine)                     │
└─────────────────────────────────────────────────────────────────────┘

  📁 metadata/hero_orange/hero_orange_walk.json
  📁 atlas/hero_orange_walk_atlas.png
           │
           ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Load in Game Engine                                       │
  └───────────────────────────────────────────────────────────┘
           │
           ├──► Load atlas texture
           │      └─ const atlas = loadTexture('atlas/hero_orange_walk_atlas.png')
           │
           ├──► Load metadata
           │      └─ const meta = loadJSON('metadata/hero_orange_walk.json')
           │
           ├──► Create sprite
           │      ├─ sprite.pivot.set(meta.pivot_px[0], meta.pivot_px[1])
           │      └─ sprite.pivot = (64, 108)
           │
           ├──► Setup depth sorting
           │      └─ sprite.sortKey = sprite.y + sprite.elevation * 1000
           │
           ├──► Add blob shadow
           │      ├─ shadow.position = sprite.pivot
           │      └─ shadow.alpha = 0.28
           │
           └──► Play animation
                  └─ playAnimation(sprite, meta.frames, meta.frame_rate)


┌─────────────────────────────────────────────────────────────────────┐
│ RUNTIME: Animation Playback                                        │
└─────────────────────────────────────────────────────────────────────┘

  Frame 1 (83ms) → Frame 2 (83ms) → Frame 3 (83ms) → ...
           │              │              │
           ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  Sprite │    │  Sprite │    │  Sprite │
    │  @ y=50 │    │  @ y=51 │    │  @ y=52 │
    │ Pivot:  │    │ Pivot:  │    │ Pivot:  │
    │ (64,108)│    │ (64,108)│    │ (64,108)│
    │         │    │         │    │         │
    │ sortKey │    │ sortKey │    │ sortKey │
    │  = 50   │    │  = 51   │    │  = 52   │
    └─────────┘    └─────────┘    └─────────┘
         │              │              │
         └──────────────┴──────────────┘
                        │
                        ▼
              Depth-sorted rendering
              (back to front based on y position)


┌─────────────────────────────────────────────────────────────────────┐
│ KEY FILES & SCRIPTS                                                 │
└─────────────────────────────────────────────────────────────────────┘

  📄 pipeline_config.json        Master configuration (LOCK after calibration)
  📄 batch_orchestrator.py       Main pipeline controller (506 lines)
  📄 normalize_sprite.py         Frame standardization (185 lines)
  📄 qc_checker.py               Quality gates (232 lines)
  📄 atlas_assembler.py          Texture packing (141 lines)
  📄 start_comfyui.sh            ComfyUI server startup
  📄 test_pipeline.sh            Pipeline testing (no ComfyUI)


┌─────────────────────────────────────────────────────────────────────┐
│ COMMANDS                                                            │
└─────────────────────────────────────────────────────────────────────┘

  # Start ComfyUI
  ./start_comfyui.sh

  # Test pipeline (no ComfyUI)
  ./test_pipeline.sh

  # Run character job
  python3 batch_orchestrator.py jobs/hero_orange.json

  # Monitor job
  tail -f logs/hero_orange.log

  # Check results
  cat logs/hero_orange_results.json | jq

  # Build atlas
  python3 atlas_assembler.py hero_orange walk


┌─────────────────────────────────────────────────────────────────────┐
│ STATUS                                                              │
└─────────────────────────────────────────────────────────────────────┘

  ✅ ComfyUI installed & configured
  ✅ Pipeline directory structure
  ✅ Normalization (production ready)
  ✅ Quality control (6 automated gates)
  ✅ Metadata generation (engine-ready JSON)
  ✅ Atlas assembly (texture packing)
  ✅ Logging & results tracking
  ✅ Configuration system (locked parameters)
  ✅ Documentation (800+ lines)
  ✅ Helper scripts (test, startup)

  ⏳ ComfyUI API integration (line ~78 in batch_orchestrator.py)
     └─ Need to implement API calls for generation stage


┌─────────────────────────────────────────────────────────────────────┐
│ NEXT STEPS                                                          │
└─────────────────────────────────────────────────────────────────────┘

  1. Start ComfyUI server
  2. Design workflow in UI
  3. Export workflow JSON
  4. Download models (SD 1.5 + IP-Adapter)
  5. Implement API calls in batch_orchestrator.py
  6. Run style calibration (12 test frames)
  7. Lock parameters
  8. Start batch production

  Estimated time to first sprite: 1-2 hours
```
