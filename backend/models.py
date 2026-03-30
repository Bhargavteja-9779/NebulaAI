from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    ip = Column(String)
    gpu = Column(String, default="None")
    cpu_cores = Column(Integer, default=4)
    ram_gb = Column(Float, default=8.0)
    reliability = Column(Float, default=0.9)   # 0-1
    speed_score = Column(Float, default=0.8)   # 0-1
    trust_score = Column(Float, default=50.0)  # 0-100
    status = Column(String, default="offline")  # online/offline/busy
    failure_count = Column(Integer, default=0)
    jobs_completed = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    registered_at = Column(DateTime, default=datetime.utcnow)
    location = Column(String, default="Unknown")
    node_type = Column(String, default="cpu")  # cpu/gpu/tpu

    trust_scores = relationship("TrustScore", back_populates="node")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    model_type = Column(String, default="CNN")
    dataset = Column(String, default="MNIST")
    status = Column(String, default="queued")  # queued/running/completed/failed
    allocated_nodes = Column(JSON, default=[])
    progress = Column(Float, default=0.0)
    current_loss = Column(Float, default=None)
    current_accuracy = Column(Float, default=None)
    final_accuracy = Column(Float, default=None)
    epochs = Column(Integer, default=10)
    batch_size = Column(Integer, default=32)
    learning_rate = Column(Float, default=0.001)
    estimated_time = Column(Float, default=0.0)  # seconds
    actual_time = Column(Float, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=None)
    completed_at = Column(DateTime, default=None)
    loss_history = Column(JSON, default=[])
    accuracy_history = Column(JSON, default=[])
    compute_metrics = Column(JSON, default={})
    agent_plan = Column(JSON, default={})

    experiments = relationship("Experiment", back_populates="job")
    scheduler_logs = relationship("SchedulerLog", back_populates="job")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    name = Column(String)
    config = Column(JSON, default={})
    result_snapshot = Column(JSON, default={})
    timeline_events = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON, default=[])

    job = relationship("Job", back_populates="experiments")


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"))
    score = Column(Float, default=50.0)
    reliability_score = Column(Float, default=0.9)
    speed_score = Column(Float, default=0.8)
    uptime_score = Column(Float, default=0.95)
    failure_penalty = Column(Float, default=0.0)
    history = Column(JSON, default=[])  # list of {timestamp, score, event}
    updated_at = Column(DateTime, default=datetime.utcnow)
    badge = Column(String, default="Newcomer")  # Pioneer/Reliable/Veteran/Unstable

    node = relationship("Node", back_populates="trust_scores")


class SchedulerLog(Base):
    __tablename__ = "scheduler_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    decision = Column(JSON, default={})
    reasoning = Column(Text)
    allocated_nodes = Column(JSON, default=[])
    expected_time = Column(Float, default=0.0)
    actual_time = Column(Float, default=None)
    timestamp = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="scheduler_logs")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)  # planner/scheduler/verifier/optimizer/recovery
    action = Column(String)
    input_data = Column(JSON, default={})
    result = Column(JSON, default={})
    reasoning = Column(Text, default="")
    duration_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
