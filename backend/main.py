import asyncio
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .services.ws_manager import manager
from .routers import nodes, jobs, trust, scheduler, orchestrator, simulation, dist_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nebulaai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    logger.info("✅ NebulaAI backend started. DB tables ready.")
    # Start heartbeat broadcaster
    task = asyncio.create_task(heartbeat_broadcast())
    yield
    task.cancel()


app = FastAPI(
    title="NebulaAI API",
    description="Autonomous AI Research Cloud – Distributed Compute Orchestration",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(nodes.router)
app.include_router(jobs.router)
app.include_router(trust.router)
app.include_router(scheduler.router)
app.include_router(orchestrator.router)
app.include_router(simulation.router)
app.include_router(dist_router.router)

@app.get("/")
def root():
    return {
        "name": "NebulaAI",
        "tagline": "Transforming idle devices into a self-organizing AI supercomputer.",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/nodes", "/jobs", "/trust", "/scheduler", "/orchestrate", "/simulate"
        ]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "nebulaai-backend"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await manager.send_personal({"type": "pong"}, websocket)
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def heartbeat_broadcast():
    """Periodically broadcast system stats to all connected clients."""
    from .database import SessionLocal
    import random
    while True:
        try:
            await asyncio.sleep(3)
            db = SessionLocal()
            try:
                node_count = db.query(models.Node).filter(models.Node.status == "online").count()
                running_jobs = db.query(models.Job).filter(models.Job.status == "running").count()
                total_jobs = db.query(models.Job).count()
                # Get running job progress
                running = db.query(models.Job).filter(models.Job.status == "running").all()
                job_updates = [
                    {
                        "id": j.id,
                        "name": j.name,
                        "progress": j.progress,
                        "loss": j.current_loss,
                        "accuracy": j.current_accuracy,
                        "status": j.status,
                        "allocated_nodes": j.allocated_nodes,
                    }
                    for j in running
                ]
                await manager.broadcast({
                    "type": "system_heartbeat",
                    "data": {
                        "active_nodes": node_count,
                        "running_jobs": running_jobs,
                        "total_jobs": total_jobs,
                        "compute_utilization": round(random.uniform(45, 85), 1),
                        "network_throughput_mbps": round(random.uniform(100, 850), 1),
                        "job_updates": job_updates,
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                })
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
