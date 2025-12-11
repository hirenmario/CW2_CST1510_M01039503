import pandas as pd
import os

CSV_PATH = "CW2_CST1510_M01039503/week9/DATA/it_tickets.csv"

def load_tickets():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        cols = ["id", "ticket_id", "priority", "status", "category", "subject", "description", "created_at", "resolved_at", "assigned_to"]
        pd.DataFrame(columns=cols).to_csv(CSV_PATH, index=False)
        return pd.DataFrame(columns=cols)

def save_tickets(df):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    df.to_csv(CSV_PATH, index=False)

def get_all_tickets():
    return load_tickets().sort_values(by="id")

def insert_ticket(ticket_id, priority, status, category, subject, description, created_at, resolved_at, assigned_to):
    df = load_tickets()
    new_id = df["id"].max() + 1 if not df.empty else 1
    new_row = {
        "id": new_id,
        "ticket_id": ticket_id,
        "priority": priority,
        "status": status,
        "category": category,
        "subject": subject,
        "description": description,
        "created_at": created_at,
        "resolved_at": resolved_at,
        "assigned_to": assigned_to,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_tickets(df)

def update_ticket_status(pk_id, new_status):
    df = load_tickets()
    df.loc[df["id"] == pk_id, "status"] = new_status
    save_tickets(df)

def delete_ticket(pk_id):
    df = load_tickets()
    df = df[df["id"] != pk_id]
    save_tickets(df)
