# NebulaAI – Perfect Demo Flow Script

**Total Time: 3 minutes**

---

## Slide 0: Context Setup (before starting)

Have these tabs open:
1. NebulaAI frontend: `http://localhost:3000`
2. API docs: `http://localhost:8000/docs`

Backend, frontend, and seed data must be running.

---

## [0:00–0:30] Problem Statement (live, talking while showing dashboard)

> _"This is NebulaAI. What you're looking at is a live network of 5 compute nodes — student laptops — forming a distributed AI supercomputer."_

Show: **Dashboard** — active nodes, running jobs, accuracy counter

> _"AI training costs $3/hour on AWS. Most students can't afford it. But every laptop has spare compute. We built the infrastructure to harness it."_

---

## [0:30–0:60] AI Orchestrator Demo

Navigate to: **AI Orchestrator** tab

Type: `"Train the best model as fast as possible"`

> _"I just described my goal in plain English. Watch what happens."_

Wait ~3 seconds for response. Point to:
- "Planner Agent: analyzed intent, selected CNN architecture"
- "Scheduler Agent: allocated Atlas + Orion (highest trust)"
- "Optimizer Agent: tuned LR to 0.01, batch size 64"

Expand one agent's reasoning to show depth.

> _"Five AI agents collaborated to plan, schedule, verify, and optimize this job — autonomously."_

---

## [1:00–1:30] Node Network + Training

Navigate to: **Node Map**

> _"Here's our cluster topology. Color = trust score. Green = Pioneer. The edges show live data flow between nodes."_

Point out Atlas (gold), Quasar (red/yellow).

Navigate to: **Training Monitor**

> _"The training job just started. Live loss is dropping. Accuracy is climbing. This is running right now across the cluster."_

Click "Generate Twin":

> _"Our Digital Twin predicted the training time to within 3%. That's our innovation — a real-time runtime model."_

---

## [1:30–2:00] Failure Simulation (Most Impressive Part)

Navigate to: **Node Map**

Click "Fail" on Quasar.

> _"I just simulated a node crash. Watch what happens."_

Point to the red banner: "⚠️ Quasar went offline. Recovery agent reallocating..."

> _"Our Recovery Agent detected the failure instantly. It reallocated the workload to the next-best available nodes. Job continues — no data lost."_

Navigate to: **Trust Leaderboard**

> _"Quasar's trust score just dropped. In a real system, repeated failures permanently demote a node. The cluster learns to avoid unreliable nodes."_

---

## [2:00–2:30] Cluster Formation Animation

Navigate to: **Cluster Formation**

Click "Simulate Cluster Formation"

> _"This is the magic — nodes discovering each other, exchanging capability manifests, verifying trust, electing a governor, and forming a mesh topology. All automatic. All in seconds."_

Point to Atlas with 👑 crown:

> _"Atlas — our highest-trust node — was elected cluster governor. It's responsible for job coordination and health monitoring."_

---

## [2:30–3:00] Vision + Close

Navigate back to: **Dashboard**

> _"What you just saw is just the beginning. 

> 10,000 students sharing idle compute = 15 petaFLOPS — that's a top-50 supercomputer, built from nothing.

> We're not building another app. We're building infrastructure intelligence.

> The student version of Google Cloud AI.

> NebulaAI — thank you."_

---

## Backup: Experiment Replay (if time allows)

Navigate to: **Experiment Replay**

Click the MNIST Baseline experiment.

Click "Play" on the timeline.

> _"Every experiment is recorded and replayable. You can step through the exact allocation decisions, metric evolution, and agent reasoning. This is how teams learn from past runs."_

---

## Emergency Recovery

| If backend is down | `cd backend && uvicorn backend.main:app --reload` |
|---|---|
| If no data shows | `python3 -m backend.seed_data` |
| If charts blank | Refresh page — WebSocket reconnects in 3s |
| If job not progressing | Submit new job via AI Chat |
