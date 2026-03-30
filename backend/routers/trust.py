from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/trust", tags=["trust"])


@router.get("", response_model=list[schemas.TrustOut])
def get_trust_scores(db: Session = Depends(get_db)):
    scores = db.query(models.TrustScore).all()
    return scores


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    nodes = db.query(models.Node).order_by(models.Node.trust_score.desc()).all()
    result = []
    for rank, node in enumerate(nodes, 1):
        trust = db.query(models.TrustScore).filter(
            models.TrustScore.node_id == node.id
        ).first()
        result.append({
            "rank": rank,
            "node_id": node.id,
            "name": node.name,
            "trust_score": node.trust_score,
            "badge": trust.badge if trust else "Newcomer",
            "jobs_completed": node.jobs_completed,
            "failure_count": node.failure_count,
            "reliability": node.reliability,
            "speed_score": node.speed_score,
            "last_seen": node.last_seen.isoformat() if node.last_seen else None,
            "history": trust.history[-10:] if trust else [],
        })
    return result
