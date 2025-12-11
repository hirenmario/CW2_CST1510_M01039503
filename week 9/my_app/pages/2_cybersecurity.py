import streamlit as st
import pandas as pd
import datetime
import time
import os

# --- ABSOLUTE FILE PATH TO EXISTING CSV ---
CSV_PATH = r"C:\Users\DELL\Desktop\CST1510\CW2_CST1510_M01039503\week 9\DATA\cyber_incidents.csv"

# --- DB FUNCTIONS USING EXISTING CSV ONLY ---

def load_incidents():
    if not os.path.exists(CSV_PATH):
        st.error(f"CSV file not found at {CSV_PATH}. Please ensure the file exists.")
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)

def save_incidents(df):
    df.to_csv(CSV_PATH, index=False)

def get_all_incidents():
    df = load_incidents()
    if df.empty:
        return df
    return df.sort_values(by="id")

def insert_incident(date, type, severity, status, description, reported_by, created_at):
    df = load_incidents()
    new_id = df["id"].max() + 1 if not df.empty else 1
    new_row = {
        "id": new_id,
        "date": date,
        "incident_type": type,
        "severity": severity,
        "status": status,
        "description": description,
        "reported_by": reported_by,
        "created_at": created_at,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_incidents(df)

def update_incident_status(pk_id, new_status):
    df = load_incidents()
    df.loc[df["id"] == pk_id, "status"] = new_status
    save_incidents(df)

def delete_incident(pk_id):
    df = load_incidents()
    df = df[df["id"] != pk_id]
    save_incidents(df)

# --- STREAMLIT PAGE SETUP ---

st.set_page_config(page_title="Cybersecurity", page_icon="🛡️", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("Cybersecurity Incident Dashboard")

df_incidents = get_all_incidents()

# --- METRICS & CHARTS ---

if not df_incidents.empty:
    st.subheader("Incident Metrics")

    total = len(df_incidents)
    critical_active = (df_incidents["severity"] == "Critical").sum()
    active_incidents = (df_incidents["status"].isin(["Active", "Triage"])).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", total)
    col2.metric("Critical Severity", critical_active)
    col3.metric("Active Cases", active_incidents)

    st.markdown("---")

    st.subheader("Incident Type Distribution")
    type_counts = df_incidents["incident_type"].value_counts()
    st.bar_chart(type_counts)

else:
    st.info("No incidents found. Use the 'Report Incident' tab to log a new case.")

# --- CRUD OPERATIONS (Incident Management) ---

st.divider()
st.header("Incident Management")

tab_view, tab_add, tab_update, tab_delete = st.tabs(["View Queue", "Report Incident", "Update Status", "Delete"])

with tab_view:
    st.dataframe(df_incidents, use_container_width=True, hide_index=True)

with tab_add:
    with st.form("add_incident"):
        st.markdown("**Report New Incident**")
        inc_date = str(st.date_input("Date of Incident", datetime.date.today()))
        inc_type = st.selectbox("Type", ["DDoS Attack", "Phishing Email", "Malware Infection", "Unauthorized Access"])
        inc_sev = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        inc_desc = st.text_area("Description")
        inc_rpt = st.text_input("Reported By", value=st.session_state.username)

        if st.form_submit_button("Submit Incident Report", type="primary"):
            if not inc_desc:
                st.error("Please provide a description.")
            else:
                insert_incident(inc_date, inc_type, inc_sev, "Triage", inc_desc, inc_rpt, str(datetime.date.today()))
                st.success(f"Incident of type **{inc_type}** reported successfully.")
                time.sleep(1)
                st.rerun()

with tab_update:
    if not df_incidents.empty:
        active_incidents_df = df_incidents[df_incidents["status"].isin(["Triage", "Active"])]
        if active_incidents_df.empty:
            st.info("No active incidents to update.")
        else:
            opts = {f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row["id"] for i, row in active_incidents_df.iterrows()}
            sel_lbl = st.selectbox("Select Incident to Update", list(opts.keys()))

            if sel_lbl:
                sel_id = opts[sel_lbl]
                current_status = active_incidents_df[active_incidents_df["id"] == sel_id]["status"].iloc[0]
                status_options = ["Triage", "Active", "Contained", "Closed"]
                default_index = status_options.index(current_status)

                new_stat = st.selectbox("New Status", status_options, index=default_index)

                if st.button("Update Status", type="primary"):
                    update_incident_status(sel_id, new_stat)
                    st.success(f"Incident status updated to **{new_stat}**.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("No incidents available for status update.")

with tab_delete:
    if not df_incidents.empty:
        del_opts = {f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row["id"] for i, row in df_incidents.iterrows()}
        del_lbl = st.selectbox("Select Incident to Delete", list(del_opts.keys()))

        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of incident **{del_lbl}**.")

            if st.button("Confirm Delete", type="primary"):
                delete_incident(del_id)
                st.success("Incident deleted.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No incidents available to delete.")
# Logout button

# --- LOGOUT BUTTON ---
st.divider()
if st.button("Logout", type="primary"):
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    time.sleep(1)
    st.switch_page("Home.py")