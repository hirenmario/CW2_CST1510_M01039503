import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page setup
st.set_page_config(
    page_title="ChatGPT Assistant",
    page_icon="💬",
    layout="wide"
)

st.title("💬 ChatGPT - OpenAI API")
st.caption("Powered by GPT-4o Mini")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! What is AI?"}
    ]

# --- Sidebar controls ---
with st.sidebar:
    st.subheader("Chat Controls")
    message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
    st.metric("Messages", message_count)

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Display chat history ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Handle initial automatic assistant reply ---
if (len(st.session_state.messages) == 2 and 
    st.session_state.messages[-1]["role"] == "user"):

    prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True
        )

    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                container.markdown(full_reply + "▌")
        container.markdown(full_reply)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})

# --- Handle new user input ---
prompt = st.chat_input("Say something...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True
        )

    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                container.markdown(full_reply + "▌")
        container.markdown(full_reply)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
