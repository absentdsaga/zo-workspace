#!/bin/bash
# Start ComfyUI server

cd "$(dirname "$0")/../ComfyUI"

if [ ! -d "venv" ]; then
    echo "ERROR: ComfyUI venv not found. Run setup first."
    exit 1
fi

source venv/bin/activate

echo "Starting ComfyUI server on http://localhost:8188"
echo "Access UI at: http://localhost:8188"
echo ""

python main.py --listen --port 8188
