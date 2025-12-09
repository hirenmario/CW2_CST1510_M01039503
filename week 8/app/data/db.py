import sqlite3
from pathlib import Path

DB_FILE_PATH = Path(__file__).resolve()
WEEK_8_ROOT = DB_FILE_PATH.parents[2]
DB_PATH = WEEK_8_ROOT / "DATA" / "intelligence_platform.db"

def connect_database():
    """Connect to SQLite database."""
    
    # Ensure the DATA directory exists
    (WEEK_8_ROOT / "DATA").mkdir(parents=True, exist_ok=True)
    
    print(f"Database path: {DB_PATH}")
    
    # Connect — SQLite will create file if missing
    return sqlite3.connect(str(DB_PATH))
