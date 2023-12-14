import streamlit as st
from PIL import Image

from utils.auth import signup, signin

# Home Page
def home():
    # Page Config
    st.set_page_config(
        page_title="Neuradev Coding Test Platform",
        initial_sidebar_state="collapsed",
    )
    
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
    st.markdown(
        """
        <style>
        [data-testid=stSidebar], [data-testid=collapsedControl] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    

# Candidate Login Form
def candidate_login_form():
    with st.form("candidate_login_form", border=False):
        first_name = st.text_input("Enter your first name")
        last_name = st.text_input("Enter your last name")
        test_code = st.text_input("Enter your test code")
        col1, col2 = st.columns([1, 3])
        col1.form_submit_button("Start My Test", type="primary", use_container_width=True)
        
    if first_name and last_name and test_code:
        st.write(f"Starting Test {test_code} as {first_name} {last_name}")
    

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
                    st.success("Successfully signed in.")
                else:
                    st.error(f"Failed to sign in. {payload}")
                
        if submitted_signup:
            with st.spinner("Creating your account..."):
                success, payload = signup(email, password)
                if success:
                    st.success("Created a new user successfully. Please log in.")
                else:
                    st.error(f"Failed to sign up. {payload}")
