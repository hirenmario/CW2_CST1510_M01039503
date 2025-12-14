import streamlit as st
import pandas as pd
import datetime
import os
from openai import OpenAI

# --- ABSOLUTE FILE PATH TO EXISTING CSV ---
CSV_PATH = r"C:\Users\DELL\Desktop\CST1510\CW2_CST1510_M01039503\week 9\DATA\cyber_incidents.csv"

# --- Initialize OpenAI client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- STREAMLIT PAGE SETUP ---
st.set_page_config(page_title="Cybersecurity", page_icon="🛡️", layout="wide")

# --- AUTH CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# --- Title + AI Assistant Button ---
col_title, col_button = st.columns([0.85, 0.15])
with col_title:
    st.title("Cybersecurity Incident Dashboard")
with col_button:
    if st.button("AI Assistant (bottom of page)", use_container_width=True):
        st.session_state.show_chat = not st.session_state.get("show_chat", False)

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
    return df.sort_values(by="id") if not df.empty else df

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

# --- REFRESH HANDLING ---
if "refresh" in st.session_state and st.session_state.refresh:
    df_incidents = get_all_incidents()
    st.session_state.refresh = False
else:
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

    # --- BAR CHART: Incident Type Distribution ---
    st.subheader("Incident Type Distribution")
    type_counts = df_incidents["incident_type"].value_counts()
    st.bar_chart(type_counts)

    # --- LINE CHART: Incidents Over Time ---
    st.subheader("Incidents Over Time")
    df_incidents["date"] = pd.to_datetime(df_incidents["date"], errors="coerce")
    incidents_over_time = df_incidents.groupby(df_incidents["date"].dt.date).size()
    incidents_over_time_df = incidents_over_time.reset_index()
    incidents_over_time_df.columns = ["Date", "Incident Count"]
    st.line_chart(incidents_over_time_df.set_index("Date"))

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
        inc_rpt = st.text_input("Reported By", value=st.session_state.get("username", ""))

        if st.form_submit_button("Submit Incident Report", type="primary"):
            if not inc_desc:
                st.error("Please provide a description.")
            else:
                insert_incident(inc_date, inc_type, inc_sev, "Triage", inc_desc, inc_rpt, str(datetime.date.today()))
                st.success(f"Incident of type **{inc_type}** reported successfully.")
                st.session_state.refresh = True

with tab_update:
    if not df_incidents.empty:
        active_incidents_df = df_incidents[df_incidents["status"].isin(["Triage", "Active"])]
        if active_incidents_df.empty:
            st.info("No incidents to update.")
        else:
            opts = {
                f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row["id"]
                for _, row in active_incidents_df.iterrows()
            }
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
                    st.session_state.refresh = True
    else:
        st.info("No incidents available to update status.")

with tab_delete:
    if not df_incidents.empty:
        del_opts = {
            f"ID {row['id']} - {row['incident_type']} ({row['severity']})": row["id"]
            for _, row in df_incidents.iterrows()
        }
        del_lbl = st.selectbox("Select Incident to Delete", list(del_opts.keys()))

        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of incident **{del_lbl}**.")

            if st.button("Confirm Delete", type="primary"):
                delete_incident(del_id)
                st.success("Incident deleted.")
                st.session_state.refresh = True
    else:
        st.info("No other incidents available to delete.")

# --- CHATGPT ASSISTANT (only shown when button clicked) ---
if st.session_state.get("show_chat"):
    st.divider()
    st.header("ChatGPT Assistant")
    st.caption("Powered by GPT-4o Mini")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful cybersecurity assistant."}
        ]

    with st.sidebar:
        st.subheader("Chat Controls")
        message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
        st.metric("Messages", message_count)
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.success("Chat cleared.")

    chat_box = st.container()
    for message in st.session_state.messages:
        if message["role"] != "system":
            chat_box.markdown(f"**{message['role'].capitalize()}:** {message['content']}")


    prompt = st.text_input("Ask me anything about cybersecurity incidents...", key="cyber_chat_prompt")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.cyber_chat_prompt = ""  

        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True
            )

        full_reply = ""
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content

        st.session_state.messages.append({"role": "assistant", "content": full_reply})

# --- LOGOUT BUTTON ---
st.divider()
if st.button("Logout", type="primary"):
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    st.switch_page("Home.py")
