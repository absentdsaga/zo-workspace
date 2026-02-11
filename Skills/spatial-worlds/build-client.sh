#!/bin/bash
cd /home/workspace/Skills/spatial-worlds
echo "Building client..."
bun build scripts/client/main-iso.ts --outdir=dist --target=browser
echo "✅ Build complete: dist/main-iso.js"
