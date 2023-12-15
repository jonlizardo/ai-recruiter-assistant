import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from utils.init import initialize_app


def recruiter_new_test():
    # Page Config
    st.set_page_config(
        page_title="New Test | Neuradev Coding Test Platform",
        initial_sidebar_state="expanded",
    )
    
    # Header
    st.header("Create New Test")
    
    
# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    if st.session_state.is_authenticated and st.session_state.role == "recruiter":
        recruiter_new_test()
    else:
        switch_page('home')