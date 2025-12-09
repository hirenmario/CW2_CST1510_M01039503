import streamlit as st
import pandas as pd
import datetime
import time 
import numpy as np 

# --- MOCK DB FUNCTIONS (Adapted for Dataset Metadata) ---

def mock_get_all_datasets():
    if 'datasets_db' not in st.session_state:
        st.session_state.datasets_db = {}
        today = str(datetime.date.today())
        # Mock data based on schema.py: dataset_name, category, source, last_updated, record_count, file_size_mb
        mock_insert_dataset("ImageNetSubset", "Computer Vision", "Kaggle", today, 100000, 550.5)
        mock_insert_dataset("NLP_Corpus_v1", "NLP", "Internal", today, 500000, 12.8)
        mock_insert_dataset("Customer_Churn_v2", "Predictive Modeling", "CRM Export", str(datetime.date.today() - datetime.timedelta(days=30)), 20000, 1.2)
        
    data_list = list(st.session_state.datasets_db.values())
    if not data_list:
        return pd.DataFrame()
        
    df = pd.DataFrame(data_list)
    return df.sort_values(by='id')

def mock_insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    if 'next_dataset_id' not in st.session_state:
        st.session_state.next_dataset_id = 1
    
    if any(ds['dataset_name'] == dataset_name for ds in st.session_state.datasets_db.values()):
        st.error(f"Dataset name {dataset_name} already exists.")
        return

    new_id = st.session_state.next_dataset_id
    st.session_state.datasets_db[new_id] = {
        'id': new_id, 'dataset_name': dataset_name, 'category': category, 'source': source, 
        'last_updated': last_updated, 'record_count': record_count, 'file_size_mb': file_size_mb,
    }
    st.session_state.next_dataset_id += 1

def mock_update_dataset(pk_id, new_record_count, new_size_mb):
    if pk_id in st.session_state.datasets_db:
        st.session_state.datasets_db[pk_id]['record_count'] = new_record_count
        st.session_state.datasets_db[pk_id]['file_size_mb'] = new_size_mb
        st.session_state.datasets_db[pk_id]['last_updated'] = str(datetime.date.today())

def mock_delete_dataset(pk_id):
    if pk_id in st.session_state.datasets_db:
        del st.session_state.datasets_db[pk_id]

# --- STREAMLIT PAGE SETUP ---

st.set_page_config(page_title="AI Dashboard", page_icon="🤖", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("AI Dashboard 🤖")

df_datasets = mock_get_all_datasets()

# --- METRICS & CHARTS ---

if not df_datasets.empty:
    st.subheader("Data Metrics")
    
    total = len(df_datasets)
    total_records = df_datasets['record_count'].sum()
    total_size = df_datasets['file_size_mb'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Datasets", total)
    col2.metric("Total Records", f"{total_records/1000000:.1f}M")
    col3.metric("Total Storage (GB)", f"{total_size/1024:.2f} GB")
    
    st.markdown("---")

    st.subheader("Dataset Category Distribution")
    category_counts = df_datasets['category'].value_counts()
    st.bar_chart(category_counts)

else:
    st.info("No datasets found. Use the 'Create Metadata' tab to add a new entry.")

# --- CRUD OPERATIONS (Dataset Metadata Management) ---

st.divider()
st.header("Dataset Metadata Management")

tab_view, tab_add, tab_update, tab_delete = st.tabs(["View Metadata", "Create Metadata", "Update Records", "Delete"])

with tab_view:
    st.dataframe(df_datasets, use_container_width=True, hide_index=True)

with tab_add:
    with st.form("add_dataset"):
        st.markdown("**Enter New Dataset Metadata**")
        ds_name = st.text_input("Dataset Name (unique)")
        ds_cat = st.selectbox("Category", ["Computer Vision", "NLP", "Predictive Modeling", "Time Series"])
        ds_src = st.text_input("Source")
        ds_recs = st.number_input("Record Count", min_value=1, value=1000)
        ds_size = st.number_input("File Size (MB)", min_value=0.1, value=1.0)
        
        if st.form_submit_button("Submit New Dataset", type="primary"):
            if not ds_name or not ds_src:
                st.error("Please fill in Dataset Name and Source.")
            else:
                mock_insert_dataset(ds_name, ds_cat, ds_src, str(datetime.date.today()), ds_recs, ds_size)
                st.success(f"Metadata for **{ds_name}** created.")
                time.sleep(1) 
                st.rerun()

with tab_update:
    if not df_datasets.empty:
        opts = {f"{row['dataset_name']} ({row['category']})": row['id'] for i, row in df_datasets.iterrows()}
        sel_lbl = st.selectbox("Select Dataset to Update", list(opts.keys()))
        
        if sel_lbl:
            sel_id = opts[sel_lbl]
            
            current_recs = df_datasets[df_datasets['id'] == sel_id]['record_count'].iloc[0]
            current_size = df_datasets[df_datasets['id'] == sel_id]['file_size_mb'].iloc[0]

            new_recs = st.number_input("New Record Count", min_value=1, value=int(current_recs))
            new_size = st.number_input("New File Size (MB)", min_value=0.1, value=float(current_size))

            if st.button("Update Metadata", type="primary"):
                mock_update_dataset(sel_id, new_recs, new_size)
                st.success(f"Metadata for **{sel_lbl.split('(')[0].strip()}** updated.")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No datasets available for update.")

with tab_delete:
    if not df_datasets.empty:
        del_opts = {f"{row['dataset_name']} ({row['id']})": row['id'] for i, row in df_datasets.iterrows()}
        del_lbl = st.selectbox("Select Dataset to Delete", list(del_opts.keys()))
        
        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of dataset metadata **{del_lbl}**.")
            
            if st.button("Confirm Delete", type="primary"):
                mock_delete_dataset(del_id)
                st.success("Dataset metadata deleted.")
                time.sleep(1)
                st.rerun()

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have logged out.")
    st.switch_page("Home.py")