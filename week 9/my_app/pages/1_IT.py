import streamlit as st
import pandas as pd
import datetime
import time 

# --- MOCK DB FUNCTIONS (Uses st.session_state for persistence) ---

def mock_get_all_tickets():
    if 'tickets_db' not in st.session_state:
        st.session_state.tickets_db = {}
        today = str(datetime.date.today())
        last_week = str(datetime.date.today() - datetime.timedelta(days=7))
        mock_insert_ticket("T-101", "High", "Open", "Network", "Slow internet in R&D", "Severe latency reported.", today, None, None)
        mock_insert_ticket("T-102", "Medium", "In Progress", "Software", "Excel crashing", "Affects three users.", today, None, None)
        mock_insert_ticket("T-103", "Low", "Resolved", "Hardware", "Monitor flickering", "Monitor needs replacing.", last_week, today, "Replaced monitor.")
        
    data_list = list(st.session_state.tickets_db.values())
    if not data_list:
        return pd.DataFrame()
        
    df = pd.DataFrame(data_list)
    return df.sort_values(by='id')

def mock_insert_ticket(ticket_id, priority, status, category, subject, description, created_date, resolved_date, resolution_notes):
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 1
    
    if any(ticket['ticket_id'] == ticket_id for ticket in st.session_state.tickets_db.values()):
        st.error(f"Ticket ID {ticket_id} already exists.")
        return

    new_id = st.session_state.next_id
    st.session_state.tickets_db[new_id] = {
        'id': new_id, 'ticket_id': ticket_id, 'priority': priority, 'status': status, 
        'category': category, 'subject': subject, 'description': description, 
        'created_date': created_date, 'resolved_date': resolved_date, 
        'resolution_notes': resolution_notes
    }
    st.session_state.next_id += 1

def mock_update_ticket_status(ticket_pk_id, new_status):
    if ticket_pk_id in st.session_state.tickets_db:
        st.session_state.tickets_db[ticket_pk_id]['status'] = new_status
        is_resolved = new_status in ("Resolved", "Closed")
        st.session_state.tickets_db[ticket_pk_id]['resolved_date'] = str(datetime.date.today()) if is_resolved else None

def mock_delete_ticket(ticket_pk_id):
    if ticket_pk_id in st.session_state.tickets_db:
        del st.session_state.tickets_db[ticket_pk_id]

# --- STREAMLIT PAGE SETUP ---

st.set_page_config(page_title="IT Operations", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first to access the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("IT Operations Dashboard 💻")

df_tickets = mock_get_all_tickets()

# --- METRICS & CHARTS ---

if not df_tickets.empty:
    st.subheader("Ticket Metrics")
    
    total = len(df_tickets)
    high = (df_tickets['priority'] == 'High').sum()
    open_t = (df_tickets['status'] == 'Open').sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", total)
    col2.metric("High Priority", high)
    col3.metric("Open Tickets", open_t)
    
    st.markdown("---")

    st.subheader("Current Ticket Status Distribution")
    status_counts = df_tickets['status'].value_counts()
    st.bar_chart(status_counts)

else:
    st.info("No tickets found. Use the 'Create Ticket' tab to add a new entry.")

# CRUD OPERATIONS 
st.divider()
st.header("Ticket Management")

tab_view, tab_add, tab_update, tab_delete = st.tabs(["View Queue", "Create Ticket", "Update Status", "Delete"])

with tab_view:
    st.dataframe(df_tickets, use_container_width=True, hide_index=True)

with tab_add:
    with st.form("add_tick"):
        st.markdown("**Enter New Ticket Details**")
        tid = st.text_input("Ticket ID (e.g. T-100)", key="tid_add")
        subj = st.text_input("Subject")
        prio = st.selectbox("Priority", ["Low", "Medium", "High"])
        cat = st.selectbox("Category", ["Hardware", "Software", "Network", "Access"])
        desc = st.text_area("Description")
        
        if st.form_submit_button("Submit New Ticket", type="primary"):
            if not tid or not subj:
                st.error("Please fill in Ticket ID and Subject.")
            else:
                mock_insert_ticket(tid, prio, "Open", cat, subj, desc, str(datetime.date.today()), None, None)
                st.success(f"Ticket **{tid}** created successfully!")
                time.sleep(1) 
                st.rerun()

with tab_update:
    if not df_tickets.empty:
        open_tickets = df_tickets[df_tickets['status'].isin(['Open', 'In Progress'])]
        if open_tickets.empty:
            st.info("No active tickets to update.")
        else:
            opts = {f"{row['ticket_id']} - {row['subject']}": row['id'] for i, row in open_tickets.iterrows()}
            sel_lbl = st.selectbox("Select Ticket to Update", list(opts.keys()))
            
            if sel_lbl:
                sel_id = opts[sel_lbl]
                current_status = open_tickets[open_tickets['id'] == sel_id]['status'].iloc[0]
                status_options = ["Open", "In Progress", "Resolved", "Closed"]
                default_index = status_options.index(current_status) 
                
                new_stat = st.selectbox("New Status", status_options, index=default_index)
                
                if st.button("Update Status", type="primary"):
                    mock_update_ticket_status(sel_id, new_stat)
                    st.success(f"Ticket **{sel_lbl.split('-')[0].strip()}** status updated to **{new_stat}**.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("No tickets available for status update.")

with tab_delete:
    if not df_tickets.empty:
        del_opts = {f"{row['ticket_id']} - {row['subject']}": row['id'] for i, row in df_tickets.iterrows()}
        del_lbl = st.selectbox("Select Ticket to Delete", list(del_opts.keys()))
        
        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of ticket **{del_lbl}**.")
            
            if st.button("Confirm Delete", type="primary"):
                mock_delete_ticket(del_id)
                st.success("Ticket deleted.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No tickets available to delete.")