from datetime import datetime
from sqlalchemy.orm import Session
from .. import models


def calculate_trust_score(node: models.Node) -> float:
    """
    Trust Score Formula:
    trust = 0.4*reliability + 0.3*speed_score + 0.2*uptime_score - 0.1*failure_penalty
    Scaled to 0-100
    """
    reliability = node.reliability
    speed = node.speed_score
    uptime = 1.0 - min(node.failure_count / 20.0, 0.5)
    failure_penalty = min(node.failure_count * 0.05, 0.5)

    raw = 0.4 * reliability + 0.3 * speed + 0.2 * uptime - 0.1 * failure_penalty
    score = max(0.0, min(100.0, raw * 100))
    return round(score, 2)


def assign_badge(score: float) -> str:
    if score >= 85:
        return "Pioneer"
    elif score >= 70:
        return "Veteran"
    elif score >= 50:
        return "Reliable"
    elif score >= 30:
        return "Newcomer"
    else:
        return "Unstable"


def update_trust_score(db: Session, node_id: int, event: str, success: bool):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        return None

    if success:
        node.jobs_completed += 1
        node.reliability = min(1.0, node.reliability + 0.01)
    else:
        node.failure_count += 1
        node.reliability = max(0.1, node.reliability - 0.05)

    new_score = calculate_trust_score(node)
    node.trust_score = new_score

    trust = db.query(models.TrustScore).filter(models.TrustScore.node_id == node_id).first()
    if not trust:
        trust = models.TrustScore(node_id=node_id)
        db.add(trust)

    trust.score = new_score
    trust.reliability_score = node.reliability
    trust.speed_score = node.speed_score
    trust.uptime_score = 1.0 - min(node.failure_count / 20.0, 0.5)
    trust.failure_penalty = min(node.failure_count * 0.05, 0.5)
    trust.badge = assign_badge(new_score)
    trust.updated_at = datetime.utcnow()

    history = trust.history or []
    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "score": new_score,
        "event": event,
        "success": success
    })
    trust.history = history[-50:]  # Keep last 50 events

    db.commit()
    db.refresh(trust)
    return trust
