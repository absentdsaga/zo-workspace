#!/usr/bin/env python3
"""Download CBD EP29 (contains Tatyana Ali 'waiting for Spence' scene)."""
import os, sys
sys.path.insert(0, "/home/workspace/Skills/vurt-captions/scripts")
from download_cbd_social import download, OUT_DIR

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    download("a0bf9892-be48-4b18-8c9f-1b3016bdf996", "CBD_EP29_TatyanaAli.mp4")
