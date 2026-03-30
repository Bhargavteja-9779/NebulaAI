from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..services.trust_engine import calculate_trust_score, assign_badge, update_trust_score

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("/register", response_model=schemas.NodeOut)
def register_node(node_data: schemas.NodeRegister, db: Session = Depends(get_db)):
    existing = db.query(models.Node).filter(models.Node.name == node_data.name).first()
    if existing:
        existing.ip = node_data.ip
        existing.status = "online"
        existing.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    node = models.Node(
        name=node_data.name,
        ip=node_data.ip,
        gpu=node_data.gpu,
        cpu_cores=node_data.cpu_cores,
        ram_gb=node_data.ram_gb,
        location=node_data.location,
        node_type=node_data.node_type,
        status="online",
        registered_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
    )
    node.trust_score = calculate_trust_score(node)
    db.add(node)
    db.commit()
    db.refresh(node)

    trust = models.TrustScore(
        node_id=node.id,
        score=node.trust_score,
        badge=assign_badge(node.trust_score),
        reliability_score=node.reliability,
        speed_score=node.speed_score,
    )
    db.add(trust)
    db.commit()
    return node


@router.get("", response_model=list[schemas.NodeOut])
def get_nodes(db: Session = Depends(get_db)):
    return db.query(models.Node).all()


@router.get("/{node_id}", response_model=schemas.NodeOut)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/{node_id}/heartbeat")
def heartbeat(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.last_seen = datetime.utcnow()
    node.status = "online"
    db.commit()
    return {"status": "ok", "node": node.name}
