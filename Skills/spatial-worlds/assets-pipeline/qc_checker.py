#!/usr/bin/env python3
"""
QC automation for sprite pipeline
Validates frames against strict quality gates
"""

import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def load_config():
    config_path = Path(__file__).parent / "pipeline_config.json"
    with open(config_path) as f:
        return json.load(f)

def check_box_artifacts(img_array, threshold):
    """Check for opaque pixels on outer 2px border"""
    h, w = img_array.shape[:2]
    if img_array.shape[2] < 4:
        return True, "No alpha channel"

    alpha = img_array[:, :, 3]

    # Check outer 2px border
    border_mask = np.zeros((h, w), dtype=bool)
    border_mask[:2, :] = True  # top
    border_mask[-2:, :] = True  # bottom
    border_mask[:, :2] = True  # left
    border_mask[:, -2:] = True  # right

    opaque_border_pixels = np.sum((alpha > 200) & border_mask)

    if opaque_border_pixels > threshold:
        return False, f"Box artifacts: {opaque_border_pixels} opaque border pixels (threshold: {threshold})"
    return True, None

def check_feet_visibility(img_array, baseline_y, tolerance):
    """Check if feet are visible and aligned to baseline"""
    if img_array.shape[2] < 4:
        return True, "No alpha channel"

    alpha = img_array[:, :, 3]

    # Find lowest non-transparent pixel
    non_transparent_rows = np.where(np.any(alpha > 10, axis=1))[0]
    if len(non_transparent_rows) == 0:
        return False, "No visible pixels found"

    lowest_pixel_y = non_transparent_rows[-1]

    if abs(lowest_pixel_y - baseline_y) > tolerance:
        return False, f"Feet at y={lowest_pixel_y}, expected baseline={baseline_y}±{tolerance}"
    return True, None

def check_scale_drift(img_array, target_height, drift_percent):
    """Check if sprite height matches target"""
    if img_array.shape[2] < 4:
        return True, "No alpha channel"

    alpha = img_array[:, :, 3]

    # Get bounding box height
    non_transparent_rows = np.where(np.any(alpha > 10, axis=1))[0]
    if len(non_transparent_rows) == 0:
        return False, "No visible pixels"

    bbox_height = len(non_transparent_rows)
    max_deviation = target_height * (drift_percent / 100.0)

    if abs(bbox_height - target_height) > max_deviation:
        return False, f"Height {bbox_height}px, expected {target_height}±{max_deviation:.1f}px"
    return True, None

def check_palette_overflow(img_array, max_colors):
    """Check if unique colors exceed palette limit"""
    if img_array.shape[2] < 3:
        return True, "Invalid image format"

    # Reshape to list of RGB(A) tuples
    pixels = img_array.reshape(-1, img_array.shape[2])

    # Only count non-transparent pixels
    if img_array.shape[2] >= 4:
        opaque_mask = pixels[:, 3] > 10
        pixels = pixels[opaque_mask]

    # Count unique colors
    unique_colors = len(np.unique(pixels[:, :3], axis=0))

    if unique_colors > max_colors:
        return False, f"Palette overflow: {unique_colors} colors (max: {max_colors})"
    return True, None

def check_jitter(img_array, prev_array, tolerance_px):
    """Check center-of-mass shift between adjacent frames"""
    if prev_array is None:
        return True, None

    if img_array.shape[2] < 4 or prev_array.shape[2] < 4:
        return True, "No alpha channel"

    def get_center_of_mass(arr):
        alpha = arr[:, :, 3]
        y_indices, x_indices = np.where(alpha > 10)
        if len(y_indices) == 0:
            return None
        return (np.mean(x_indices), np.mean(y_indices))

    com1 = get_center_of_mass(img_array)
    com2 = get_center_of_mass(prev_array)

    if com1 is None or com2 is None:
        return True, None

    distance = np.sqrt((com1[0] - com2[0])**2 + (com1[1] - com2[1])**2)

    if distance > tolerance_px:
        return False, f"Jitter: {distance:.1f}px shift (max: {tolerance_px}px)"
    return True, None

def check_silhouette_break(img_array, prev_array, max_delta_percent):
    """Check bbox area delta between adjacent frames"""
    if prev_array is None:
        return True, None

    if img_array.shape[2] < 4 or prev_array.shape[2] < 4:
        return True, "No alpha channel"

    def get_bbox_area(arr):
        alpha = arr[:, :, 3]
        return np.sum(alpha > 10)

    area1 = get_bbox_area(img_array)
    area2 = get_bbox_area(prev_array)

    if area2 == 0:
        return True, None

    delta_percent = abs(area1 - area2) / area2 * 100

    if delta_percent > max_delta_percent:
        return False, f"Silhouette break: {delta_percent:.1f}% area change (max: {max_delta_percent}%)"
    return True, None
def check_angle_consistency(img_array, prev_array, max_mass_ratio_delta=0.15):
    """
    QC Gate #7: Angle consistency
    
    Reject if character facing drifts too far from locked 3/4 orientation
    between adjacent frames in same state (except turn animations).
    
    Proxy: compare left/right bbox mass ratio
    
    Args:
        max_mass_ratio_delta: Max allowed change in L/R mass ratio (0-1)
    """
    if prev_array is None:
        return True, None

    if img_array.shape[2] < 4 or prev_array.shape[2] < 4:
        return True, "No alpha channel"

    def get_lr_mass_ratio(arr):
        """Get ratio of left vs right pixel mass (relative to vertical center)"""
        alpha = arr[:, :, 3]
        h, w = alpha.shape
        
        # Find vertical center of mass
        y_indices, x_indices = np.where(alpha > 10)
        if len(x_indices) == 0:
            return None
        
        center_x = np.mean(x_indices)
        
        # Count pixel mass on left vs right of center
        left_mass = np.sum(alpha[:, :int(center_x)] > 10)
        right_mass = np.sum(alpha[:, int(center_x):] > 10)
        
        if right_mass == 0:
            return None
        
        # Ratio: values < 1 mean right-facing, > 1 mean left-facing
        # For 3/4 angle, expect consistent ratio across frames
        ratio = left_mass / right_mass
        return ratio

    ratio1 = get_lr_mass_ratio(img_array)
    ratio2 = get_lr_mass_ratio(prev_array)

    if ratio1 is None or ratio2 is None:
        return True, None

    # Check if ratio changed significantly (indicates angle drift)
    delta = abs(ratio1 - ratio2)

    if delta > max_mass_ratio_delta:
        return False, f"Angle drift: L/R mass ratio changed {delta:.2f} (max: {max_mass_ratio_delta})"
    
    return True, None


def run_qc(image_path, prev_image_path=None, config=None):
    """Run all QC checks on an image"""
    if config is None:
        config = load_config()

    qc_gates = config["qc_gates"]
    norm = config["normalization"]

    img = Image.open(image_path).convert("RGBA")
    img_array = np.array(img)

    prev_array = None
    if prev_image_path and Path(prev_image_path).exists():
        prev_img = Image.open(prev_image_path).convert("RGBA")
        prev_array = np.array(prev_img)

    results = {
        "image": str(image_path),
        "passed": True,
        "failures": []
    }

    # Run all checks
    checks = [
        ("box_artifacts", check_box_artifacts(img_array, qc_gates["box_artifact_threshold"])),
        ("feet_visibility", check_feet_visibility(img_array, norm["baseline_y"], qc_gates["feet_baseline_tolerance"])),
        ("scale_drift", check_scale_drift(img_array, norm["target_char_height_px"], qc_gates["scale_drift_percent"])),
        ("palette_overflow", check_palette_overflow(img_array, qc_gates["palette_overflow_threshold"])),
        ("jitter", check_jitter(img_array, prev_array, qc_gates["jitter_tolerance_px"])),
        ("silhouette_break", check_silhouette_break(img_array, prev_array, qc_gates["silhouette_delta_percent"])),
        ("angle_consistency", check_angle_consistency(img_array, prev_array, 0.15))
    ]

    for check_name, (passed, reason) in checks:
        if not passed:
            results["passed"] = False
            results["failures"].append({
                "check": check_name,
                "reason": reason
            })

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: qc_checker.py <image_path> [prev_image_path]")
        sys.exit(1)

    image_path = sys.argv[1]
    prev_image_path = sys.argv[2] if len(sys.argv) > 2 else None

    results = run_qc(image_path, prev_image_path)

    print(json.dumps(results, indent=2))
    sys.exit(0 if results["passed"] else 1)

if __name__ == "__main__":
    main()
