import streamlit as st
import pandas as pd
import datetime
import time 

# --- MOCK DB FUNCTIONS (Adapted for Cyber Incidents) ---

def mock_get_all_incidents():
    if 'incidents_db' not in st.session_state:
        st.session_state.incidents_db = {}
        today = str(datetime.date.today())
        yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        last_week = str(datetime.date.today() - datetime.timedelta(days=7))
        mock_insert_incident(today, "DDoS Attack", "High", "Active", "High volume of traffic detected.", "System", yesterday)
        mock_insert_incident(today, "Phishing Email", "Medium", "Triage", "User reported suspicious email.", "User", today)
        mock_insert_incident(last_week, "Malware Infection", "Critical", "Closed", "Ransomware detected and contained.", "System", last_week)
        
    data_list = list(st.session_state.incidents_db.values())
    if not data_list:
        return pd.DataFrame()
        
    df = pd.DataFrame(data_list)
    return df.sort_values(by='id')

def mock_insert_incident(date, type, severity, status, description, reported_by, created_at):
    if 'next_incident_id' not in st.session_state:
        st.session_state.next_incident_id = 1
    
    new_id = st.session_state.next_incident_id
    st.session_state.incidents_db[new_id] = {
        'id': new_id, 
        'date': date, 
        'incident_type': type, 
        'severity': severity, 
        'status': status, 
        'description': description, 
        'reported_by': reported_by, 
        'created_at': created_at,
    }
    st.session_state.next_incident_id += 1

def mock_update_incident_status(pk_id, new_status):
    if pk_id in st.session_state.incidents_db:
        st.session_state.incidents_db[pk_id]['status'] = new_status

def mock_delete_incident(pk_id):
    if pk_id in st.session_state.incidents_db:
        del st.session_state.incidents_db[pk_id]

# --- STREAMLIT PAGE SETUP ---

st.set_page_config(page_title="Cybersecurity", page_icon="🛡️", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("Cybersecurity Incident Dashboard")
    
df_incidents = mock_get_all_incidents()

# --- METRICS & CHARTS ---

if not df_incidents.empty:
    st.subheader("Incident Metrics")
    
    total = len(df_incidents)
    critical_active = (df_incidents['severity'] == 'Critical').sum()
    active_incidents = (df_incidents['status'].isin(['Active', 'Triage'])).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", total)
    col2.metric("Critical Severity", critical_active)
    col3.metric("Active Cases", active_incidents)
    
    st.markdown("---")

    st.subheader("Incident Type Distribution")
    type_counts = df_incidents['incident_type'].value_counts()
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
                mock_insert_incident(inc_date, inc_type, inc_sev, "Triage", inc_desc, inc_rpt, str(datetime.date.today()))
                st.success(f"Incident of type **{inc_type}** reported successfully.")
                time.sleep(1) 
                st.rerun()

with tab_update:
    if not df_incidents.empty:
        active_incidents_df = df_incidents[df_incidents['status'].isin(['Triage', 'Active'])]
        if active_incidents_df.empty:
            st.info("No active incidents to update.")
        else:
            opts = {f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row['id'] for i, row in active_incidents_df.iterrows()}
            sel_lbl = st.selectbox("Select Incident to Update", list(opts.keys()))
            
            if sel_lbl:
                sel_id = opts[sel_lbl]
                current_status = active_incidents_df[active_incidents_df['id'] == sel_id]['status'].iloc[0]
                status_options = ["Triage", "Active", "Contained", "Closed"]
                default_index = status_options.index(current_status) 
                
                new_stat = st.selectbox("New Status", status_options, index=default_index)
                
                if st.button("Update Status", type="primary"):
                    mock_update_incident_status(sel_id, new_stat)
                    st.success(f"Incident status updated to **{new_stat}**.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("No incidents available for status update.")

with tab_delete:
    if not df_incidents.empty:
        del_opts = {f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row['id'] for i, row in df_incidents.iterrows()}
        del_lbl = st.selectbox("Select Incident to Delete", list(del_opts.keys()))
        
        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of incident **{del_lbl}**.")
            
            if st.button("Confirm Delete", type="primary"):
                mock_delete_incident(del_id)
                st.success("Incident deleted.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No incidents available to delete.")