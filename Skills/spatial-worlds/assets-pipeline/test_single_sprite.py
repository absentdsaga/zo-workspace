#!/usr/bin/env python3
"""
Test single sprite generation through complete pipeline
"""

import sys
import json
from pathlib import Path

# Import pipeline functions
sys.path.insert(0, str(Path(__file__).parent))
from batch_orchestrator import (
    load_config,
    generate_comfy_prompt,
    run_comfy_generation,
    process_frame
)

def test_single_sprite():
    """Generate a single test sprite"""
    config = load_config()

    # Test job
    job = {
        "character_id": "test_hero",
        "style_profile": "saga_iso_v1",
        "size_class": "humanoid_m",
        "states": ["idle"],
        "color_theme": "orange heroic",
        "reference_images": []
    }

    print("=== Single Sprite Generation Test ===")
    print()
    print(f"Character: {job['character_id']}")
    print(f"State: idle")
    print(f"Frame: 1")
    print()

    # Generate single frame
    print("Step 1: ComfyUI Generation")
    raw_path = run_comfy_generation(
        character_id="test_hero",
        state="idle",
        frame_num=1,
        seed_offset=0,
        config=config,
        job=job
    )

    print(f"  Raw output: {raw_path}")
    print()

    if not raw_path.exists():
        print("ERROR: Generation failed - raw file not created")
        print("Check ComfyUI logs at /tmp/comfyui.log")
        return False

    # Process through pipeline
    print("Step 2: Process through pipeline (cutout → normalize → QC)")
    result_path = process_frame(
        raw_path=raw_path,
        character_id="test_hero",
        state="idle",
        frame_num=1,
        prev_normalized_path=None,
        config=config,
        job=job
    )

    print()

    if result_path:
        print(f"✅ SUCCESS! Sprite passed QC: {result_path}")
        print()
        print("Output files:")
        print(f"  Raw:        {raw_path}")
        print(f"  Normalized: output_norm/test_hero/test_hero_idle_f01.png")
        print(f"  QC Pass:    {result_path}")
        return True
    else:
        print("❌ FAILED QC")
        print()
        print("Check failure reason:")
        fail_reason = Path(__file__).parent / "output_qc_fail" / "test_hero" / "test_hero_idle_f01_reason.json"
        if fail_reason.exists():
            with open(fail_reason) as f:
                reason = json.load(f)
                print(json.dumps(reason, indent=2))
        return False

if __name__ == "__main__":
    success = test_single_sprite()
    sys.exit(0 if success else 1)
