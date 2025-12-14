import streamlit as st
import pandas as pd
import datetime
import time
import os
from openai import OpenAI

# --- FILE PATHS ---
ABSOLUTE_PATH = r"C:\Users\DELL\Desktop\CST1510\CW2_CST1510_M01039503\week 9\DATA\datasets_metadata.csv"
RELATIVE_PATH = os.path.join("week 9", "DATA", "datasets_metadata.csv")

def resolve_csv_path():
    if os.path.exists(ABSOLUTE_PATH):
        return ABSOLUTE_PATH
    elif os.path.exists(RELATIVE_PATH):
        return RELATIVE_PATH
    else:
        return None

CSV_PATH = resolve_csv_path()

# --- DATA ACCESS ---
def get_all_datasets():
    if not CSV_PATH:
        st.error("CSV file not found. Please ensure datasets_metadata.csv exists.")
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH)
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)
    return df.sort_values(by='id')

def save_to_csv(df):
    if CSV_PATH:
        df.to_csv(CSV_PATH, index=False)

def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    df = get_all_datasets()
    if dataset_name in df['dataset_name'].values:
        st.error(f"Dataset name {dataset_name} already exists.")
        return
    new_id = df['id'].max() + 1 if not df.empty else 1
    new_row = {
        'id': new_id,
        'dataset_name': dataset_name,
        'category': category,
        'source': source,
        'last_updated': last_updated,
        'record_count': record_count,
        'file_size_mb': file_size_mb,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_to_csv(df)
    st.success(f"Metadata for **{dataset_name}** created.")

def update_dataset(pk_id, new_record_count, new_size_mb):
    df = get_all_datasets()
    if pk_id in df['id'].values:
        df.loc[df['id'] == pk_id, 'record_count'] = new_record_count
        df.loc[df['id'] == pk_id, 'file_size_mb'] = new_size_mb
        df.loc[df['id'] == pk_id, 'last_updated'] = str(datetime.date.today())
        save_to_csv(df)
        st.success("Dataset updated.")
    else:
        st.error("Dataset ID not found.")

def delete_dataset(pk_id):
    df = get_all_datasets()
    if pk_id in df['id'].values:
        df = df[df['id'] != pk_id]
        save_to_csv(df)
        st.success("Dataset deleted.")
    else:
        st.error("Dataset ID not found.")


st.set_page_config(page_title="AI Operations", page_icon="🤖", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- AUTH CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# --- Title + AI Assistant Button ---
col_title, col_button = st.columns([0.85, 0.15])
with col_title:
    st.title("AI Analytics Dashboard")
with col_button:
    if st.button("AI Assistant (bottom of page)", use_container_width=True):
        st.session_state.show_chat = not st.session_state.get("show_chat", False)

# --- REFRESH HANDLING ---
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# Load datasets (respect refresh flag)
if st.session_state.refresh:
    df_datasets = get_all_datasets()
    st.session_state.refresh = False
else:
    df_datasets = get_all_datasets()

# --- METRICS & GRAPHS ---
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

    # --- BAR CHART: Dataset Category Distribution ---
    st.subheader("Dataset Category Distribution")
    category_counts = df_datasets['category'].value_counts()
    st.bar_chart(category_counts)

    # --- SCATTER PLOT: Dataset Size vs Record Count ---
    st.subheader("Dataset Size vs Record Count")
    scatter_df = df_datasets[['dataset_name', 'record_count', 'file_size_mb']].dropna()
    st.scatter_chart(scatter_df.rename(columns={'record_count': 'x', 'file_size_mb': 'y'}).set_index('dataset_name'))
else:
    st.info("No datasets found. Use the 'Create Metadata' tab to add a new entry.")

# --- CRUD TABS ---
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
                insert_dataset(ds_name, ds_cat, ds_src, str(datetime.date.today()), ds_recs, ds_size)
                st.session_state.refresh = True

with tab_update:
    if not df_datasets.empty:
        opts = {f"{row['dataset_name']} ({row['category']})": row['id'] for _, row in df_datasets.iterrows()}
        sel_lbl = st.selectbox("Select Dataset to Update", list(opts.keys()))
        if sel_lbl:
            sel_id = opts[sel_lbl]
            current_recs = int(df_datasets[df_datasets['id'] == sel_id]['record_count'].iloc[0])
            current_size = float(df_datasets[df_datasets['id'] == sel_id]['file_size_mb'].iloc[0])

            new_recs = st.number_input("New Record Count", min_value=1, value=current_recs)
            new_size = st.number_input("New File Size (MB)", min_value=0.1, value=current_size)

            if st.button("Update Metadata", type="primary"):
                update_dataset(sel_id, new_recs, new_size)
                st.session_state.refresh = True
    else:
        st.info("No datasets available for update.")

with tab_delete:
    if not df_datasets.empty:
        del_opts = {f"{row['dataset_name']} ({row['id']})": row['id'] for _, row in df_datasets.iterrows()}
        del_lbl = st.selectbox("Select Dataset to Delete", list(del_opts.keys()))
        if del_lbl:
            del_id = del_opts[del_lbl]
            st.warning(f"Confirm deletion of dataset metadata **{del_lbl}**.")
            if st.button("Confirm Delete", type="primary"):
                delete_dataset(del_id)
                st.session_state.refresh = True
    else:
        st.info("No datasets available to delete.")

if st.session_state.get("show_chat"):
    st.divider()
    st.header("ChatGPT Assistant")
    st.caption("Powered by GPT-4o Mini")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful AI analytics assistant."}
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

    prompt = st.text_input("Ask me anything about datasets or AI operations...", key="ai_chat_prompt")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.ai_chat_prompt = ""

        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True
            )

        full_reply = ""
        for chunk in completion:
            try:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    full_reply += delta.content
            except Exception:
                try:
                    content = chunk.choices[0].message.get("content", "")
                    if content:
                        full_reply += content
                except Exception:
                    pass

        st.session_state.messages.append({"role": "assistant", "content": full_reply})

st.divider()
if st.button("Logout", type="primary"):
    st.session_state.logged_in = False

    if "username" in st.session_state:
        st.session_state.username = ""
    if "messages" in st.session_state:
        st.session_state.messages = []
    st.success("You have been logged out.")
    time.sleep(1)
    st.switch_page("Home.py")
