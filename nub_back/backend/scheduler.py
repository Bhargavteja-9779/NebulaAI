from database import get_db_connection

def get_best_node():
    """
    Selects best node using: score = (cpu * 2) + (ram * 1.5) + (trust * 3)
    Returns the node_id string, or None if no nodes are available.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Fetch all online nodes
    c.execute("SELECT id, cpu, ram, trust FROM nodes WHERE status = 'online'")
    nodes = c.fetchall()
    conn.close()
    
    if not nodes:
        return None
        
    best_node = None
    best_score = -1.0
    
    for node in nodes:
        node_id = node['id']
        cpu = node['cpu']
        ram = node['ram']
        trust = node['trust']
        
        # Calculate score according to requirements
        score = (cpu * 2) + (ram * 1.5) + (trust * 3)
        if score > best_score:
            best_score = score
            best_node = node_id
            
    return best_node
