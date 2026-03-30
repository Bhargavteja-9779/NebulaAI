"""
Real Distributed ML Worker Agent (Pure Numpy Version)
Downloads MNIST shard, polls coordinator, downloads global model, trains locally, uploads weights.
"""
import os
import sys
import time
import json
import base64
import argparse
import logging
import psutil
import requests

# Import shared model & dataset utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from distributed_training.model import NumpyModel
from distributed_training.dataset_utils import get_worker_shard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("worker")

class WorkerAgent:
    def __init__(self, server_ip: str, port: int):
        self.coordinator_url = f"http://{server_ip}:{port}/dist"
        self.worker_id = None
        self.name = f"Node-{os.getpid()}"
        self.model = NumpyModel()
        self.n_samples = 0
        self.data_generator_factory = None

    def register(self):
        logger.info(f"Registering with coordinator at {self.coordinator_url}...")
        try:
            res = requests.post(f"{self.coordinator_url}/register", json={
                "name": self.name,
                "ip": "127.0.0.1",
                "port": 8000 + os.getpid() % 1000,
                "cpu_cores": psutil.cpu_count(),
                "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
                "gpu": "CPU (Numpy)"
            }, timeout=5)
            res.raise_for_status()
            data = res.json()
            self.worker_id = data["worker_id"]
            logger.info(f"Registered successfully! Worker ID: {self.worker_id}")
        except Exception as e:
            logger.error(f"Failed to register: {e}")
            sys.exit(1)

    def load_dataset(self, total_workers: int):
        logger.info(f"Loading dataset shard for worker {self.worker_id}/{total_workers}...")
        self.data_generator_factory, self.n_samples = get_worker_shard(self.worker_id, total_workers, batch_size=64)
        logger.info(f"Loaded {self.n_samples} samples.")

    def download_global_weights(self) -> int:
        res = requests.get(f"{self.coordinator_url}/model-weights", timeout=10)
        res.raise_for_status()
        data = res.json()
        b64 = data["weights_b64"]
        weights_dict = json.loads(base64.b64decode(b64.encode()).decode())
        self.model.set_weights(weights_dict)
        return data["round"]

    def upload_local_weights(self, current_round: int, train_loss: float, train_acc: float, batch_time: float, batches_done: int):
        weights_dict = self.model.get_weights()
        b64 = base64.b64encode(json.dumps(weights_dict).encode()).decode()

        payload = {
            "worker_id": self.worker_id,
            "round": current_round,
            "weights_b64": b64,
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "batch_time_ms": batch_time * 1000.0,
            "cpu_percent": psutil.cpu_percent(),
            "batches_done": batches_done,
            "n_samples": self.n_samples,
        }
        res = requests.post(f"{self.coordinator_url}/upload-weights", json=payload, timeout=20)
        if res.status_code == 200:
            logger.info(f"Uploaded weights for round {current_round} successfully.")
        else:
            logger.warning(f"Upload failed: {res.text}")

    def train_local_round(self, batches_per_round: int, lr: float):
        total_loss = 0.0
        correct = 0
        total = 0
        start_time = time.time()
        batch_count = 0
        
        # We might need to iterate multiple times over dataset generator if batches_per_round is large
        while batch_count < batches_per_round:
            generator = self.data_generator_factory()
            for X, y in generator:
                probs = self.model.forward(X)
                loss = self.model.backward(X, y, lr=lr)
                
                total_loss += loss
                preds = np.argmax(probs, axis=1)
                correct += np.sum(preds == y)
                total += len(y)
                
                batch_count += 1
                if batch_count >= batches_per_round:
                    break
                    
        avg_loss = total_loss / batch_count
        avg_acc = 100. * correct / total
        batch_time = (time.time() - start_time) / batch_count
        
        return avg_loss, avg_acc, batch_time, batch_count

    def run(self):
        self.register()
        last_round_trained = -1
        
        logger.info("Worker ready. Waiting for coordinator to start training...")
        while True:
            try:
                res = requests.get(f"{self.coordinator_url}/job-config?worker_id={self.worker_id}", timeout=5)
                if res.status_code != 200:
                    time.sleep(2)
                    continue
                    
                config = res.json()
                status = config["status"]
                target_round = config["round"]
                
                if status == "idle" or status == "done":
                    time.sleep(2)
                    continue
                    
                if status == "training" and target_round > last_round_trained:
                    if self.data_generator_factory is None or config["total_workers"] != (self.n_samples and 60000//self.n_samples):
                        self.load_dataset(config["total_workers"])

                    logger.info(f"--- Starting Round {target_round}/{config['target_rounds']} ---")
                    
                    global_round = self.download_global_weights()
                    if global_round != target_round:
                        logger.warning("Downloaded weights round mismatch. Retrying next tick.")
                        time.sleep(1)
                        continue

                    loss, acc, bt, count = self.train_local_round(
                        batches_per_round=config["batches_per_round"],
                        lr=config["learning_rate"]
                    )
                    logger.info(f"Trained {count} batches. Loss: {loss:.4f}, Acc: {acc:.2f}%")
                    
                    self.upload_local_weights(target_round, loss, acc, bt, count)
                    last_round_trained = target_round

            except requests.exceptions.RequestException as e:
                logger.warning(f"Connection issue: {e}")
            except Exception as e:
                logger.error(f"Error during training loop: {e}", exc_info=True)
                
            time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NebulaAI Real PyTorch Worker")
    parser.add_argument("--server", type=str, default="127.0.0.1", help="Coordinator node IP")
    parser.add_argument("--port", type=int, default=8000, help="Coordinator port")
    args = parser.parse_args()

    worker = WorkerAgent(server_ip=args.server, port=args.port)
    worker.run()
