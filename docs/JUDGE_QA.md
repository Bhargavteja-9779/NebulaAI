# NebulaAI – Judge Q&A

## Q: Why is this different from AWS or Google Cloud?

**A:** AWS and Google Cloud are centralized, corporate-owned infrastructure that costs money.

NebulaAI is a **peer-to-peer, community-owned compute network.**

Key differences:
- **Cost**: Students contribute idle compute → earn credits → use AI for free
- **Architecture**: Decentralized edge cluster vs monolithic cloud datacenter
- **Model**: Community-owned, not SaaS
- **Novelty**: Self-organizing topology + multi-agent orchestration — no cloud provider does this
- **Latency**: Edge nodes can be physically co-located with researchers

We're not competing with AWS. We're the "Wikipedia of compute" — user-contributed.

---

## Q: What about security? Any node could be malicious?

**A:** Great question. Three layers of defense:

1. **Trust Engine**: Every node gets a dynamic trust score based on reliability, speed, uptime, and historical job success. Malicious or unreliable nodes quickly drop to "Unstable" — excluded from allocation.

2. **Job Isolation**: No node sees the full model or dataset — only its assigned chunk. Data partitioning prevents any single node from reconstructing training data.

3. **Verifier Agent**: Our Verifier Agent cross-checks outputs from multiple nodes. Outlier detection flags nodes returning anomalous gradients.

**Roadmap**: WireGuard VPN tunnels between nodes, homomorphic encryption for sensitive workloads, hardware attestation.

---

## Q: How does this scale?

**A:** Horizontally — by design.

Each component is stateless and scales independently:
- Backend: Horizontally scalable behind a load balancer
- Node Discovery: mDNS + DHT (like BitTorrent peer discovery)
- Scheduling: Consistent hashing distributes job assignment
- Trust DB: Replicated across governor nodes

At 10,000 nodes → ~15 petaFLOPS. At 100,000 nodes → matches a top-5 supercomputer.

The architecture mirrors what Google does with Borg/GKE — but decentralized.

---

## Q: What's novel about this? Can't I just use BOINC or Folding@Home?

**A:** BOINC is for predefined scientific tasks. Folding@Home is domain-specific.

NebulaAI is fundamentally different:

1. **Multi-Agent AI Orchestration**: A 5-agent AI pipeline that dynamically plans, schedules, verifies, optimizes, and recovers — autonomously. No human-in-the-loop.

2. **Self-Learning Scheduler**: Unlike static schedulers, ours improves allocation decisions using historical node performance data.

3. **Trust-Weighted Dynamic Allocation**: Our composite trust score allows fine-grained reliability discrimination — not just "node is up/down."

4. **Digital Twin**: Runtime prediction via a physics-inspired twin model — unique to NebulaAI.

5. **Natural Language Interface**: Tell the system what you want in plain English. Unprecedented in distributed compute platforms.

---

## Q: What's the research contribution?

**A:** Three publishable contributions:

1. **Trust Scoring for Heterogeneous Edge Compute** (novel formula + evaluation)
2. **Multi-Agent Orchestration for Distributed ML Workloads** (LLM-agent collaboration framework)
3. **Digital Twin Modeling for Distributed Training Runtime Prediction**

We are in discussions with two professors about turning this into a paper submission for MLSys 2025.

---

## Q: Why would nodes join? What's the incentive?

**A:** Compute credits (like Bitcoin mining, but for AI):

- Share idle compute → earn credits
- Spend credits on NebulaAI compute when you need it
- Top nodes earn Pioneer/Veteran badges visible on the global leaderboard

It's a compute economy. Students who can't afford GPUs can earn access by contributing their laptop's idle time.

---

## Q: What's your business model?

**A:** Three tiers:

1. **Free (Community)**: Community nodes, queued jobs — like GitHub Free
2. **Pro ($29/mo)**: Priority scheduling, private experiments, dedicated nodes
3. **Institution License**: University/lab clusters, custom SLAs, compliance

Revenue share with top-contributing nodes (compute miners).

Long-term: compute marketplace where labs lease excess university GPU capacity to researchers globally.
