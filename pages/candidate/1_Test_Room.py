import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages, Page, hide_pages

from utils.init import initialize_app
from utils.components import sidebar_logout


def candidate():
    # Page Config
    st.set_page_config(
        page_title="My Tests | Neuradev Coding Test Platform",
        initial_sidebar_state="expanded",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/candidate/1_Test_Room.py'),
    ])
    hide_pages(["create_new_test", "my_tests"])
    
    # Add Logout button to sidebar
    sidebar_logout()
    
    # Header
    st.header("Candidate Page")

    st.write(f"Welcome {st.session_state.user['first_name']} {st.session_state.user['last_name']}. Your test code is {st.session_state.test_code}")
    
    
# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    if st.session_state.is_authenticated and st.session_state.role == "candidate":
        candidate()
    else:
        switch_page('home')