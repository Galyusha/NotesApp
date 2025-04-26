import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Simple Notes App", page_icon="📝")

st.title("📝 Cool Notes App")

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None


with st.expander("Don't have an account? Register here"):
    new_username = st.text_input("New Username", key="register_username")
    new_password = st.text_input("New Password", type="password", key="register_password")
    if st.button("Register"):
        if new_username and new_password:
            res = requests.post(
                f"{API_URL}/users/register",
                json={"username": new_username, "password": new_password}
            )
            if res.ok:
                st.success("Registered successfully! You can now log in.")
            else:
                st.error(res.json().get("detail", "Registration failed."))
        else:
            st.warning("Please fill out both username and password.")


st.subheader("Login")
username = st.text_input("Username", key="login_username")
password = st.text_input("Password", type="password", key="login_password")

if st.button("Login"):
    if username and password:
        res = requests.post(
            f"{API_URL}/users/login",
            json={"username": username, "password": password}
        )
        if res.ok:
            token = res.json()["access_token"]
            st.session_state.token = token
            st.session_state.username = username
            st.success("Logged in!")
        else:
            st.error(res.json().get("detail", "Login failed"))
    else:
        st.warning("Enter both username and password.")


if st.session_state.token:
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.username = None
        st.success("Logged out.")
