import pandas as pd
from pathlib import Path
from app.data.db import connect_database, DB_PATH, DATA_DIR
from app.data.schema import create_all_tables
from app.data.cyber_incidents import insert_incident, get_all_incidents, update_incident_status, delete_incident
from app.data.users import register_user, login_user, migrate_users_from_file

# -----------------------------
# CSV Helper Functions
# -----------------------------

def load_csv_to_table(conn, csv_path, table_name):
    """Load a CSV file into a database table using pandas."""
    csv_file = Path(csv_path)

    if not csv_file.exists():
        print(f"  CSV file not found: {csv_file}. Skipping {table_name}.")
        return 0

    try:
        df = pd.read_csv(csv_file)
        rows_loaded = df.to_sql(
            name=table_name,
            con=conn,
            if_exists='append',
            index=False
        )
        print(f" Loaded {rows_loaded} rows into {table_name} from {csv_file.name}.")
        return rows_loaded
    except Exception as e:
        print(f"Error loading CSV {csv_file.name} into {table_name}: {e}")
        return 0


def load_all_csv_data(conn):
    """Load data for all main tables from CSV files."""
    total_rows = 0
    total_rows += load_csv_to_table(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    total_rows += load_csv_to_table(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    total_rows += load_csv_to_table(conn, DATA_DIR / "it_tickets.csv", "it_tickets")
    return total_rows


# -----------------------------
# Database Setup
# -----------------------------

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data
    5. Verify setup
    """
    print("\n" + "=" * 60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("=" * 60)

    conn = connect_database()

    # 2. Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)

    # 3. Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    migrate_users_from_file()  # Function handles its own connection and printout

    # 4. Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)
    print(f"      Total {total_rows} rows loaded into domain tables.")

    # 5. Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "=" * 60)
    print(" DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n Database location: {DB_PATH.resolve()}")


# -----------------------------
# Test Queries
# -----------------------------

def run_test_queries():
    """Run simple tests on authentication and CRUD."""
    conn = connect_database()

    print("\n" + "=" * 60)
    print(" RUNNING APPLICATION TESTS")
    print("=" * 60)

    # Test 1: Authentication
    success, msg = register_user("analyst_test", "P@ssword1", "analyst")
    print(f" Register Test: {'' if success else '❌'} {msg}")

    success, msg = login_user("analyst_test", "P@ssword1")
    print(f" Login Test:    {'' if success else '❌'} {msg}")

    # Test 2: CRUD
    incident_id = insert_incident(
        conn,
        "2025-12-08", "DDoS", "Critical", "Open", "Test attack", "analyst_test"
    )
    print(f" CRUD Create:    Incident #{incident_id} created")

    update_incident_status(conn, incident_id, "Resolved")
    print(f" CRUD Update:    Status updated")

    df = get_all_incidents(conn)
    print(f" CRUD Read:      Total incidents: {len(df)}")

    delete_incident(conn, incident_id)
    print(f" CRUD Delete:    Test incident deleted")

    conn.close()


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    setup_database_complete()
    run_test_queries()