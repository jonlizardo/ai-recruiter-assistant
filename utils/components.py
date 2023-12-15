import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from utils.auth import signout


def sidebar_logout():
    with st.sidebar:
        if st.columns([1, 2])[0].button("Sign out", use_container_width=True):
            signout()

def hide_sidebar():
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
    
def hide_seperator_from_sidebar():
    st.markdown(
        """
        <style>
        [data-testid=stSidebarNavSeparator] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
def hide_navitems_from_sidebar():
    st.markdown(
        """
        <style>
        [data-testid=stSidebarNavItems] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
