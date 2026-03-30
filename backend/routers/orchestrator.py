from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import random
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..agents.agents import (
    planner_agent, scheduler_agent, verifier_agent,
    optimizer_agent, recovery_agent
)
from ..services.scheduler_service import scheduler as sched_service

router = APIRouter(prefix="/orchestrate", tags=["orchestrator"])


@router.post("", response_model=schemas.OrchestratorResponse)
def orchestrate(request: schemas.OrchestratorRequest,
                background_tasks: BackgroundTasks,
                db: Session = Depends(get_db)):
    """
    AI Orchestrator: chains all 5 agents to process a natural-language job request.
    Returns model suggestion, node allocation, time estimate, and accuracy prediction.
    """
    prompt = request.prompt
    agent_chain = []

    # Step 1: Planner
    plan_result = planner_agent.run(db, prompt, request.context)
    agent_chain.append({
        "step": 1,
        "agent": "Planner",
        "icon": "🧠",
        "action": "Analyzed intent & decomposed tasks",
        "reasoning": plan_result["reasoning"],
        "result_summary": f"Model: {plan_result['result']['model_type']}, "
                         f"Epochs: {plan_result['result']['epochs']}",
        "duration_ms": random.randint(120, 350),
    })

    # Step 2: Scheduler
    online_nodes = db.query(models.Node).filter(models.Node.status == "online").all()
    sched_result = scheduler_agent.run(db, plan_result["result"], online_nodes)
    allocated_names = sched_result["result"]["allocated_nodes"]
    agent_chain.append({
        "step": 2,
        "agent": "Scheduler",
        "icon": "📡",
        "action": "Allocated optimal nodes",
        "reasoning": sched_result["reasoning"],
        "result_summary": f"Allocated: {', '.join(allocated_names)}",
        "duration_ms": random.randint(80, 200),
    })

    # Step 3: Verifier
    ver_result = verifier_agent.run(db, plan_result["result"], allocated_names)
    agent_chain.append({
        "step": 3,
        "agent": "Verifier",
        "icon": "✅",
        "action": "Verified feasibility & resources",
        "reasoning": ver_result["reasoning"],
        "result_summary": f"Feasible: {ver_result['result']['feasible']}, "
                         f"RAM: {ver_result['result']['total_ram_gb']}GB",
        "duration_ms": random.randint(60, 150),
    })

    # Step 4: Optimizer
    opt_result = optimizer_agent.run(db, plan_result["result"], len(allocated_names))
    agent_chain.append({
        "step": 4,
        "agent": "Optimizer",
        "icon": "⚡",
        "action": "Tuned hyperparameters",
        "reasoning": opt_result["reasoning"],
        "result_summary": f"LR: {opt_result['result']['optimized_lr']}, "
                         f"Batch: {opt_result['result']['optimized_batch_size']}",
        "duration_ms": random.randint(90, 250),
    })

    # Auto-submit job
    model_type = plan_result["result"]["model_type"]
    epochs = plan_result["result"]["epochs"]
    est_time = opt_result["result"]["predicted_time_seconds"]
    pred_acc = opt_result["result"]["predicted_accuracy"]

    nodes_objs = db.query(models.Node).filter(models.Node.name.in_(allocated_names)).all()
    job = models.Job(
        name=f"Job: {prompt[:40]}",
        model_type=model_type,
        dataset=plan_result["result"]["dataset"],
        epochs=epochs,
        batch_size=opt_result["result"]["optimized_batch_size"],
        learning_rate=opt_result["result"]["optimized_lr"],
        allocated_nodes=allocated_names,
        estimated_time=est_time,
        status="queued",
        agent_plan={
            "planner": plan_result["result"],
            "scheduler": sched_result["result"],
            "verifier": ver_result["result"],
            "optimizer": opt_result["result"],
        }
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Import inline to avoid circular
    from ..routers.jobs import simulate_training
    background_tasks.add_task(simulate_training, job.id)

    time_str = f"{int(est_time // 60)}m {int(est_time % 60)}s" if est_time >= 60 else f"{int(est_time)}s"

    return schemas.OrchestratorResponse(
        model_suggestion=model_type,
        node_allocation=allocated_names,
        time_estimate=time_str,
        accuracy_prediction=f"{pred_acc:.1f}%",
        agent_chain=agent_chain,
        reasoning=(
            f"Based on your request '{prompt}', I deployed a {model_type} architecture. "
            f"Selected {len(allocated_names)} nodes using trust-weighted allocation. "
            f"Estimated {pred_acc:.1f}% accuracy in {time_str}."
        ),
        job_id=job.id,
    )


@router.get("/experiments")
def get_experiments(db: Session = Depends(get_db)):
    exps = db.query(models.Experiment).order_by(models.Experiment.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "job_id": e.job_id,
            "name": e.name,
            "config": e.config,
            "result_snapshot": e.result_snapshot,
            "timeline_events": e.timeline_events,
            "tags": e.tags,
            "created_at": e.created_at.isoformat(),
        }
        for e in exps
    ]
