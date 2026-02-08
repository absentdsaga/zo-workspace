#!/usr/bin/env python3
"""Start the Remotion studio for live preview."""

import subprocess
import sys
import os

STUDIO_PATH = "/home/workspace/motion-graphics-studio"

def main():
    if not os.path.exists(STUDIO_PATH):
        print(f"Error: Studio not found at {STUDIO_PATH}")
        sys.exit(1)
    
    print("Starting Remotion Studio...")
    print("Preview will be available at http://localhost:3000")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run(
            ["bun", "run", "dev"],
            cwd=STUDIO_PATH,
            check=True
        )
    except KeyboardInterrupt:
        print("\nStopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting studio: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
