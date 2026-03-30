#!/bin/bash
# NebulaAI – Full Stack Startup Script
# Usage: bash run.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      NebulaAI – Starting All Services    ║"
echo "╚══════════════════════════════════════════╝"

# Kill any existing processes
echo "🔪 Stopping old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

# ── Backend ────────────────────────────────────
echo ""
echo "🚀 Starting backend on http://localhost:8000"
cd "$ROOT"

# Install backend deps if needed
if [ ! -d "$ROOT/backend/venv" ]; then
  echo "  Installing Python deps..."
  python3 -m venv "$ROOT/backend/venv"
fi
source "$ROOT/backend/venv/bin/activate"
pip install -q -r "$ROOT/backend/requirements.txt"

# Seed database
echo "🌱 Seeding demo data..."
python3 -m backend.seed_data > /dev/null 2>&1 && echo "  ✅ Demo data ready"

# Start backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/nebulaai_backend.log 2>&1 &
BACKEND_PID=$!
echo "  ✅ Backend PID: $BACKEND_PID"
sleep 2

# Verify backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
  echo "  ✅ Backend is healthy"
else
  echo "  ⚠️  Backend check failed — see /tmp/nebulaai_backend.log"
fi

# ── Frontend ───────────────────────────────────
echo ""
echo "🎨 Starting frontend on http://localhost:3000"
cd "$ROOT/frontend"

# Install npm deps if needed
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "  Installing npm deps..."
  npm install --silent
fi

# Start Vite using the local binary
node "$ROOT/frontend/node_modules/vite/bin/vite.js" --port 3000 --host 0.0.0.0 > /tmp/nebulaai_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  ✅ Frontend PID: $FRONTEND_PID"
sleep 3

if curl -s http://localhost:3000 > /dev/null 2>&1; then
  echo "  ✅ Frontend is serving"
else
  echo "  ⚠️  Frontend check failed — see /tmp/nebulaai_frontend.log"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  🌐 NebulaAI is ready!                   ║"
echo "║  Open: http://localhost:3000             ║"
echo "║                                          ║"
echo "║  Logs:                                   ║"
echo "║    Backend:  /tmp/nebulaai_backend.log   ║"
echo "║    Frontend: /tmp/nebulaai_frontend.log  ║"
echo "║                                          ║"
echo "║  Press Ctrl+C to stop                   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Keep running, show backend output
wait $BACKEND_PID
