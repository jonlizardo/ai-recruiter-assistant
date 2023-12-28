import streamlit as st

from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials


def initialize_app():
    # load .env file
    load_dotenv()

    # initialize firebase
    cred = credentials.Certificate('neurakey.json')
    try:
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'neurainterview.appspot.com'
        })
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
