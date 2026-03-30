from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import asyncio
import random
from datetime import datetime
from .. import models
from ..database import get_db
from ..services.trust_engine import update_trust_score

router = APIRouter(prefix="/simulate", tags=["simulation"])


@router.post("/failure")
async def simulate_failure(node_id: int, job_id: int = None, db: Session = Depends(get_db)):
    """Simulate a node failure and trigger Recovery Agent."""
    from ..agents.agents import recovery_agent
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    recovery_result = recovery_agent.run(db, node_id, job_id)

    update_trust_score(db, node_id, "node_failure", False)

    return {
        "event": "node_failure",
        "failed_node": node.name,
        "recovery": recovery_result,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"⚠️ Node {node.name} went offline. Recovery agent reallocating workload..."
    }


@router.post("/recovery")
async def simulate_recovery(node_id: int, db: Session = Depends(get_db)):
    """Bring a node back online after simulated failure."""
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.status = "online"
    node.last_seen = datetime.utcnow()
    db.commit()

    update_trust_score(db, node_id, "node_recovered", True)

    return {
        "event": "node_recovery",
        "node": node.name,
        "trust_score": node.trust_score,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"✅ Node {node.name} is back online. Trust score recalculated."
    }


@router.get("/digital-twin/{job_id}")
def digital_twin_prediction(job_id: int, db: Session = Depends(get_db)):
    """Generate digital twin: predicted vs actual runtime comparison."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    predicted = job.estimated_time
    actual = job.actual_time or (predicted * random.uniform(0.85, 1.15))
    variance_pct = abs(actual - predicted) / max(predicted, 1) * 100

    # Simulate epoch-by-epoch twin comparison
    predicted_loss = []
    predicted_acc = []
    for i, (rl, ra) in enumerate(zip(job.loss_history or [], job.accuracy_history or [])):
        noise = random.uniform(-0.03, 0.03)
        predicted_loss.append(round(rl + noise, 4))
        predicted_acc.append(round(ra + noise * 10, 2))

    return {
        "job_id": job_id,
        "job_name": job.name,
        "predicted_time_seconds": predicted,
        "actual_time_seconds": round(actual, 1),
        "variance_percent": round(variance_pct, 2),
        "real_loss_curve": job.loss_history,
        "predicted_loss_curve": predicted_loss,
        "real_accuracy_curve": job.accuracy_history,
        "predicted_accuracy_curve": predicted_acc,
        "twin_accuracy": round(100 - variance_pct, 1),
    }
