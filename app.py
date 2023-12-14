import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page

from PIL import Image
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials

from pages.home import home
from pages.recruiter import recruiter
from pages.candidate import candidate


def initialize_app():
    # initialized firebase
    cred = credentials.Certificate('neurakey.json')
    try:
        firebase_admin.initialize_app(cred)
    except:
        print('Already initialized Firebase')
        
    # initizalize state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'test_code' not in st.session_state:
        st.session_state.test_code = False


# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    if st.session_state.is_authenticated:
        if st.session_state.role == "recruiter":
            recruiter()
        elif st.session_state.role == "candidate":
            candidate()
        else:
            home()
    else:
        home()
