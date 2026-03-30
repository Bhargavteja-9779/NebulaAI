#!/bin/bash
# NebulaAI — Start Coordinator Node
# Run this on your main laptop/PC.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║  NebulaAI Coordinator (Main Node)        ║"
echo "╚══════════════════════════════════════════╝"

# Get Local IP (macOS/Linux compatible)
if command -v ip >/dev/null 2>&1; then
    LOCAL_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
else
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
fi

echo ""
echo "📡 Coordinator IP: $LOCAL_IP"
echo "Tell your worker laptops to connect to: $LOCAL_IP"
echo "Example:"
echo "  bash START_WORKER.sh $LOCAL_IP"
echo ""

cd "$ROOT"
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
fi
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt
pip install -q -r distributed_training/requirements.txt

echo "🚀 Starting FastAPI Cloud Coordinator..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000
