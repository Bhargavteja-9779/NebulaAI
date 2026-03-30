"""
NebulaAI Multi-Agent System
Five specialized AI agents: Planner, Scheduler, Verifier, Optimizer, Recovery
Each agent uses structured reasoning + optional LLM integration.
"""
import time
import random
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .. import models


def _log_agent(db: Session, agent_name: str, action: str,
               input_data: dict, result: dict, reasoning: str,
               duration_ms: float, success: bool = True):
    log = models.AgentLog(
        agent_name=agent_name,
        action=action,
        input_data=input_data,
        result=result,
        reasoning=reasoning,
        duration_ms=duration_ms,
        success=success,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()


class PlannerAgent:
    """Analyzes user intent and decomposes into sub-tasks."""
    name = "planner"

    def run(self, db: Session, prompt: str, context: dict) -> Dict[str, Any]:
        start = time.time()

        keywords = prompt.lower()
        model_type = "CNN"
        dataset = "MNIST"
        epochs = 10
        priority = "normal"

        if "fast" in keywords or "quick" in keywords:
            epochs = 5
            priority = "high"
        if "accurate" in keywords or "best" in keywords:
            epochs = 20
            priority = "high"
        if "transformer" in keywords or "bert" in keywords:
            model_type = "Transformer"
        elif "resnet" in keywords:
            model_type = "ResNet"
        elif "lstm" in keywords or "rnn" in keywords:
            model_type = "LSTM"
        if "cifar" in keywords:
            dataset = "CIFAR-10"
        elif "imagenet" in keywords:
            dataset = "ImageNet"

        result = {
            "model_type": model_type,
            "dataset": dataset,
            "epochs": epochs,
            "priority": priority,
            "sub_tasks": ["allocate_nodes", "configure_training", "monitor", "verify"],
            "parallelization": "data_parallel",
        }

        reasoning = (
            f"Parsed intent: model={model_type}, dataset={dataset}, "
            f"epochs={epochs}, priority={priority}. "
            f"Decomposed into {len(result['sub_tasks'])} sub-tasks."
        )

        duration = (time.time() - start) * 1000
        _log_agent(db, self.name, "plan", {"prompt": prompt}, result, reasoning, duration)
        return {"agent": self.name, "result": result, "reasoning": reasoning}


class SchedulerAgent:
    """Allocates nodes based on trust scores and job requirements."""
    name = "scheduler"

    def run(self, db: Session, plan: dict, nodes: List[models.Node]) -> Dict[str, Any]:
        start = time.time()

        sorted_nodes = sorted(nodes, key=lambda n: n.trust_score, reverse=True)
        needed = 3 if plan.get("priority") == "high" else 2
        selected = sorted_nodes[:min(needed, len(sorted_nodes))]

        result = {
            "allocated_nodes": [n.name for n in selected],
            "node_ids": [n.id for n in selected],
            "strategy": "trust_weighted_greedy",
            "rationale": f"Selected top-{needed} nodes by trust score"
        }

        reasoning = (
            f"Evaluated {len(nodes)} online nodes. "
            f"Selected {[n.name + f'(trust={n.trust_score:.1f})' for n in selected]}. "
            f"Strategy: trust_weighted_greedy."
        )

        duration = (time.time() - start) * 1000
        _log_agent(db, self.name, "schedule", {"plan": plan}, result, reasoning, duration)
        return {"agent": self.name, "result": result, "reasoning": reasoning}


class VerifierAgent:
    """Verifies feasibility and resource adequacy."""
    name = "verifier"

    def run(self, db: Session, plan: dict, allocated_nodes: List[str]) -> Dict[str, Any]:
        start = time.time()

        nodes = db.query(models.Node).filter(models.Node.name.in_(allocated_nodes)).all()
        total_ram = sum(n.ram_gb for n in nodes)
        avg_reliability = sum(n.reliability for n in nodes) / max(len(nodes), 1)
        feasible = len(nodes) >= 1 and avg_reliability > 0.5

        result = {
            "feasible": feasible,
            "total_ram_gb": total_ram,
            "avg_reliability": round(avg_reliability, 3),
            "verification_passed": feasible,
            "warnings": [] if avg_reliability > 0.8 else ["Some nodes have low reliability"]
        }

        reasoning = (
            f"Verified {len(nodes)} nodes. Total RAM: {total_ram}GB. "
            f"Avg reliability: {avg_reliability:.2%}. Feasible: {feasible}."
        )

        duration = (time.time() - start) * 1000
        _log_agent(db, self.name, "verify", {"plan": plan, "nodes": allocated_nodes},
                   result, reasoning, duration)
        return {"agent": self.name, "result": result, "reasoning": reasoning}


class OptimizerAgent:
    """Optimizes hyperparameters and training configuration."""
    name = "optimizer"

    def run(self, db: Session, plan: dict, node_count: int) -> Dict[str, Any]:
        start = time.time()

        lr = 0.001
        batch_size = 32
        epochs = plan.get("epochs", 10)

        if node_count >= 3:
            batch_size = 64
            lr = 0.01
        elif node_count == 1:
            batch_size = 16

        if plan.get("priority") == "high":
            lr *= 1.5

        predicted_accuracy = min(95.0, 70.0 + epochs * 1.2 + node_count * 1.5)
        predicted_time = max(30, epochs * 12 / max(node_count * 0.5, 1))

        result = {
            "optimized_lr": round(lr, 4),
            "optimized_batch_size": batch_size,
            "optimized_epochs": epochs,
            "predicted_accuracy": round(predicted_accuracy, 1),
            "predicted_time_seconds": round(predicted_time, 1),
            "optimization_strategy": "adaptive_scaling"
        }

        reasoning = (
            f"With {node_count} nodes, optimal batch_size={batch_size}, lr={lr:.4f}. "
            f"Predicted accuracy: {predicted_accuracy:.1f}%, time: {predicted_time:.0f}s."
        )

        duration = (time.time() - start) * 1000
        _log_agent(db, self.name, "optimize", {"plan": plan, "node_count": node_count},
                   result, reasoning, duration)
        return {"agent": self.name, "result": result, "reasoning": reasoning}


class RecoveryAgent:
    """Handles node failures and reallocates workloads."""
    name = "recovery"

    def run(self, db: Session, failed_node_id: int, job_id: int = None) -> Dict[str, Any]:
        start = time.time()

        failed_node = db.query(models.Node).filter(models.Node.id == failed_node_id).first()
        if failed_node:
            failed_node.status = "offline"
            failed_node.failure_count += 1
            db.commit()

        # Find best replacement
        candidates = db.query(models.Node).filter(
            models.Node.id != failed_node_id,
            models.Node.status == "online"
        ).order_by(models.Node.trust_score.desc()).limit(2).all()

        replacement_names = [n.name for n in candidates]

        result = {
            "failed_node": failed_node.name if failed_node else f"node_{failed_node_id}",
            "recovery_action": "reallocate",
            "replacement_nodes": replacement_names,
            "estimated_overhead_seconds": random.randint(5, 15),
            "job_id": job_id
        }

        reasoning = (
            f"Node {result['failed_node']} went offline. "
            f"Reallocating to {replacement_names}. "
            f"Job continuity maintained with ~{result['estimated_overhead_seconds']}s overhead."
        )

        duration = (time.time() - start) * 1000
        _log_agent(db, self.name, "recover",
                   {"failed_node_id": failed_node_id, "job_id": job_id},
                   result, reasoning, duration)
        return {"agent": self.name, "result": result, "reasoning": reasoning}


planner_agent = PlannerAgent()
scheduler_agent = SchedulerAgent()
verifier_agent = VerifierAgent()
optimizer_agent = OptimizerAgent()
recovery_agent = RecoveryAgent()
