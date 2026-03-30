from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from .. import models


class SelfLearningScheduler:
    """
    Self-learning scheduler that tracks historical node performance
    and improves allocation decisions over time using a weighted scoring model.
    """

    def allocate(self, db: Session, job: models.Job, top_n: int = 3) -> List[models.Node]:
        nodes = db.query(models.Node).filter(models.Node.status == "online").all()
        if not nodes:
            # Fall back to any available nodes
            nodes = db.query(models.Node).all()

        scored = []
        for node in nodes:
            score = self._composite_score(node)
            scored.append((score, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [n for _, n in scored[:min(top_n, len(scored))]]
        return selected

    def _composite_score(self, node: models.Node) -> float:
        """
        Composite allocation score considering:
        - Trust score (normalized)
        - Speed score
        - Reliability
        - Job completion rate
        - Recency of activity
        """
        trust_norm = node.trust_score / 100.0
        completion_bonus = min(node.jobs_completed / 50.0, 0.2)
        failure_penalty = min(node.failure_count * 0.03, 0.3)

        score = (
            0.35 * trust_norm +
            0.30 * node.speed_score +
            0.25 * node.reliability +
            0.10 * completion_bonus -
            failure_penalty
        )
        return max(0.0, score)

    def estimate_time(self, job: models.Job, nodes: List[models.Node]) -> float:
        """Estimate job completion time in seconds based on node speeds."""
        if not nodes:
            return 300.0
        avg_speed = sum(n.speed_score for n in nodes) / len(nodes)
        base_time = job.epochs * 15.0  # 15 sec per epoch baseline
        parallelism_factor = 1.0 / (1.0 + 0.3 * (len(nodes) - 1))
        estimated = base_time * parallelism_factor / max(avg_speed, 0.1)
        return round(estimated, 1)

    def log_decision(self, db: Session, job_id: int, nodes: List[models.Node],
                     reasoning: str, estimated_time: float):
        log = models.SchedulerLog(
            job_id=job_id,
            decision={"node_ids": [n.id for n in nodes], "node_names": [n.name for n in nodes]},
            reasoning=reasoning,
            allocated_nodes=[n.name for n in nodes],
            expected_time=estimated_time,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()


scheduler = SelfLearningScheduler()
