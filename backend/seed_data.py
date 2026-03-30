"""Seed demo data: 5 simulated nodes + pre-built experiments."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend import models
from backend.services.trust_engine import calculate_trust_score, assign_badge
from datetime import datetime, timedelta
import json
import random

models.Base.metadata.create_all(bind=engine)

DEMO_NODES = [
    {
        "name": "Atlas",
        "ip": "192.168.1.101",
        "gpu": "NVIDIA RTX 3080",
        "cpu_cores": 16,
        "ram_gb": 32.0,
        "reliability": 0.97,
        "speed_score": 0.95,
        "status": "online",
        "location": "San Francisco, CA",
        "node_type": "gpu",
        "jobs_completed": 42,
        "failure_count": 1,
    },
    {
        "name": "Orion",
        "ip": "192.168.1.102",
        "gpu": "NVIDIA RTX 3060",
        "cpu_cores": 12,
        "ram_gb": 16.0,
        "reliability": 0.91,
        "speed_score": 0.82,
        "status": "online",
        "location": "Austin, TX",
        "node_type": "gpu",
        "jobs_completed": 28,
        "failure_count": 3,
    },
    {
        "name": "Vega",
        "ip": "192.168.1.103",
        "gpu": "None",
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "reliability": 0.78,
        "speed_score": 0.65,
        "status": "online",
        "location": "New York, NY",
        "node_type": "cpu",
        "jobs_completed": 15,
        "failure_count": 5,
    },
    {
        "name": "Pulsar",
        "ip": "192.168.1.104",
        "gpu": "AMD RX 6700",
        "cpu_cores": 10,
        "ram_gb": 24.0,
        "reliability": 0.88,
        "speed_score": 0.79,
        "status": "online",
        "location": "Seattle, WA",
        "node_type": "gpu",
        "jobs_completed": 31,
        "failure_count": 2,
    },
    {
        "name": "Quasar",
        "ip": "192.168.1.105",
        "gpu": "None",
        "cpu_cores": 4,
        "ram_gb": 8.0,
        "reliability": 0.62,
        "speed_score": 0.45,
        "status": "online",
        "location": "Chicago, IL",
        "node_type": "cpu",
        "jobs_completed": 8,
        "failure_count": 9,
    },
]


def generate_loss_curve(epochs: int, start_loss=2.3, end_loss=0.08):
    curve = []
    for i in range(epochs):
        progress = i / max(epochs - 1, 1)
        loss = start_loss * (1 - progress) ** 1.8 + end_loss + random.uniform(-0.02, 0.02)
        curve.append(round(max(end_loss, loss), 4))
    return curve


def generate_accuracy_curve(epochs: int, start_acc=10.0, end_acc=97.5):
    curve = []
    for i in range(epochs):
        progress = i / max(epochs - 1, 1)
        acc = start_acc + (end_acc - start_acc) * (1 - (1 - progress) ** 2) + random.uniform(-0.3, 0.3)
        curve.append(round(min(end_acc + 1, max(start_acc, acc)), 2))
    return curve


def seed():
    db = SessionLocal()

    # Clear existing
    db.query(models.AgentLog).delete()
    db.query(models.SchedulerLog).delete()
    db.query(models.TrustScore).delete()
    db.query(models.Experiment).delete()
    db.query(models.Job).delete()
    db.query(models.Node).delete()
    db.commit()

    # Create nodes
    node_objs = []
    for nd in DEMO_NODES:
        node = models.Node(**nd, registered_at=datetime.utcnow(), last_seen=datetime.utcnow())
        node.trust_score = calculate_trust_score(node)
        db.add(node)
        node_objs.append(node)
    db.commit()

    # Create trust scores
    for node in node_objs:
        trust = models.TrustScore(
            node_id=node.id,
            score=node.trust_score,
            reliability_score=node.reliability,
            speed_score=node.speed_score,
            uptime_score=1.0 - min(node.failure_count / 20.0, 0.5),
            failure_penalty=min(node.failure_count * 0.05, 0.5),
            badge=assign_badge(node.trust_score),
            history=[{
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "score": node.trust_score - random.uniform(0, 3),
                "event": "historical",
                "success": True
            } for i in range(10, 0, -1)],
            updated_at=datetime.utcnow()
        )
        db.add(trust)
    db.commit()

    # Create demo jobs + experiments
    demo_jobs = [
        {"name": "MNIST Baseline", "model_type": "CNN", "dataset": "MNIST", "epochs": 10,
         "status": "completed", "final_accuracy": 97.8, "nodes": ["Atlas", "Orion"]},
        {"name": "CIFAR ResNet", "model_type": "ResNet", "dataset": "CIFAR-10", "epochs": 20,
         "status": "completed", "final_accuracy": 89.3, "nodes": ["Atlas", "Pulsar", "Orion"]},
        {"name": "Text Classifier LSTM", "model_type": "LSTM", "dataset": "IMDB", "epochs": 15,
         "status": "running", "final_accuracy": None, "nodes": ["Orion", "Vega"]},
    ]

    job_objs = []
    for jd in demo_jobs:
        epochs = jd["epochs"]
        loss_hist = generate_loss_curve(epochs)
        acc_hist = generate_accuracy_curve(epochs,
                                           end_acc=jd["final_accuracy"] or 75.0)
        job = models.Job(
            name=jd["name"],
            model_type=jd["model_type"],
            dataset=jd["dataset"],
            status=jd["status"],
            allocated_nodes=jd["nodes"],
            epochs=epochs,
            progress=100.0 if jd["status"] == "completed" else 65.0,
            current_loss=loss_hist[-1],
            current_accuracy=acc_hist[-1],
            final_accuracy=jd["final_accuracy"],
            loss_history=loss_hist,
            accuracy_history=acc_hist,
            estimated_time=epochs * 12.0,
            actual_time=epochs * 11.5 if jd["status"] == "completed" else None,
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            agent_plan={
                "planner": {"model_type": jd["model_type"], "priority": "high"},
                "scheduler": {"strategy": "trust_weighted_greedy"},
                "optimizer": {"predicted_accuracy": jd["final_accuracy"] or 75.0}
            }
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_objs.append(job)

        # Experiment entry
        exp = models.Experiment(
            job_id=job.id,
            name=f"Exp: {jd['name']}",
            config={"model": jd["model_type"], "dataset": jd["dataset"], "epochs": epochs},
            result_snapshot={"final_accuracy": jd["final_accuracy"], "final_loss": loss_hist[-1]},
            timeline_events=[
                {"t": 0, "event": "Job submitted", "note": "Agent chain triggered"},
                {"t": 5, "event": "Nodes allocated", "note": f"Nodes: {jd['nodes']}"},
                {"t": 10, "event": "Training started"},
                {"t": epochs * 6, "event": f"Epoch {epochs // 2} complete",
                 "note": f"Loss: {loss_hist[epochs // 2]:.3f}"},
                {"t": epochs * 12, "event": "Training complete",
                 "note": f"Accuracy: {jd['final_accuracy']}%"}
            ],
            tags=["demo", jd["model_type"].lower()]
        )
        db.add(exp)

    db.commit()
    print("✅ NebulaAI demo data seeded successfully!")
    print(f"   Nodes: {len(node_objs)}, Jobs: {len(job_objs)}")


if __name__ == "__main__":
    seed()
