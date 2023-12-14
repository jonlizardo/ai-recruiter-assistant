import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page

from PIL import Image
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials

from pages.home import home


def initialize_app():
    cred = credentials.Certificate('neurakey.json')
    try:
        firebase_admin.initialize_app(cred)
    except:
        print('Already initialized Firebase')


# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    home()
