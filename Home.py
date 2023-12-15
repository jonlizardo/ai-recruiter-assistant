import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages, Page, hide_pages

from PIL import Image

from utils.init import initialize_app
from utils.auth import signup, signin
from utils.components import hide_sidebar


# Home Page
def home():
    # Page Config
    st.set_page_config(
        page_title="Neuradev Coding Test Platform",
        initial_sidebar_state="collapsed",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/recruiter/1_Create_New_Test.py'),
        Page(path='pages/recruiter/2_My_Tests.py'),
        Page(path='pages/candidate/1_Test_Room.py'),
    ])

    # Header
    st.header("Eugene AI Testing Platform")
    
    # Hero Image
    hero_image = Image.open('assets/images/starter.jpg')
    st.image(hero_image)

    # Candidate/Recruiter Tabs
    tab1, tab2 = st.tabs(['I am a Candidate', 'I am Hiring'])
    with tab1:
        candidate_login_form()
    with tab2:
        recruiter_login_form()
    
    # Hide Sidebar
    hide_sidebar()
    

# Candidate Login Form
def candidate_login_form():
    with st.form("candidate_login_form", border=False):
        first_name = st.text_input("Enter your first name")
        last_name = st.text_input("Enter your last name")
        test_code = st.text_input("Enter your test code")
        col1, col2 = st.columns([1, 3])
        col1.form_submit_button("Start My Test", type="primary", use_container_width=True)
        
    if first_name and last_name and test_code:
        st.session_state.user = {
            "first_name": first_name,
            "last_name": last_name,
        }
        st.session_state.role = "candidate"
        st.session_state.test_code = test_code 
        st.session_state.is_authenticated = True
        st.rerun()
    

# Recruiter Login Form
def recruiter_login_form():
    with st.form("recruiter_login_form", border=False):
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password", type="password")
        col1, col2, col3 = st.columns([1.5, 2, 3])
        submitted_login = col1.form_submit_button("Login", type="primary", use_container_width=True)
        submitted_signup = col2.form_submit_button("Create a new account", type="secondary", use_container_width=True)
    
    if email and password:
        if submitted_login:
            with st.spinner("Please wait..."):
                success, payload = signin(email, password)
                if success:
                    st.session_state.user = payload
                    st.session_state.role = "recruiter"
                    st.session_state.is_authenticated = True
                    st.rerun()
                else:
                    st.error(f"Failed to sign in. Email or password is incorrrect.")
                
        if submitted_signup:
            with st.spinner("Creating your account..."):
                success, payload = signup(email, password)
                if success:
                    st.success("Created a new user successfully. Please log in.")
                else:
                    st.error(f"Failed to sign up. {payload}")


# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    if st.session_state.is_authenticated:
        if st.session_state.role == "recruiter":
            switch_page('create_new_test')
        elif st.session_state.role == "candidate":
            switch_page('test_room')
        else:
            home()
    else:
        home()
