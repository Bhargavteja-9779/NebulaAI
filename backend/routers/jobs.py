from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import asyncio
import random
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..services.scheduler_service import scheduler
from ..services.trust_engine import update_trust_score

router = APIRouter(prefix="/jobs", tags=["jobs"])


async def simulate_training(job_id: int):
    """Background task: simulates real training progress updates."""
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        epochs = job.epochs
        loss = 2.3
        acc = 10.0
        loss_hist = []
        acc_hist = []

        for ep in range(epochs):
            await asyncio.sleep(0.8)  # ~0.8s per simulated epoch
            decay = 1 - (ep / epochs) ** 0.7
            loss = max(0.05, loss * (1 - 0.18 * random.uniform(0.9, 1.1)) * decay + 0.05 * (1 - decay))
            acc = min(99.0, acc + (90.0 - acc) * 0.15 * random.uniform(0.9, 1.1))

            loss = round(loss, 4)
            acc = round(acc, 2)
            loss_hist.append(loss)
            acc_hist.append(acc)

            job = db.query(models.Job).filter(models.Job.id == job_id).first()
            job.progress = round((ep + 1) / epochs * 100, 1)
            job.current_loss = loss
            job.current_accuracy = acc
            job.loss_history = loss_hist
            job.accuracy_history = acc_hist
            db.commit()

        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        job.status = "completed"
        job.final_accuracy = round(acc, 2)
        job.completed_at = datetime.utcnow()
        db.commit()

        # Update trust scores for allocated nodes
        for node_name in (job.allocated_nodes or []):
            node = db.query(models.Node).filter(models.Node.name == node_name).first()
            if node:
                update_trust_score(db, node.id, "job_completed", True)
    finally:
        db.close()


@router.post("/submit", response_model=schemas.JobOut)
def submit_job(job_data: schemas.JobSubmit, background_tasks: BackgroundTasks,
               db: Session = Depends(get_db)):
    nodes = db.query(models.Node).filter(models.Node.status == "online").all()
    selected = scheduler.allocate(db, None, top_n=3)
    est_time = scheduler.estimate_time(job_data, selected) if selected else 120.0

    job = models.Job(
        name=job_data.name,
        model_type=job_data.model_type,
        dataset=job_data.dataset,
        epochs=job_data.epochs,
        batch_size=job_data.batch_size,
        learning_rate=job_data.learning_rate,
        allocated_nodes=[n.name for n in selected],
        estimated_time=est_time,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    scheduler.log_decision(db, job.id, selected,
                          f"Auto-allocated {len(selected)} nodes via trust-weighted scheduler",
                          est_time)

    background_tasks.add_task(simulate_training, job.id)
    return job


@router.get("", response_model=list[schemas.JobOut])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
