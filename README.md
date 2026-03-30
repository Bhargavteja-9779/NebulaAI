# NebulaAI — Autonomous AI Research Cloud

> *"Transforming idle devices into a self-organizing AI supercomputer."*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-blue)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## Problem

AI compute is expensive. Students can't afford GPUs. Research is blocked by lack of infrastructure. Meanwhile, **millions of devices sit idle** every day.

## Solution

NebulaAI turns idle devices into a **decentralized AI compute cloud** that:
- Discovers and forms compute clusters automatically
- Schedules ML workloads using AI-powered, trust-weighted allocation
- Learns from history to improve scheduling over time
- Recovers from failures in real-time
- Visualizes everything as a living compute network

---

## Architecture

```
User → AI Chat (NL prompt)
         ↓
  AI Orchestrator
  ┌──────────────────────────────────┐
  │ Planner → Scheduler → Verifier  │
  │        → Optimizer → Recovery   │
  └──────────────────────────────────┘
         ↓
  Self-Learning Scheduler
  (Trust-weighted node allocation)
         ↓
  Distributed Node Agents
  (Simulate training, stream metrics)
         ↓
  Frontend (React + React Flow)
  (Live visualization, replay, leaderboard)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion, Recharts, React Flow |
| Backend | FastAPI, SQLAlchemy, SQLite, WebSockets |
| AI Agents | 5 specialized agents (Planner, Scheduler, Verifier, Optimizer, Recovery) |
| Visualization | React Flow (Node Map), SVG animations (Cluster Formation) |
| Node Agent | Python simulator with realistic training curves |

---

## Features

| Feature | Description |
|---------|-------------|
| 🧠 AI Orchestrator | Natural language → 5-agent pipeline → auto-training |
| 🌐 Node Network Map | Live React Flow graph with trust-tier coloring |
| ⚡ Cluster Formation | Animated 5-phase cluster assembly visualization |
| 📊 Training Monitor | Live loss/accuracy curves + Digital Twin comparison |
| 🏆 Trust Leaderboard | Ranked nodes by composite trust score + badge system |
| 🔁 Experiment Replay | Timeline step-through replay of past experiments |
| 💀 Failure Simulation | Inject node failures → watch Recovery Agent reallocate |

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `nodes` | Compute node registry (IP, GPU, trust score, status) |
| `jobs` | Training jobs (model, dataset, progress, metrics) |
| `experiments` | Experiment snapshots with replay timeline |
| `trust_scores` | Rolling trust history per node |
| `scheduler_logs` | Allocation decisions with reasoning |
| `agent_logs` | 5-agent execution traces |

---

## API Endpoints

```
POST  /nodes/register        Register a compute node
GET   /nodes                 List all nodes
POST  /jobs/submit           Submit a training job
GET   /jobs/{id}             Get job status
GET   /trust/leaderboard     Ranked trust scores
GET   /scheduler/logs        Scheduler decision log
POST  /orchestrate           AI Orchestrator (NL → plan → job)
POST  /simulate/failure      Inject node failure
POST  /simulate/recovery     Recover a node
GET   /simulate/digital-twin/{id}  Real vs predicted comparison
GET   /ws                    WebSocket (live system heartbeat)
```

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### Quick Start

```bash
# 1. Clone and setup
chmod +x setup.sh && ./setup.sh

# 2. Start backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn backend.main:app --reload

# 3. Start frontend (Terminal 2)
cd frontend && npm run dev

# 4. (Optional) Start node simulator (Terminal 3)
python3 node_agent/multi_node_sim.py
```

Open **http://localhost:3000**

---

## Demo Nodes

| Node | GPU | Reliability | Trust Score | Badge |
|------|-----|------------|-------------|-------|
| Atlas | RTX 3080 | 97% | ~92 | 🏆 Pioneer |
| Orion | RTX 3060 | 91% | ~82 | ⭐ Veteran |
| Pulsar | RX 6700 | 88% | ~78 | ✅ Reliable |
| Vega | CPU | 78% | ~65 | ✅ Reliable |
| Quasar | CPU | 62% | ~42 | 🆕 Newcomer |

---

## Research Contributions

1. **Trust-Weighted Scheduling** – Novel composite scoring for heterogeneous peer nodes
2. **Multi-Agent Orchestration** – 5-agent pipeline for autonomous ML infrastructure decisions
3. **Digital Twin for Distributed Training** – Predicted vs actual runtime modeling
4. **Self-Healing Clusters** – Autonomous failure detection and workload reallocation

---

## Future Roadmap

- [ ] Real PyTorch MNIST training (via torchserve)
- [ ] P2P encryption between nodes (WireGuard)
- [ ] Federated learning support
- [ ] RL-based scheduler using historical data
- [ ] Mobile node agent (iOS/Android)
- [ ] Public node marketplace

---

## Patent Potential

**"System and Method for Autonomous AI Workload Orchestration Across Untrusted Heterogeneous Edge Devices Using Multi-Agent Trust Scoring"**

Core novelty: Dynamic trust computation + multi-agent pipeline applied to distributed ML scheduling on consumer hardware.

---

## License

MIT — Built for hackathon demonstration.
