#!/bin/bash
# NebulaAI – Quick Setup Script
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      NebulaAI – Setup & Launch           ║"
echo "║  Autonomous AI Research Cloud            ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 is required. Install from https://python.org"
  exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "❌ Node.js is required. Install from https://nodejs.org"
  exit 1
fi

echo "📦 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Backend dependencies installed"

echo ""
echo "🌱 Seeding demo data..."
cd ..
python3 -m backend.seed_data
echo "✅ Demo data seeded (5 nodes, 3 experiments)"

echo ""
echo "📦 Setting up frontend..."
cd frontend
npm install --silent
echo "✅ Frontend dependencies installed"
cd ..

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup complete! Run the following:      ║"
echo "╠══════════════════════════════════════════╣"
echo "║                                          ║"
echo "║  Terminal 1 (Backend):                   ║"
echo "║  cd backend && source venv/bin/activate  ║"
echo "║  uvicorn backend.main:app --reload       ║"
echo "║                                          ║"
echo "║  Terminal 2 (Frontend):                  ║"
echo "║  cd frontend && npm run dev              ║"
echo "║                                          ║"
echo "║  Terminal 3 (Nodes, optional):           ║"
echo "║  python3 node_agent/multi_node_sim.py    ║"
echo "║                                          ║"
echo "║  Open: http://localhost:3000             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
