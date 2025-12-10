import pandas as pd
from app.data.db import connect_database

def insert_ticket(ticket_id, priority, status, category, subject, description, created_date, resolved_date=None, assigned_to=None):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    conn.commit()
    pk_id = cursor.lastrowid
    conn.close()
    return pk_id

def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

def update_ticket_status(id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?",
        (new_status, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected

def delete_ticket(id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM it_tickets WHERE id = ?",
        (id,)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected