#!/bin/bash
set -e

JUPYTER_PASSWORD="${JUPYTER_PASSWORD:-dlinano}"
HOST_IP="$(hostname -I | awk '{print $1}')"

PASSWORD_HASH="$(python3 -c "from jupyter_server.auth import passwd; print(passwd('${JUPYTER_PASSWORD}'))")"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  DLI Nano AI — JetPack 6 Container  ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  JupyterLab → http://${HOST_IP}:8888"
echo "  Password   → ${JUPYTER_PASSWORD}"
echo ""

exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --allow-root \
    --no-browser \
    --ServerApp.password="${PASSWORD_HASH}" \
    --ServerApp.token='' \
    --notebook-dir=/workspace
