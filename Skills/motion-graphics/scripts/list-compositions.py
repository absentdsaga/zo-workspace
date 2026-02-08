#!/usr/bin/env python3
"""List all available compositions in the Remotion project."""

import subprocess
import sys
import os

STUDIO_PATH = "/home/workspace/motion-graphics-studio"

def main():
    if not os.path.exists(STUDIO_PATH):
        print(f"Error: Studio not found at {STUDIO_PATH}")
        sys.exit(1)
    
    print("Available compositions:")
    print()
    
    try:
        result = subprocess.run(
            ["bunx", "remotion", "compositions"],
            cwd=STUDIO_PATH,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # Fallback: parse Root.tsx
        root_path = os.path.join(STUDIO_PATH, "src", "Root.tsx")
        if os.path.exists(root_path):
            import re
            with open(root_path) as f:
                content = f.read()
            
            comps = re.findall(r'<Composition[^>]*id="([^"]+)"', content)
            for comp in comps:
                print(f"  - {comp}")
        else:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
