import sqlite3
from sqlite3 import Connection
from config import DATABASE_URL

def get_db_connection() -> Connection:
    """Returns a connection to the SQLite database."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # nodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            cpu INTEGER,
            ram REAL,
            gpu BOOLEAN,
            trust INTEGER DEFAULT 50,
            status TEXT DEFAULT 'online',
            credits INTEGER DEFAULT 0,
            last_seen REAL
        )
    ''')
    
    # jobs table (added type column)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            type TEXT,
            status TEXT DEFAULT 'pending',
            assigned_node TEXT,
            accuracy REAL DEFAULT 0.0,
            loss REAL DEFAULT 0.0,
            epoch INTEGER DEFAULT 0
        )
    ''')
    
    # metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            epoch INTEGER,
            accuracy REAL,
            loss REAL,
            node_id TEXT,
            timestamp REAL
        )
    ''')
    
    conn.commit()
    conn.close()
