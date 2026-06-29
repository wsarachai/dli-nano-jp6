#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop any existing instance
docker rm -f dli-nano-jp6 2>/dev/null || true

docker run --runtime nvidia \
    -it --rm \
    --network host \
    --name dli-nano-jp6 \
    --volume "${SCRIPT_DIR}/data:/workspace/data" \
    --volume /tmp/argus_socket:/tmp/argus_socket \
    --device /dev/video0 \
    -e JUPYTER_PASSWORD=dlinano \
    dli-nano-jp6:latest
