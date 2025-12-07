import sqlite3
from pathlib import Path

# Get the path of the current file (db.py)
DB_FILE_PATH = Path(__file__).resolve()

# Go up 2 levels (index 1) to reach the 'week 8' folder (where DATA is located): 
# parents[0] = data, parents[1] = app, parents[2] = week 8
WEEK_8_ROOT = DB_FILE_PATH.parents[2] 

# Define the full path to the database file inside the DATA folder
DB_PATH = WEEK_8_ROOT / "DATA" / "intelligence_platform.db"

def connect_database():
    """Connect to SQLite database."""
    
    # Ensure the DATA directory exists
    (WEEK_8_ROOT / "DATA").mkdir(parents=True, exist_ok=True)
    
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Database file not found at: {DB_PATH}")
        
    return sqlite3.connect(str(DB_PATH))