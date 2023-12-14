import streamlit as st


def candidate():
    st.write(f"Welcome {st.session_state.user['first_name']} {st.session_state.user['last_name']}. Your test code is {st.session_state.test_code}")