#!/usr/bin/env python3
"""
Canva Studio — Design Automation CLI

Orchestrates Canva MCP tools for batch operations, asset pipelines,
and multi-platform design generation.

Usage:
  python3 canva.py batch-social --topic "..." --brand-kit-id "..." [--platforms ig,fb,tw,yt,pin,story]
  python3 canva.py export --design-id "D..." --format png [--width 1080] [--quality 100]
  python3 canva.py organize --query "..." --folder "..." [--create-folder]
  python3 canva.py audit --folder-id "..." [--export-manifest]
  python3 canva.py upload --url "https://..." --name "asset name"
  python3 canva.py search --query "..." [--ownership any|owned|shared]
  python3 canva.py info --design-id "D..."
"""

import argparse
import json
import sys
import os
from datetime import datetime

PLATFORM_SPECS = {
    "ig": {"type": "instagram_post", "name": "Instagram Post", "w": 1080, "h": 1080},
    "story": {"type": "your_story", "name": "Instagram/FB Story", "w": 1080, "h": 1920},
    "fb": {"type": "facebook_post", "name": "Facebook Post", "w": 1200, "h": 630},
    "fb_cover": {"type": "facebook_cover", "name": "Facebook Cover", "w": 1640, "h": 924},
    "tw": {"type": "twitter_post", "name": "Twitter/X Post", "w": 1600, "h": 900},
    "yt_thumb": {"type": "youtube_thumbnail", "name": "YouTube Thumbnail", "w": 1280, "h": 720},
    "yt_banner": {"type": "youtube_banner", "name": "YouTube Banner", "w": 2560, "h": 1440},
    "pin": {"type": "pinterest_pin", "name": "Pinterest Pin", "w": 1000, "h": 1500},
    "poster": {"type": "poster", "name": "Poster", "w": None, "h": None},
    "flyer": {"type": "flyer", "name": "Flyer", "w": None, "h": None},
    "logo": {"type": "logo", "name": "Logo", "w": None, "h": None},
    "biz_card": {"type": "business_card", "name": "Business Card", "w": None, "h": None},
    "infographic": {"type": "infographic", "name": "Infographic", "w": None, "h": None},
    "doc": {"type": "doc", "name": "Canva Doc", "w": None, "h": None},
    "presentation": {"type": "presentation", "name": "Presentation", "w": 1920, "h": 1080},
    "proposal": {"type": "proposal", "name": "Proposal", "w": None, "h": None},
    "report": {"type": "report", "name": "Report", "w": None, "h": None},
    "resume": {"type": "resume", "name": "Resume", "w": None, "h": None},
    "linkedin": {"type": None, "name": "LinkedIn Post", "w": 1200, "h": 627},
    "tiktok": {"type": None, "name": "TikTok Cover", "w": 1080, "h": 1920},
}

EXPORT_FORMATS = ["pdf", "png", "jpg", "gif", "pptx", "mp4"]


def build_batch_manifest(topic: str, platforms: list, brand_kit_id: str = None, asset_ids: list = None) -> dict:
    """Build a batch generation manifest for multi-platform design creation."""
    manifest = {
        "created": datetime.now().isoformat(),
        "topic": topic,
        "brand_kit_id": brand_kit_id,
        "platforms": [],
    }

    for p in platforms:
        spec = PLATFORM_SPECS.get(p)
        if not spec:
            print(f"WARNING: Unknown platform '{p}', skipping. Available: {', '.join(PLATFORM_SPECS.keys())}")
            continue

        entry = {
            "key": p,
            "name": spec["name"],
            "design_type": spec["type"],
            "dimensions": {"width": spec["w"], "height": spec["h"]} if spec["w"] else None,
            "status": "pending",
        }

        if spec["type"] is None:
            entry["note"] = f"No native Canva type — generate as closest match then resize to {spec['w']}x{spec['h']}"
            entry["design_type"] = "instagram_post" if spec["h"] > spec["w"] else "facebook_post"
            entry["needs_resize"] = True

        manifest["platforms"].append(entry)

    if asset_ids:
        manifest["asset_ids"] = asset_ids

    return manifest


def build_export_config(design_id: str, fmt: str, width: int = None, height: int = None,
                        quality: int = None, pages: list = None, transparent: bool = False) -> dict:
    """Build an export configuration dict."""
    config = {
        "design_id": design_id,
        "format": {"type": fmt},
    }

    if width and fmt in ("png", "jpg", "gif"):
        config["format"]["width"] = width
    if height and fmt in ("png", "jpg", "gif"):
        config["format"]["height"] = height
    if quality and fmt == "jpg":
        config["format"]["quality"] = quality
    if pages:
        config["format"]["pages"] = pages
    if transparent and fmt == "png":
        config["format"]["transparent_background"] = True

    return config


def build_edit_operations(operations_json: str) -> list:
    """Parse and validate edit operations from JSON string."""
    ops = json.loads(operations_json)
    valid_types = [
        "update_title", "replace_text", "find_and_replace_text",
        "update_fill", "insert_fill", "delete_element",
        "position_element", "resize_element", "format_text"
    ]
    for op in ops:
        if op.get("type") not in valid_types:
            raise ValueError(f"Invalid operation type: {op.get('type')}. Valid: {valid_types}")
    return ops


def print_platform_specs():
    """Print all platform specifications."""
    print("\n=== Canva Studio — Platform Specifications ===\n")
    print(f"{'Key':<14} {'Name':<22} {'Type':<20} {'Dimensions'}")
    print("-" * 75)
    for key, spec in PLATFORM_SPECS.items():
        dims = f"{spec['w']}×{spec['h']}" if spec['w'] else "Auto"
        dtype = spec['type'] or "(resize needed)"
        print(f"{key:<14} {spec['name']:<22} {dtype:<20} {dims}")
    print()


def print_workflow_steps(workflow: str):
    """Print step-by-step instructions for a workflow."""
    workflows = {
        "generate": [
            "1. (Optional) Call list-brand-kits to get brand_kit_id",
            "2. Call generate-design with query, design_type, and optional brand_kit_id",
            "3. User selects a candidate from the preview",
            "4. Call create-design-from-candidate with job_id and candidate_id",
            "5. (Optional) Edit via editing transaction",
            "6. (Optional) Export with export-design",
        ],
        "presentation": [
            "1. Call request-outline-review with topic, pages, audience, style, length",
            "2. User reviews and approves outline in widget",
            "3. Call generate-design-structured with approved outline",
            "4. Call create-design-from-candidate",
            "5. (Optional) Edit slides",
            "6. (Optional) Export as PPTX or PDF",
        ],
        "edit": [
            "1. Find design: search-designs or resolve-shortlink",
            "2. Call start-editing-transaction(design_id) → get transaction_id",
            "3. Review returned element list (richtexts, fills)",
            "4. Call perform-editing-operations with operations array",
            "5. Preview changes (thumbnails returned automatically)",
            "6. Call commit-editing-transaction or cancel-editing-transaction",
        ],
        "batch": [
            "1. Generate hero design for primary platform",
            "2. create-design-from-candidate → design_id",
            "3. For each additional platform: resize-design to target dimensions",
            "4. Export each variant",
            "5. Organize all into a Canva folder",
        ],
        "asset-pipeline": [
            "1. Generate/find image (Zo generate_image or image_search)",
            "2. upload-asset-from-url(url, name) → asset_id",
            "3. Use asset_id in generate-design or editing operations",
            "4. Export final design",
        ],
    }

    if workflow not in workflows:
        print(f"Unknown workflow. Available: {', '.join(workflows.keys())}")
        return

    print(f"\n=== Workflow: {workflow} ===\n")
    for step in workflows[workflow]:
        print(f"  {step}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Canva Studio — Design Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s platforms                          # List all platform specs
  %(prog)s workflow generate                  # Show generation workflow steps
  %(prog)s workflow batch                     # Show batch workflow steps
  %(prog)s batch-manifest --topic "VURT Launch" --platforms ig,fb,tw,story
  %(prog)s export-config --design-id DABcd1234_ --format png --width 1080
  %(prog)s edit-ops '[{"type":"find_and_replace_text","element_id":"e1","find_text":"old","replace_text":"new"}]'
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # platforms
    subparsers.add_parser("platforms", help="List all platform specifications")

    # workflow
    wf_parser = subparsers.add_parser("workflow", help="Show workflow steps")
    wf_parser.add_argument("name", choices=["generate", "presentation", "edit", "batch", "asset-pipeline"])

    # batch-manifest
    batch_parser = subparsers.add_parser("batch-manifest", help="Generate a batch creation manifest")
    batch_parser.add_argument("--topic", required=True, help="Design topic/description")
    batch_parser.add_argument("--platforms", required=True, help="Comma-separated platform keys")
    batch_parser.add_argument("--brand-kit-id", help="Optional brand kit ID")
    batch_parser.add_argument("--asset-ids", help="Comma-separated asset IDs to include")
    batch_parser.add_argument("--output", help="Output file path (default: stdout)")

    # export-config
    export_parser = subparsers.add_parser("export-config", help="Generate export configuration")
    export_parser.add_argument("--design-id", required=True, help="Design ID (starts with D)")
    export_parser.add_argument("--format", required=True, choices=EXPORT_FORMATS)
    export_parser.add_argument("--width", type=int, help="Export width in pixels")
    export_parser.add_argument("--height", type=int, help="Export height in pixels")
    export_parser.add_argument("--quality", type=int, help="JPEG quality 1-100")
    export_parser.add_argument("--pages", help="Comma-separated page numbers")
    export_parser.add_argument("--transparent", action="store_true", help="Transparent background (PNG only)")

    # edit-ops
    edit_parser = subparsers.add_parser("edit-ops", help="Validate edit operations JSON")
    edit_parser.add_argument("operations", help="JSON string of operations array")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "platforms":
        print_platform_specs()

    elif args.command == "workflow":
        print_workflow_steps(args.name)

    elif args.command == "batch-manifest":
        platforms = [p.strip() for p in args.platforms.split(",")]
        asset_ids = [a.strip() for a in args.asset_ids.split(",")] if args.asset_ids else None
        manifest = build_batch_manifest(args.topic, platforms, args.brand_kit_id, asset_ids)

        output = json.dumps(manifest, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Manifest written to {args.output}")
        else:
            print(output)

    elif args.command == "export-config":
        pages = [int(p) for p in args.pages.split(",")] if args.pages else None
        config = build_export_config(
            args.design_id, args.format, args.width, args.height,
            args.quality, pages, args.transparent
        )
        print(json.dumps(config, indent=2))

    elif args.command == "edit-ops":
        try:
            ops = build_edit_operations(args.operations)
            print(f"Valid: {len(ops)} operation(s)")
            print(json.dumps(ops, indent=2))
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
