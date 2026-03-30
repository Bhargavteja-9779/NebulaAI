import time
from database import get_db_connection
from scheduler import get_best_node

def reassign_job(job_id: str):
    """Finds a new node for the job."""
    new_node = get_best_node()
    conn = get_db_connection()
    c = conn.cursor()
    if new_node:
        c.execute("UPDATE jobs SET assigned_node = ?, status = 'pending' WHERE id = ?", (new_node, job_id))
        print(f"[*] Reassigned job {job_id} to node {new_node}")
    else:
        c.execute("UPDATE jobs SET assigned_node = NULL, status = 'pending' WHERE id = ?", (job_id,))
        print(f"[*] Could not reassign job {job_id}, no online nodes available.")
    conn.commit()
    conn.close()
    
def check_node_failures():
    """Checks nodes for missing heartbeats (> 15 seconds) and processes failures."""
    conn = get_db_connection()
    c = conn.cursor()
    current_time = time.time()
    
    # 15 seconds missed heartbeat threshold
    limit = current_time - 15
    c.execute("SELECT id FROM nodes WHERE status = 'online' AND last_seen < ?", (limit,))
    failed_nodes = c.fetchall()
    
    failed_node_ids = [row['id'] for row in failed_nodes]
    
    for node_id in failed_node_ids:
        print(f"[!] Node failed heartbeat check: {node_id}")
        
        # Mark offline and deduct trust points
        c.execute("UPDATE nodes SET status = 'offline', trust = trust - 10 WHERE id = ?", (node_id,))
        conn.commit()
        
        # Reassign their active jobs
        c.execute("SELECT id FROM jobs WHERE assigned_node = ? AND status != 'completed'", (node_id,))
        jobs_to_reassign = c.fetchall()
        for job_row in jobs_to_reassign:
            reassign_job(job_row['id'])

    if failed_node_ids:
        conn.commit()
    conn.close()

def simulate_node_failure(node_id: str):
    """Manually flags a node as failed, used for the demo endpoint."""
    print(f"[!] Simulating failure for node {node_id}")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE nodes SET status = 'offline', trust = trust - 10 WHERE id = ?", (node_id,))
    
    c.execute("SELECT id FROM jobs WHERE assigned_node = ? AND status != 'completed'", (node_id,))
    jobs = c.fetchall()
    conn.commit()
    conn.close()
    
    for j in jobs:
        reassign_job(j['id'])
