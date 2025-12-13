import streamlit as st

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("Welcome 🔐")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged onto the dashboard as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_IT.py")  # path is relative to Home.py :contentReference[oaicite:1]{index=1}
    st.stop()  # Don’t show login/register again


# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        users = st.session_state.users
        if login_username in users and users[login_username] == login_password:
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.success(f"Welcome back, {login_username}! ")

            # Redirect to dashboard page
            st.switch_page("pages/1_IT.py")
        else:
            st.error("Invalid username or password.")


with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif new_username in st.session_state.users:
            st.error("Username already exists. Choose another one.")
        else:
            # "Save" user in our simple in-memory store
            st.session_state.users[new_username] = new_password
            st.success("Account created! Now log in from the Login tab.")
            st.info("Tip: Switch to the Login tab and sign in with your new account.")