import streamlit as st
from streamlit_extras.switch_page_button import switch_page


def sidebar_logout():
    with st.sidebar:
        col1, col2 = st.columns([1, 2])
        clicked = col1.button("Sign out", use_container_width=True)
        if clicked:
            st.session_state.is_authenticated = False
            switch_page('home')
