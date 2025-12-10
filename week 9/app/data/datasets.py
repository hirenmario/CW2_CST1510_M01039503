import pandas as pd
from app.data.db import connect_database

def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))
    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()
    return dataset_id

def get_all_datasets():
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def update_dataset_record_count(id, new_count):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datasets_metadata SET record_count = ? WHERE id = ?",
        (new_count, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected

def delete_dataset(id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (id,)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected