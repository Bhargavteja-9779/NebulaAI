import time
import uuid
import asyncio
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict

from database import init_db, get_db_connection
from models import NodeRegistration, NodeHeartbeat, JobSubmission, JobMetrics
from trust_manager import add_trust, deduct_trust, add_credits
from websocket_manager import manager
from scheduler import get_best_node
from job_manager import check_node_failures, simulate_node_failure, reassign_job

app = FastAPI(title="NebulaAI Central Server")

@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Start background task to check for dead nodes
    async def failure_detector():
        while True:
            check_node_failures()
            await asyncio.sleep(5)
            
    asyncio.create_task(failure_detector())

@app.post("/register_node")
def register_node(node: NodeRegistration):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM nodes WHERE id = ?", (node.id,))
    if c.fetchone():
        # Update existing node
        c.execute("""
            UPDATE nodes SET cpu=?, ram=?, gpu=?, status='online', last_seen=? WHERE id=?
        """, (node.cpu, node.ram, node.gpu, time.time(), node.id))
    else:
        c.execute("""
            INSERT INTO nodes (id, cpu, ram, gpu, trust, status, credits, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (node.id, node.cpu, node.ram, node.gpu, 50, 'online', 0, time.time()))
    conn.commit()
    conn.close()
    print(f"[*] Node joined: {node.id} ({node.hostname})")
    return {"status": "success", "message": f"Node {node.id} registered"}

@app.post("/heartbeat")
def heartbeat(hb: NodeHeartbeat):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE nodes SET last_seen=?, status='online' WHERE id=?", (time.time(), hb.node_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/get_nodes")
def get_nodes():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM nodes")
    nodes = [dict(row) for row in c.fetchall()]
    conn.close()
    return nodes

@app.post("/submit_job")
def submit_job(job: JobSubmission):
    best_node = get_best_node()
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO jobs (id, type, status, assigned_node)
        VALUES (?, ?, ?, ?)
    """, (job.id, job.type, 'pending', best_node))
    conn.commit()
    conn.close()
    
    if best_node:
        print(f"[*] Job {job.id} assigned to node {best_node}")
        return {"status": "assigned", "node": best_node}
    else:
        print(f"[*] Job {job.id} pending, no nodes available")
        return {"status": "pending", "message": "Queueing job"}

@app.get("/get_job/{node_id}")
def get_job(node_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE assigned_node=? AND status='pending' LIMIT 1", (node_id,))
    job = c.fetchone()
    if job:
        c.execute("UPDATE jobs SET status='running' WHERE id=?", (job['id'],))
        conn.commit()
        conn.close()
        print(f"[*] Node {node_id} accepted job: {job['id']}")
        return {
            "job_id": job['id'],
            "task": job['type'],
            "epochs": 3 # Hardcoded for demo as requested
        }
    conn.close()
    return {"message": "No jobs available"}

@app.post("/job_metrics")
async def job_metrics(metrics: JobMetrics):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO metrics (job_id, epoch, accuracy, loss, node_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (metrics.job_id, metrics.epoch, metrics.accuracy, metrics.loss, metrics.node_id, time.time()))
    
    # Update job latest metrics
    c.execute("""
        UPDATE jobs SET accuracy=?, loss=?, epoch=? WHERE id=?
    """, (metrics.accuracy, metrics.loss, metrics.epoch, metrics.job_id))
    
    conn.commit()
    
    # Broadcast to demo dashboard via websockets
    metrics_data = dict(metrics)
    await manager.broadcast(metrics_data)
    print(f"[*] Metrics received for job {metrics.job_id} on epoch {metrics.epoch} (Acc: {metrics.accuracy}%)")
    
    # Check if job is finished
    if metrics.epoch >= 3:
        c.execute("UPDATE jobs SET status='completed' WHERE id=?", (metrics.job_id,))
        print(f"[*] Job {metrics.job_id} completed by {metrics.node_id}")
        conn.commit()
        add_trust(metrics.node_id, 5)
        add_credits(metrics.node_id, 20)
        
    conn.close()
    return {"status": "recorded"}

@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    job = c.fetchone()
    conn.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(job)

@app.post("/simulate_failure/{node_id}")
def fail_node(node_id: str):
    simulate_node_failure(node_id)
    return {"status": "success", "message": f"Simulated failure for {node_id}"}
    
@app.post("/demo_job")
def demo_job():
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    return submit_job(JobSubmission(id=job_id, type="mnist_training"))

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
