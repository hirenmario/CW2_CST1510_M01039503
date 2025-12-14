import streamlit as st
import pandas as pd
import datetime
import time
import os
from openai import OpenAI

# --- CONFIGURATION ---
CSV_PATH = r"C:\Users\DELL\Desktop\CST1510\CW2_CST1510_M01039503\week 9\DATA\it_tickets.csv"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="IT Operations", layout="wide")

# --- AUTH CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    st.stop()

# --- Title + AI Assistant Button ---
col_title, col_button = st.columns([0.85, 0.15])
with col_title:
    st.title("IT Operations Dashboard")
with col_button:
    if st.button("AI Assistant (bottom of page)", use_container_width=True):
        st.session_state.show_chat = not st.session_state.get("show_chat", False)

# --- DATA FUNCTIONS ---
def load_tickets():
    if not os.path.exists(CSV_PATH):
        st.error(f"CSV file not found at {CSV_PATH}. Please ensure the file exists.")
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)

def save_tickets(df):
    df.to_csv(CSV_PATH, index=False)

def get_all_tickets():
    df = load_tickets()
    return df.sort_values(by="id") if not df.empty else df

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

# --- REFRESH HANDLING ---
if "refresh" in st.session_state and st.session_state.refresh:
    df_tickets = get_all_tickets()
    st.session_state.refresh = False
else:
    df_tickets = get_all_tickets()

# --- METRICS ---
st.subheader("Ticket Metrics")

if not df_tickets.empty:
    total = len(df_tickets)
    high = len(df_tickets[df_tickets['priority'] == 'High'])
    open_t = len(df_tickets[df_tickets['status'] == 'Open'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", total)
    col2.metric("High Priority", high)
    col3.metric("Open Tickets", open_t)

    # --- LINE CHART: Tickets Over Time ---
    st.subheader("Tickets Created Over Time")
    df_tickets["created_at"] = pd.to_datetime(df_tickets["created_at"], errors="coerce")
    tickets_over_time = df_tickets.groupby(df_tickets["created_at"].dt.date).size()
    tickets_over_time_df = tickets_over_time.reset_index()
    tickets_over_time_df.columns = ["Date", "Ticket Count"]
    st.line_chart(tickets_over_time_df.set_index("Date"))

    # --- BAR CHART: Current Ticket Status ---
    st.subheader("Current Ticket Status")
    st.bar_chart(df_tickets['status'].value_counts())
else:
    st.info("No tickets found.")

# --- CRUD TABS ---
st.divider()
st.header("Ticket Management")

tab_view, tab_add, tab_update, tab_delete = st.tabs([
    "View Queue", "Create Ticket", "Update Status", "Delete"
])

with tab_view:
    st.dataframe(df_tickets, use_container_width=True)

with tab_add:
    with st.form("add_tick"):
        tid = st.text_input("Ticket ID (e.g. T-100)")
        subj = st.text_input("Subject")
        prio = st.selectbox("Priority", ["Low", "Medium", "High"])
        cat = st.selectbox("Category", ["Hardware", "Software", "Network"])
        desc = st.text_area("Description")
        if st.form_submit_button("Submit"):
            today = str(datetime.date.today())
            insert_ticket(tid, prio, "Open", cat, subj, desc, today, None, None)
            st.success("Created!")
            st.session_state.refresh = True

with tab_update:
    if not df_tickets.empty:
        opts = {f"{row['ticket_id']} (ID: {row['id']})": row['id'] for _, row in df_tickets.iterrows()}
        sel_lbl = st.selectbox("Select Ticket", list(opts.keys()))
        sel_id = opts[sel_lbl]
        new_stat = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
        if st.button("Update Status"):
            update_ticket_status(sel_id, new_stat)
            st.success("Updated!")
            st.session_state.refresh = True

with tab_delete:
    if not df_tickets.empty:
        ids = df_tickets['id'].tolist()
        del_id = st.selectbox("Select ID to Delete", ids)
        if st.button("Confirm Delete", type="primary"):
            delete_ticket(del_id)
            st.success("Deleted.")
            st.session_state.refresh = True

# --- CHATGPT ASSISTANT (only shown when button clicked) ---
if st.session_state.get("show_chat"):
    st.divider()
    st.header("ChatGPT Assistant")
    st.caption("Powered by GPT-4o Mini")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful IT assistant."}
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

    prompt = st.text_input("Ask me anything about IT tickets...", key="chat_prompt")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_prompt = ""  # clear input

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
    time.sleep(1)
    st.switch_page("Home.py")
