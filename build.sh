#!/bin/bash
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Building dli-nano-jp6 image..."
docker build -t dli-nano-jp6:latest .
echo ""
echo "Build complete → dli-nano-jp6:latest"
echo "Run with: ./run.sh"
