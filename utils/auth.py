import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from firebase_admin import auth as auth_admin
import pyrebase
from datetime import datetime

from .db import db

firebaseConfig = {
    "apiKey": "AIzaSyD3ndHauNbDHzJ9RPezh_u7h1_diyNfhuw",
    "authDomain": "neurainterview.firebaseapp.com",
    "projectId": "neurainterview",
    "storageBucket": "neurainterview.appspot.com",
    "messagingSenderId": "960636332151",
    "databaseURL": "xxxxxx",
    "appId": "1:960636332151:web:16c9b1a1cf6b0df0423e72",
    "measurementId": "G-HBX31ZE5X3"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


def signin(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        return False, f"{e}"

def signup(email, password):
    # check if user already exists
    user_info = db.collection('users').where('email', '==', email).get()
    if len(user_info) > 0:
        return False, f"User with {email} already exists"
    
    try:
        user = auth_admin.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set(
            {
                "email": email,
                "user_id": user.uid,
                "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "mode": "email/password",
                "active": True,
            }
        )
        return True, user.uid
    except Exception as e:
        return False, f"{e}"
    
def signout():
    st.session_state.is_authenticated = False
    switch_page('home')