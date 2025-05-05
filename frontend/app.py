import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Simple Notes App", page_icon="📝")

st.title("📝 Simple Notes App")

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None


# --- REGISTRATION SECTION ---
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


# --- LOGIN SECTION ---
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


# --- LOGOUT ---
if st.session_state.token:
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.username = None
        st.success("Logged out.")


# --- MAIN APP FUNCTIONALITY ---
if st.session_state.token:
    st.header(f"Welcome, {st.session_state.username} 👋")

    st.subheader("Create a New Note")
    title = st.text_input("Note Title")
    content = st.text_area("Note Content")

    if st.button("Add Note"):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        res = requests.post(f"{API_URL}/notes/", json={"title": title, "content": content}, headers=headers)
        if res.ok:
            st.success("Note added!")
        else:
            st.error("Failed to add note")

        st.subheader("Your Notes")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.get(f"{API_URL}/notes/", headers=headers)

    if res.ok:
        notes = res.json()
        for note in notes:
            st.markdown("---")
            st.markdown(f"### ✏️ {note['title']}")
            st.write(note["content"])
            
            if st.button("Translate to English", key=f"translate_{note['id']}"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                translation_res = requests.post(
                    f"{API_URL}/notes/translate",
                    json={"text": note["content"], "source_lang": "ru", "target_lang": "en"},
                    headers=headers
                )
                
                if translation_res.ok:
                    translation = translation_res.json()
                    st.success("Translation successful!")
                    st.markdown("**English Translation:**")
                    st.write(translation["translated_text"])
                else:
                    st.error("Translation failed. Please try again.")
                    if translation_res.status_code == 401:
                        st.warning("API key may be missing or invalid. Please check your API configuration.")
                    else:
                        st.warning(f"Error: {translation_res.text}")


            note_key = f"note_{note['id']}"

            with st.expander("Edit this note", expanded=False):
                new_title = st.text_input("Updated Title", value=note["title"], key=f"title_{note_key}")
                new_content = st.text_area("Updated Content", value=note["content"], key=f"content_{note_key}")

                if st.button("Update Note", key=f"update_{note_key}"):
                    res = requests.put(
                        f"{API_URL}/notes/{note['id']}",
                        json={"title": new_title, "content": new_content},
                        headers=headers
                    )
                    if res.ok:
                        st.success("Note updated! Refresh to see changes.")
                    else:
                        st.error("Failed to update note.")

                if st.button("Delete Note", key=f"delete_{note_key}"):
                    res = requests.delete(f"{API_URL}/notes/{note['id']}", headers=headers)
                    if res.ok:
                        st.success("Note deleted! Refresh to remove from view.")
                    else:
                        st.error("Failed to delete note.")
    else:
        st.error("Failed to fetch notes.")

