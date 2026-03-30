"""
FastAPI router: /dist/* endpoints for real distributed training coordination (Numpy Version)
"""
import json
import base64
import threading
import time
import logging
import numpy as np
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from distributed_training.model import NumpyModel

logger = logging.getLogger("nebulaai.dist")
router = APIRouter(prefix="/dist", tags=["Distributed Training"])

class DistState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.model        = NumpyModel()
        self.lock         = threading.Lock()
        self.workers      = {}
        self.round        = 0
        self.target_rounds= 20
        self.batches_per_round = 50
        self.learning_rate= 0.05
        self.batch_size   = 64
        self.job_id       = None
        self.status       = "idle"
        self.round_weights = {}
        self.history      = []
        self.global_loss  = None
        self.global_acc   = None
        self.total_samples= 0

state = DistState()

class RegisterRequest(BaseModel):
    name: str; ip: str; port: int = 8001; gpu: Optional[str] = None; cpu_cores: int = 4; ram_gb: float = 8.0

class UploadWeightsRequest(BaseModel):
    worker_id: int; round: int; weights_b64: str; train_loss: float; train_accuracy: float; batch_time_ms: float; cpu_percent: float; batches_done: int; n_samples: int

class StartTrainingRequest(BaseModel):
    job_id: str = "dist_job_1"; target_rounds: int = 20; batches_per_round: int = 50; learning_rate: float = 0.05; batch_size: int = 64

def weights_to_b64(model: NumpyModel) -> str:
    j = json.dumps(model.get_weights())
    return base64.b64encode(j.encode()).decode()

def b64_to_weights(b64: str) -> dict:
    return json.loads(base64.b64decode(b64.encode()).decode())

def fedavg(weights_dicts: list[dict], sample_counts: list[int]) -> dict:
    total = sum(sample_counts)
    averaged = {}
    keys = weights_dicts[0].keys()
    for k in keys:
        arrays = [np.array(wd[k]) * (n / total) for wd, n in zip(weights_dicts, sample_counts)]
        averaged[k] = np.sum(arrays, axis=0).tolist()
    return averaged

def maybe_aggregate():
    with state.lock:
        expected = [wid for wid, w in state.workers.items() if w["active"]]
        have     = list(state.round_weights.keys())
        if set(expected) != set(have) or len(expected) == 0:
            return

        order         = sorted(have)
        weights_dicts = [state.round_weights[wid]["weights_dict"] for wid in order]
        sample_counts = [state.round_weights[wid]["n_samples"]  for wid in order]

        new_wd = fedavg(weights_dicts, sample_counts)
        state.model.set_weights(new_wd)

        total_s   = sum(sample_counts)
        avg_loss  = sum(state.round_weights[w]["loss"] * state.round_weights[w]["n_samples"] for w in order) / total_s
        avg_acc   = sum(state.round_weights[w]["acc"]  * state.round_weights[w]["n_samples"] for w in order) / total_s

        state.global_loss = round(avg_loss, 4)
        state.global_acc  = round(avg_acc, 2)
        state.history.append({
            "round":    state.round,
            "loss":     state.global_loss,
            "accuracy": state.global_acc,
            "workers":  len(order),
            "ts":       time.time(),
        })

        logger.info(f"Round {state.round} aggregated — loss={state.global_loss:.4f} acc={state.global_acc:.1f}%")
        state.round_weights = {}
        state.round += 1

        if state.round >= state.target_rounds:
            state.status = "done"
            logger.info("Training complete!")
        else:
            state.status = "training"

@router.post("/register")
def register_worker(req: RegisterRequest):
    with state.lock:
        worker_id = len(state.workers)
        state.workers[worker_id] = {
            "worker_id": worker_id, "name": req.name, "ip": req.ip, "port": req.port, "gpu": req.gpu,
            "cpu_cores": req.cpu_cores, "ram_gb": req.ram_gb, "active": True, "last_seen": time.time(),
        }
        logger.info(f"Worker registered: {req.name} (id={worker_id})")
    return {"worker_id": worker_id, "status": state.status}

@router.get("/job-config")
def get_job_config(worker_id: int):
    if worker_id not in state.workers: raise HTTPException(404, "Not registered")
    state.workers[worker_id]["last_seen"] = time.time()
    total = max(len([w for w in state.workers.values() if w["active"]]), 1)
    return {
        "status": state.status, "round": state.round, "target_rounds": state.target_rounds,
        "batches_per_round": state.batches_per_round, "learning_rate": state.learning_rate,
        "batch_size": state.batch_size, "worker_id": worker_id, "total_workers": total
    }

@router.get("/model-weights")
def get_model_weights():
    return {"round": state.round, "weights_b64": weights_to_b64(state.model), "status": state.status}

@router.post("/upload-weights")
def upload_weights(req: UploadWeightsRequest):
    if state.status not in ("training", "waiting"): return {"status": state.status}
    if req.round != state.round: return {"status": "stale"}
    try: wd = b64_to_weights(req.weights_b64)
    except Exception as e: raise HTTPException(400, f"Invalid weights: {e}")

    with state.lock:
        state.workers[req.worker_id]["last_seen"] = time.time()
        state.workers[req.worker_id]["last_loss"] = req.train_loss
        state.workers[req.worker_id]["last_acc"]  = req.train_accuracy
        state.workers[req.worker_id]["cpu"]       = req.cpu_percent
        state.round_weights[req.worker_id] = {"weights_dict": wd, "n_samples": req.n_samples, "loss": req.train_loss, "acc": req.train_accuracy}

    maybe_aggregate()
    return {"round": state.round, "status": state.status}

@router.get("/training-status")
def training_status():
    workers_out = []
    for wid, w in state.workers.items():
        alive = (time.time() - w["last_seen"]) < 30
        w["active"] = alive
        workers_out.append({
            "worker_id": wid, "name": w["name"], "ip": w["ip"], "active": alive,
            "last_loss": w.get("last_loss"), "last_acc": w.get("last_acc"), "cpu": w.get("cpu")
        })

    return {
        "status": state.status, "round": state.round, "target_rounds": state.target_rounds,
        "global_loss": state.global_loss, "global_acc": state.global_acc, "workers": workers_out,
        "history": state.history[-50:], "waiting_for": [wid for wid in [w["worker_id"] for w in workers_out if w["active"]] if wid not in state.round_weights]
    }

@router.post("/start-training")
def start_training(req: StartTrainingRequest):
    if not state.workers: raise HTTPException(400, "No workers registered.")
    with state.lock:
        state.target_rounds = req.target_rounds; state.batches_per_round = req.batches_per_round
        state.learning_rate = req.learning_rate; state.batch_size = req.batch_size
        state.round = 0; state.history = []; state.round_weights = {}; state.global_loss = None; state.global_acc = None
        state.status = "training"; state.model = NumpyModel()
        for w in state.workers.values(): w["active"] = True
    return {"message": "Started", "job_id": req.job_id, "workers": len(state.workers), "rounds": req.target_rounds}

@router.post("/reset")
def reset_state():
    state.reset()
    return {"message": "Reset"}
