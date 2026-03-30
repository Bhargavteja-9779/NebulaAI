#!/bin/bash
# NebulaAI — Start Worker Node
# Run this on secondary laptops to contribute compute power.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$1" ]; then
    echo "❌ Error: Missing Coordinator IP"
    echo "Usage: bash START_WORKER.sh <COORDINATOR_IP>"
    echo "Example: bash START_WORKER.sh 192.168.1.50"
    exit 1
fi

COORDINATOR_IP=$1

echo "╔══════════════════════════════════════════╗"
echo "║  NebulaAI Compute Node                   ║"
echo "╚══════════════════════════════════════════╝"
echo "📡 Connecting to coordinator at: $COORDINATOR_IP:8000"
echo ""

cd "$ROOT"
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv backend/venv
fi
source backend/venv/bin/activate
pip install -q -r distributed_training/requirements.txt

echo "🧠 Starting PyTorch Training Agent..."
python3 distributed_training/worker_agent.py --server "$COORDINATOR_IP" --port 8000
