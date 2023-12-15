import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages, Page, hide_pages

from utils.init import initialize_app
from utils.auth import signout
from utils.components import sidebar_logout, hide_navitems_from_sidebar, hide_seperator_from_sidebar, hide_sidebar
from utils.db import db


def candidate():
    # Page Config
    st.set_page_config(
        page_title="Test Room | Neuradev Coding Test Platform",
        initial_sidebar_state="expanded",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/candidate/1_Test_Room.py'),
    ])
    hide_pages(["create_new_test", "my_tests"])
    
    # Initialize session state
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    
    test = db.collection("tests").document(st.session_state.test_code).get().to_dict()
    # Add Components to sidebar
    with st.sidebar:
        # If not started yet
        if not st.session_state.test_started:
            # Hide Sidebar
            hide_sidebar()
            # If test not found
            if not test:
                st.header(f"😔 Oops! {st.session_state.user['first_name']}, there is no test with code {st.session_state.test_code}.")
                st.error(f"There is no test with code {st.session_state.test_code}")
            #If test is available
            else:
                st.header(f"👋 Hi {st.session_state.user['first_name']}, welcome to the Test {st.session_state.test_code}!")
                with st.container(border=True):
                    st.subheader("Test Details")
                    st.write(f"✨ Topic: {test['topic']}")
                    st.write(f"⛳ Total Problems: {len(test['problems'])}")
                    st.write(f"⌚ Time Limit: {test['time_limit']} mins")
                with st.columns([1, 2])[0]:
                    st.button("Start Test", key="Start Test Button on Sidebar", type="primary", use_container_width=True)
        # If test started
        else:
            # Hide Navigation Items and Seperator from Sidebar
            hide_seperator_from_sidebar()
            hide_navitems_from_sidebar()
            
            st.header(f"Time Left: 82min 33s")
            with st.columns([1, 2])[0]:
                st.button("Finish Test", type="primary", use_container_width=True)
    
    # Add Logout button to sidebar
    sidebar_logout()
    
    # Main Section
    if not st.session_state.test_started:
        if not test:
            st.header(f"😔 Oops! {st.session_state.user['first_name']}, there is no test with code {st.session_state.test_code}.")
            st.error(f"There is no test with code {st.session_state.test_code}")
        else:
            st.header(f"👋 Hi {st.session_state.user['first_name']}, welcome to the Test {st.session_state.test_code}!")
            with st.container(border=True):
                st.subheader("Test Details")
                st.write(f"✨ Topic: {test['topic']}")
                st.write(f"⛳ Total Problems: {len(test['problems'])}")
                st.write(f"⌚ Time Limit: {test['time_limit']} mins")
            cols = st.columns([1, 1, 2])
            with cols[0]:
                st.button("Start Test", type="primary", use_container_width=True)
            with cols[1]:
                if st.button("Sign Out", type="secondary", use_container_width=True):
                    signout()
    else:
        st.header(f"Time Left: 82min 33s")
        with st.columns([1, 2])[0]:
            st.button("Finish Test", key="Start Test Button on Main Section", type="primary", use_container_width=True)
    
    
# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    if st.session_state.is_authenticated and st.session_state.role == "candidate":
        candidate()
    else:
        switch_page('home')