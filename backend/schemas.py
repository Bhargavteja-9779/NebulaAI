from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


class NodeRegister(BaseModel):
    name: str
    ip: str
    gpu: Optional[str] = "None"
    cpu_cores: Optional[int] = 4
    ram_gb: Optional[float] = 8.0
    location: Optional[str] = "Unknown"
    node_type: Optional[str] = "cpu"


class NodeOut(BaseModel):
    id: int
    name: str
    ip: str
    gpu: str
    cpu_cores: int
    ram_gb: float
    reliability: float
    speed_score: float
    trust_score: float
    status: str
    failure_count: int
    jobs_completed: int
    last_seen: datetime
    location: str
    node_type: str

    class Config:
        from_attributes = True


class JobSubmit(BaseModel):
    name: str
    model_type: Optional[str] = "CNN"
    dataset: Optional[str] = "MNIST"
    epochs: Optional[int] = 10
    batch_size: Optional[int] = 32
    learning_rate: Optional[float] = 0.001
    natural_language_prompt: Optional[str] = None


class JobOut(BaseModel):
    id: int
    name: str
    model_type: str
    dataset: str
    status: str
    allocated_nodes: List[Any]
    progress: float
    current_loss: Optional[float]
    current_accuracy: Optional[float]
    final_accuracy: Optional[float]
    epochs: int
    estimated_time: float
    created_at: datetime
    loss_history: List[Any]
    accuracy_history: List[Any]
    agent_plan: Dict[str, Any]

    class Config:
        from_attributes = True


class TrustOut(BaseModel):
    id: int
    node_id: int
    score: float
    reliability_score: float
    speed_score: float
    uptime_score: float
    history: List[Any]
    badge: str
    updated_at: datetime

    class Config:
        from_attributes = True


class OrchestratorRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = {}


class OrchestratorResponse(BaseModel):
    model_suggestion: str
    node_allocation: List[str]
    time_estimate: str
    accuracy_prediction: str
    agent_chain: List[Dict[str, Any]]
    reasoning: str
    job_id: Optional[int] = None


class FailureSimRequest(BaseModel):
    node_id: int
    job_id: Optional[int] = None
