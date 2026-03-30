"""
NebulaAI Node Agent – Simulates a compute node that:
  1. Registers with the backend
  2. Polls for tasks
  3. Simulates MNIST/CNN training
  4. Streams metrics back
"""
import sys
import os
import time
import random
import argparse
import requests

API_BASE = os.getenv("NEBULA_API", "http://localhost:8000")


class NebulaNode:
    def __init__(self, name: str, gpu: str, cpu_cores: int, ram_gb: float,
                 reliability: float, speed_score: float, location: str):
        self.name = name
        self.gpu = gpu
        self.cpu_cores = cpu_cores
        self.ram_gb = ram_gb
        self.reliability = reliability
        self.speed_score = speed_score
        self.location = location
        self.node_id = None
        self.node_type = "gpu" if gpu != "None" else "cpu"

    def register(self):
        payload = {
            "name": self.name,
            "ip": f"192.168.1.{random.randint(100, 200)}",
            "gpu": self.gpu,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "location": self.location,
            "node_type": self.node_type,
        }
        try:
            resp = requests.post(f"{API_BASE}/nodes/register", json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.node_id = data["id"]
                print(f"[{self.name}] ✅ Registered. Node ID: {self.node_id} | Trust: {data['trust_score']:.1f}")
                return True
        except Exception as e:
            print(f"[{self.name}] ❌ Registration failed: {e}")
        return False

    def heartbeat(self):
        if not self.node_id:
            return
        try:
            requests.put(f"{API_BASE}/nodes/{self.node_id}/heartbeat", timeout=3)
        except Exception:
            pass

    def simulate_training(self, epochs: int = 10, job_name: str = "task"):
        """Simulate a realistic training loop with MNIST-like loss/accuracy curves."""
        print(f"[{self.name}] 🚀 Starting training: {job_name} ({epochs} epochs)")
        loss = 2.3
        acc = 10.0
        epoch_time = (1.0 / self.speed_score) * random.uniform(0.8, 1.2)

        for ep in range(1, epochs + 1):
            # Simulate failure based on reliability
            if random.random() > self.reliability:
                print(f"[{self.name}] ⚠️  Simulated failure at epoch {ep}!")
                time.sleep(1)
                print(f"[{self.name}] 🔄 Recovering...")
                time.sleep(0.5)

            time.sleep(epoch_time * 0.5)  # Simulated compute time
            decay = 1 - (ep / epochs) ** 0.7
            loss = max(0.05, loss * (1 - 0.18 * random.uniform(0.9, 1.1)) * decay + 0.05 * (1 - decay))
            acc = min(99.0, acc + (90.0 - acc) * 0.15 * random.uniform(0.9, 1.1))

            print(
                f"[{self.name}] Epoch {ep:2d}/{epochs} | "
                f"Loss: {loss:.4f} | Acc: {acc:.2f}% | "
                f"Speed: {self.speed_score:.2f}x"
            )

        print(f"[{self.name}] ✅ Training complete! Final Acc: {acc:.2f}%")
        return {"final_loss": round(loss, 4), "final_accuracy": round(acc, 2)}

    def run(self):
        print(f"\n{'='*50}")
        print(f"  NebulaAI Node Agent: {self.name}")
        print(f"  GPU: {self.gpu} | CPU: {self.cpu_cores}c | RAM: {self.ram_gb}GB")
        print(f"  Reliability: {self.reliability:.0%} | Speed: {self.speed_score:.0%}")
        print(f"{'='*50}\n")

        if not self.register():
            print(f"[{self.name}] Exiting due to registration failure.")
            return

        heartbeat_interval = 30
        last_heartbeat = time.time()

        print(f"[{self.name}] 📡 Listening for tasks...")
        while True:
            if time.time() - last_heartbeat > heartbeat_interval:
                self.heartbeat()
                last_heartbeat = time.time()

            # Simulate receiving a task every 45-90 seconds
            wait = random.randint(45, 90)
            time.sleep(wait)

            # Randomly decide to run a task
            if random.random() < 0.7:
                epochs = random.randint(5, 15)
                self.simulate_training(epochs=epochs, job_name=f"auto-task-{random.randint(1000, 9999)}")


NODE_PROFILES = [
    {
        "name": "Atlas",
        "gpu": "NVIDIA RTX 3080",
        "cpu_cores": 16,
        "ram_gb": 32.0,
        "reliability": 0.97,
        "speed_score": 0.95,
        "location": "San Francisco, CA",
    },
    {
        "name": "Orion",
        "gpu": "NVIDIA RTX 3060",
        "cpu_cores": 12,
        "ram_gb": 16.0,
        "reliability": 0.91,
        "speed_score": 0.82,
        "location": "Austin, TX",
    },
    {
        "name": "Vega",
        "gpu": "None",
        "cpu_cores": 8,
        "ram_gb": 16.0,
        "reliability": 0.78,
        "speed_score": 0.65,
        "location": "New York, NY",
    },
    {
        "name": "Pulsar",
        "gpu": "AMD RX 6700",
        "cpu_cores": 10,
        "ram_gb": 24.0,
        "reliability": 0.88,
        "speed_score": 0.79,
        "location": "Seattle, WA",
    },
    {
        "name": "Quasar",
        "gpu": "None",
        "cpu_cores": 4,
        "ram_gb": 8.0,
        "reliability": 0.62,
        "speed_score": 0.45,
        "location": "Chicago, IL",
    },
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NebulaAI Node Agent")
    parser.add_argument("--node", default="Atlas", help="Node name to simulate")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend API URL")
    args = parser.parse_args()

    API_BASE = args.api

    profile = next((p for p in NODE_PROFILES if p["name"] == args.node), NODE_PROFILES[0])
    node = NebulaNode(**profile)
    node.run()
