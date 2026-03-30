import os
import time
import socket
import psutil
import requests
import threading
import uuid
import sys
import itertools
from requests.exceptions import RequestException

from config import SERVER_URL
from trainer import train_mnist_job

# Generate unique node ID
NODE_ID = f"node_{socket.gethostname()}_{uuid.uuid4().hex[:4]}"
HOSTNAME = socket.gethostname()

def register_node():
    """Registers this node with the central server."""
    cpu_cores = psutil.cpu_count(logical=True)
    ram_gb = round(psutil.virtual_memory().total / 1e9, 2)
    # Simple GPU check
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available() or torch.backends.mps.is_available()
    except ImportError:
        pass

    payload = {
        "id": NODE_ID,
        "cpu": cpu_cores,
        "ram": ram_gb,
        "gpu": gpu_available,
        "hostname": HOSTNAME
    }
    
    try:
        print(f"[*] Registering node {NODE_ID} (CPU: {cpu_cores}, RAM: {ram_gb}GB, GPU: {gpu_available})")
        resp = requests.post(f"{SERVER_URL}/register_node", json=payload, timeout=5)
        resp.raise_for_status()
        print("[*] Successfully registered with central server.")
        return True
    except RequestException as e:
        print(f"[!] Registration failed: {e}. Retrying in 5 seconds...")
        return False

def send_heartbeat():
    """Sends a heartbeat every 5 seconds in a background thread."""
    while True:
        try:
            requests.post(f"{SERVER_URL}/heartbeat", json={"node_id": NODE_ID}, timeout=3)
        except RequestException:
            # Silent fail so it doesn't spam logs if server is down temporarily
            pass
        time.sleep(5)

def check_for_job():
    """Polls the central server for assigned jobs."""
    try:
        resp = requests.get(f"{SERVER_URL}/get_job/{NODE_ID}", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "job_id" in data:
            return data
    except RequestException:
        pass
    return None

def main():
    print("="*40)
    print(f" NebulaAI Node Agent: {NODE_ID}")
    print("="*40)
    
    # Wait for successful registration before doing anything else
    while not register_node():
        time.sleep(5)
        
    # Start background heartbeat thread
    hb_thread = threading.Thread(target=send_heartbeat, daemon=True)
    hb_thread.start()
    
    print("[*] Node agent active. Polling for jobs...")
    
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    
    # Main polling and execution loop
    try:
        while True:
            # Animated spinner
            sys.stdout.write(f"\r\033[96m{next(spinner)} Polling Central Server for jobs...\033[0m")
            sys.stdout.flush()
            
            job = check_for_job()
            if job:
                # Clear spinner line
                sys.stdout.write("\r\033[K")
                sys.stdout.flush()
                
                job_id = job['job_id']
                epochs = job.get('epochs', 3)
                task_type = job.get('task', 'mnist_training')
                
                print(f"[*] 🚀 Received job {job_id} ({task_type})")
                try:
                    if task_type in ["mnist_training", "mnist"]:
                        train_mnist_job(job_id, epochs, NODE_ID)
                    else:
                        print(f"[!] Unknown task type: {task_type}")
                except Exception as e:
                    print(f"[!] Training failed: {e}")
            
            # Polling delay
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Node agent shutting down.")

if __name__ == "__main__":
    main()
