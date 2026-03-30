#!/usr/bin/env python3
"""
NebulaAI Multi-Node Simulator
Spawns 5 node agents with different profiles to simulate a real distributed cluster.
"""
import subprocess
import sys
import time
import os

NODES = ["Atlas", "Orion", "Vega", "Pulsar", "Quasar"]
API_URL = os.getenv("NEBULA_API", "http://localhost:8000")
AGENT_SCRIPT = os.path.join(os.path.dirname(__file__), "agent.py")


def main():
    print("=" * 60)
    print("  NebulaAI Multi-Node Cluster Simulator")
    print("  Spawning 5 compute nodes...")
    print("=" * 60)

    processes = []
    for node_name in NODES:
        time.sleep(0.5)  # Stagger startup
        proc = subprocess.Popen(
            [sys.executable, AGENT_SCRIPT, "--node", node_name, "--api", API_URL],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append((node_name, proc))
        print(f"  ✅ Started node: {node_name} (PID: {proc.pid})")

    print(f"\n  {len(NODES)} nodes running. Press Ctrl+C to stop.\n")

    try:
        while True:
            for name, proc in processes:
                line = proc.stdout.readline()
                if line:
                    print(line.rstrip())
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all nodes...")
        for name, proc in processes:
            proc.terminate()
            print(f"  Stopped: {name}")


if __name__ == "__main__":
    main()
