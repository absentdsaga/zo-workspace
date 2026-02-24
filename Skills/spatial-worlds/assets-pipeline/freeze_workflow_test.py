#!/usr/bin/env python3
"""
Workflow freeze test - locks a single ComfyUI workflow with 3 smoke prompts
Zero tolerance for artifacts before proceeding to API integration

Test prompts:
1. hero_orange idle
2. npc_bear walk_contact
3. npc_raccoon attack_impact

Acceptance criteria:
- no background card/box
- feet visible
- consistent 3/4 angle
- silhouette readable at game zoom
"""

import json
import sys
import time
import urllib.request
from pathlib import Path
import subprocess

def test_workflow():
    """Run the 3 smoke tests and validate outputs"""
    
    smoke_tests = [
        {
            "id": "hero_orange_idle",
            "positive": "isometric 3/4 tactical RPG character sprite, orange hero character, neutral idle pose, weight balanced, readable silhouette, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark",
            "negative": "rectangular frame, border, poster, card, background scene, floor texture, painterly smear, noisy texture, blurry edges, extra limbs, cropped feet, cut-off weapon, watermark, text, logo",
            "seed": 1001
        },
        {
            "id": "npc_bear_walk_contact",
            "positive": "isometric 3/4 tactical RPG character sprite, brown bear character, walk cycle contact pose, one foot forward one back, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark",
            "negative": "rectangular frame, border, poster, card, background scene, floor texture, painterly smear, noisy texture, blurry edges, extra limbs, cropped feet, cut-off weapon, watermark, text, logo",
            "seed": 2001
        },
        {
            "id": "npc_raccoon_attack_impact",
            "positive": "isometric 3/4 tactical RPG character sprite, raccoon character, attack impact pose, clear forward action line, single character only, clean pixel-art readability, limited palette, crisp silhouette, feet fully visible, grounded stance, transparent background, no environment, no frame, no card, no text, no watermark",
            "negative": "rectangular frame, border, poster, card, background scene, floor texture, painterly smear, noisy texture, blurry edges, extra limbs, cropped feet, cut-off weapon, watermark, text, logo",
            "seed": 3001
        }
    ]
    
    # Load workflow template
    workflow_path = Path(__file__).parent / "comfy" / "workflow_character_base.json"
    with open(workflow_path) as f:
        workflow_template = json.load(f)
    
    # Output directory
    test_output = Path(__file__).parent / "test_freeze_output"
    test_output.mkdir(exist_ok=True)
    
    comfy_url = "http://localhost:8188"
    results = []
    
    print("=" * 60)
    print("WORKFLOW FREEZE TEST - 3 SMOKE PROMPTS")
    print("=" * 60)
    
    for test in smoke_tests:
        print(f"\n🔧 Testing: {test['id']}")
        print(f"   Seed: {test['seed']}")
        
        # Build workflow
        workflow = json.loads(json.dumps(workflow_template))
        workflow["2"]["inputs"]["text"] = test["positive"]
        workflow["3"]["inputs"]["text"] = test["negative"]
        workflow["5"]["inputs"]["seed"] = test["seed"]
        workflow["7"]["inputs"]["filename_prefix"] = f"freeze_test_{test['id']}"
        
        try:
            # Submit to ComfyUI
            import requests
            response = requests.post(
                f"{comfy_url}/prompt",
                json={"prompt": workflow}
            )
            response.raise_for_status()
            result = response.json()
            prompt_id = result["prompt_id"]
            
            print(f"   ✓ Prompt queued: {prompt_id}")
            
            # Poll for completion
            max_wait = 1800
            start_time = time.time()
            output_path = None
            
            while time.time() - start_time < max_wait:
                time.sleep(2)
                
                history_response = requests.get(f"{comfy_url}/history/{prompt_id}")
                history = history_response.json()
                
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    
                    if "7" in outputs and "images" in outputs["7"]:
                        images = outputs["7"]["images"]
                        if images:
                            image_info = images[0]
                            image_filename = image_info["filename"]
                            image_subfolder = image_info.get("subfolder", "")
                            image_type = image_info.get("type", "output")
                            
                            download_params = f"filename={image_filename}&subfolder={image_subfolder}&type={image_type}"
                            download_url = f"{comfy_url}/view?{download_params}"
                            
                            output_path = test_output / f"{test['id']}.png"
                            urllib.request.urlretrieve(download_url, output_path)
                            
                            print(f"   ✓ Downloaded: {output_path.name}")
                            break
            
            if not output_path or not output_path.exists():
                print(f"   ✗ TIMEOUT - no output after {max_wait}s")
                results.append({
                    "id": test["id"],
                    "status": "TIMEOUT",
                    "path": None
                })
                continue
            
            # Run visual inspection checks
            print(f"   🔍 Running artifact checks...")
            
            failures = []
            
            # Check 1: File exists and is valid PNG
            try:
                from PIL import Image
                img = Image.open(output_path)
                width, height = img.size
                
                if img.mode != "RGBA":
                    failures.append("Not RGBA format (transparency required)")
                
                if width != 768 or height != 768:
                    failures.append(f"Wrong dimensions: {width}x{height} (expected 768x768)")
                
            except Exception as e:
                failures.append(f"Invalid image file: {e}")
                results.append({
                    "id": test["id"],
                    "status": "FAIL",
                    "path": str(output_path),
                    "failures": failures
                })
                continue
            
            # Check 2: Detect rectangular frame/box artifacts
            # Simple heuristic: check edges for solid blocks
            pixels = img.load()
            
            # Sample edge regions
            edge_samples = []
            # Top edge
            for x in range(50, 718, 100):
                edge_samples.append(pixels[x, 10])
            # Bottom edge
            for x in range(50, 718, 100):
                edge_samples.append(pixels[x, 757])
            # Left edge
            for y in range(50, 718, 100):
                edge_samples.append(pixels[10, y])
            # Right edge
            for y in range(50, 718, 100):
                edge_samples.append(pixels[757, y])
            
            # Count non-transparent edge pixels
            opaque_edges = sum(1 for rgba in edge_samples if len(rgba) >= 4 and rgba[3] > 128)
            
            if opaque_edges > len(edge_samples) * 0.3:
                failures.append(f"Edge artifacts detected: {opaque_edges}/{len(edge_samples)} edge samples opaque (likely frame/card)")
            
            # Check 3: Feet visibility (bottom 15% should have character pixels)
            bottom_start_y = int(height * 0.85)
            bottom_pixels = []
            for y in range(bottom_start_y, height):
                for x in range(width):
                    pixel = pixels[x, y]
                    if len(pixel) >= 4 and pixel[3] > 128:
                        bottom_pixels.append(pixel)
            
            if len(bottom_pixels) < 100:
                failures.append(f"Feet likely cropped: only {len(bottom_pixels)} visible pixels in bottom 15%")
            
            # Check 4: Character presence (center region should have content)
            center_pixels = []
            for y in range(int(height * 0.3), int(height * 0.7)):
                for x in range(int(width * 0.3), int(width * 0.7)):
                    pixel = pixels[x, y]
                    if len(pixel) >= 4 and pixel[3] > 128:
                        center_pixels.append(pixel)
            
            if len(center_pixels) < 1000:
                failures.append(f"No character visible: only {len(center_pixels)} pixels in center region")
            
            # Check 5: Transparency (background should be transparent)
            all_opaque = True
            for y in range(0, height, 50):
                for x in range(0, width, 50):
                    pixel = pixels[x, y]
                    if len(pixel) >= 4 and pixel[3] < 128:
                        all_opaque = False
                        break
                if not all_opaque:
                    break
            
            if all_opaque:
                failures.append("No transparency detected - background not removed")
            
            # Result
            if failures:
                print(f"   ✗ FAIL")
                for f in failures:
                    print(f"      - {f}")
                results.append({
                    "id": test["id"],
                    "status": "FAIL",
                    "path": str(output_path),
                    "failures": failures
                })
            else:
                print(f"   ✓ PASS")
                results.append({
                    "id": test["id"],
                    "status": "PASS",
                    "path": str(output_path),
                    "failures": []
                })
        
        except Exception as e:
            print(f"   ✗ ERROR: {e}")
            results.append({
                "id": test["id"],
                "status": "ERROR",
                "path": None,
                "failures": [str(e)]
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("FREEZE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] in ["ERROR", "TIMEOUT"])
    
    print(f"Passed: {passed}/3")
    print(f"Failed: {failed}/3")
    print(f"Errors: {errors}/3")
    
    if passed == 3:
        print("\n✅ WORKFLOW LOCKED - Ready for API integration")
        
        # Save the locked workflow
        locked_workflow_path = Path(__file__).parent / "comfy" / "workflow_locked_v1.json"
        with open(locked_workflow_path, "w") as f:
            json.dump(workflow_template, f, indent=2)
        print(f"   Saved to: {locked_workflow_path}")
        
        return 0
    else:
        print("\n❌ WORKFLOW NOT READY - Fix artifacts before proceeding")
        print("\nNext steps:")
        print("1. Review failed outputs in test_freeze_output/")
        print("2. Adjust workflow parameters (denoise, negative prompt, etc.)")
        print("3. Re-run this test until 3/3 pass")
        print("4. Only then integrate API calls into batch_orchestrator.py")
        
        return 1

if __name__ == "__main__":
    sys.exit(test_workflow())
