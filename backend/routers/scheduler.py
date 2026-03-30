from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
from ..database import get_db

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/logs")
def get_scheduler_logs(db: Session = Depends(get_db)):
    logs = db.query(models.SchedulerLog).order_by(
        models.SchedulerLog.timestamp.desc()
    ).limit(50).all()
    return [
        {
            "id": log.id,
            "job_id": log.job_id,
            "decision": log.decision,
            "reasoning": log.reasoning,
            "allocated_nodes": log.allocated_nodes,
            "expected_time": log.expected_time,
            "actual_time": log.actual_time,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]


@router.get("/agent-logs")
def get_agent_logs(db: Session = Depends(get_db)):
    logs = db.query(models.AgentLog).order_by(
        models.AgentLog.timestamp.desc()
    ).limit(100).all()
    return [
        {
            "id": log.id,
            "agent_name": log.agent_name,
            "action": log.action,
            "result": log.result,
            "reasoning": log.reasoning,
            "duration_ms": log.duration_ms,
            "success": log.success,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
