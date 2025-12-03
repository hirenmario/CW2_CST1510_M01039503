import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
# It relies on the 'OPENAI_API_KEY' being set in Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page configuration
st.set_page_config(
    page_title="ChatGPT Assistant",
    page_icon="💬",
    layout="wide"
)
# Title
st.title("💬 ChatGPT - OpenAI API")
# Updated caption to reflect the model from the second code
st.caption("Powered by GPT-4o") 

def InitialisePage():
    # Initialize session state.
    # We check if 'messages' is empty to avoid re-initializing on re-runs.
    if 'messages' not in st.session_state or len(st.session_state.messages) == 0:
        # Pre-populate with the initial conversation structure from the 1st code
        st.session_state.messages = [
            # The system prompt that defines the model's behavior
            {"role": "system", "content": "You are a helpful assistant."},
            # The fixed user query from the 1st code, which triggers the initial auto-reply
            {"role": "user", "content": "Hello! What is AI?"} 
        ]
        
    # Sidebar with controls
    with st.sidebar:
        st.subheader("Chat Controls")
        
        # Display message count (excluding system prompt)
        message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
        st.metric("Messages", message_count)
        
        # Clear chat button
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

def Prompting():
    # --- Check for Initial State and Force Response ---
    # If the history only contains the system and initial user message, 
    # we need to generate the assistant's first reply automatically.
    if (len(st.session_state.messages) == 2 and 
        st.session_state.messages[-1]["role"] == "user"):
        
        # We simulate the prompt submission automatically here
        prompt = st.session_state.messages[-1]["content"]

        # Display the initial user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call OpenAI API with streaming for the initial response
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                # Model updated to GPT-4o from the second code snippet
                model="gpt-4o", 
                messages=st.session_state.messages,
                stream=True
            )
            
        # Display streaming response
        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""
            
            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_reply += delta.content
                    container.markdown(full_reply + "▌") # Add cursor effect
            
            # Remove cursor and show final response
            container.markdown(full_reply)
            
            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_reply
            })
            
    # --- Display Existing History (including the newly generated one) ---
    for message in st.session_state.messages:
        # Skip the system message when displaying
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
            
    # --- Handle New User Input ---
    prompt = st.chat_input("Say something...")

    if prompt:
    # Display new user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Add new user message to session state
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Call OpenAI API with streaming for the new response
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                # Model updated to GPT-4o from the second code snippet
                model="gpt-4o", 
                messages=st.session_state.messages,
                stream=True
            )
            
        # Display streaming response
        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""
            
            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_reply += delta.content
                    container.markdown(full_reply + "▌") # Add cursor effect
            # Remove cursor and show final response
            container.markdown(full_reply)
            
        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_reply
            })