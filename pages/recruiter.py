import streamlit as st


def recruiter():
  st.write(f"Welcome {st.session_state.user['email']}")