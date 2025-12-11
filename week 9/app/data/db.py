import sqlite3
from pathlib import Path

DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))

import pandas as pd
from pathlib import Path

def load_csv_to_table(conn, csv_path, table_name):
    path = Path(csv_path)
    if not path.exists():
        return 0
    
    df = pd.read_csv(path)
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    return len(df)





""" import pandas as pd
from pathlib import Path
import sqlite3
import datetime

def connect_database():

    DB_PATH =Path("DATA") / "intelligence_platform.db"
    return sqlite3.connect(str(DB_PATH)) 



def load_csv_to_table(conn, csv_path, table_name):
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        print(f"ERROR: CSV file not found at path: {csv_path}")
        return 0
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {e}")
        return 0
    
    if df.empty:
        print(f"WARNING: CSV file '{csv_file.name}' is empty. 0 rows loaded.")
        return 0

    try:
        rows_loaded = df.to_sql(
            name=table_name, 
            con=conn, 
            if_exists='append', 
            index=False
        )
    except Exception as e:
        print(f"ERROR: Failed to insert data into table '{table_name}'. Database or schema issue: {e}")
        return 0
    
    print(f"SUCCESS: Loaded {rows_loaded} rows from '{csv_file.name}' into table '{table_name}'.")
    return rows_loaded
"""