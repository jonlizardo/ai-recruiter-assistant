import streamlit as st
from st_pages import show_pages, Page, hide_pages
from streamlit_extras.switch_page_button import switch_page
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, auth
from codeinterpreterapi import CodeInterpreterSession
import pyrebase
from datetime import date, datetime
from PIL import Image


cred = credentials.Certificate('neurakey.json')
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
try:
    firebase_admin.initialize_app(cred)
except:
    print('Already initialized')

db = firestore.Client.from_service_account_json("neurakey.json")

auth_admin = firebase_admin.auth

firebase = pb = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()


show_pages([
    Page("start.py","Start"),
    Page("main.py","Main"),
    Page("recruiter.py", "Recruiter")


])
hide_pages(['Start', 'Main'])

def get_coding_questions():
    doc_ref = db.collection('questions').get()
    return doc_ref

def start():
    # st.set_page_config(page_title="Neuradev Coding Challenge", page_icon="🧑🏾‍💻", initial_sidebar_state="collapsed")
    if 'first_name' not in st.session_state:
        st.session_state.first_name = ''
    if 'last_name' not in st.session_state:
        st.session_state.last_name = ''
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 1
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = []
    st.header("Eugene AI Testing Platform")
    image = Image.open("startimage.jpg")
    st.image(image)

    tab1, tab2 = st.tabs(['I am a Candidate', 'I am Hiring'])
    with tab1:
        st.session_state.first_name = st.text_input("Enter your first name")
        st.session_state.last_name = st.text_input("Enter your last name")
        if st.button('Start Coding Challenge', type='primary'):
            if 'correct_answers' not in st.session_state:
                st.session_state.correct_answers = []
            questions = get_coding_questions()
            for question in questions:
                print(question.to_dict())
                print(question.id)
                st.session_state.questions.append(question.to_dict())
                st.session_state.correct_answers.append(question.to_dict()['answer'])
                # with CodeInterpreterSession() as session:
                #     response = session.generate_response(
                #         f'provide the code in python to solve the following question: {question.to_dict()}')
                #     st.session_state.correct_answers.append(response.content)
                #     db.collection("questions").document(question.id).set({'answer': response.content}, merge=True)
            # st.session_state.question_index = 1
            switch_page('Main')

    with tab2:
        st.text('Welcome Hiring Manager. Please create your account or Login')
        email = st.text_input("Enter Your Email")
        password = st.text_input("Enter Your Password", type="password")
        # st.divider()
        col1, col2, col3 = st.columns([2, 2, 3])
        submitted = col1.button("Login ", type="primary", use_container_width=True)
        submitted2 = col2.button("Create My Account", type="primary", use_container_width=True)

        if submitted and email and password:
            try:
                with st.spinner("Please wait..."):
                    user = auth.sign_in_with_email_and_password(email, password)
                    print(f"SIGNED AS {user}")
                    if "user_email" not in st.session_state:
                        st.session_state.user_email = ""

                    st.session_state.user_email = email
                    #user_info = get_user_info(st.session_state.user_email)
                    # st.session_state.user_id = user_info["user_id"]
                    # if user_info["active"]:
                    #     st.session_state.authenticated = True
                    #     switch_page("Home")
                    switch_page("Recruiter")
                    # else:
                    #     st.error("This account has an Inactive subscription. Please visit https://www.eugenetest.ai to subscribe")
            except Exception as e:
                print(e)
                st.error(f"Invalid username or password")

        if submitted2 and email and password:
            with st.spinner("Creating your account.."):
                #first check if this user already exists
                users_info = db.collection('users').where('email', '==', email).get()
                if len(users_info) > 0:
                  st.error("This user already exists")

                else:
                    #now check if this user has subscribed
                    # users_sub = db.collection('new_subscription').where('email', '==', email).get()

                    try:
                        user = auth_admin.create_user(email=email, password=password)
                        print(f"User Id is {user.uid}")


                        db.collection("users").document(user.uid).set(
                            {
                                "email": email,
                                "user_id": user.uid,
                                "sign_up_date": datetime.utcnow().strftime(
                                    "%Y-%m-%dT%H:%M:%S.%fZ"
                                ),
                                "mode": "email/password",
                                "active": True,

                            }
                        )
                        if "user_email" not in st.session_state:
                            st.session_state.user_email = ""
                        if "user_id" not in st.session_state:
                            st.session_state.user_id = ""

                        st.session_state.user_email = email
                        st.session_state.user_id = user.uid

                        st.session_state.authenticated = True

                        st.success("Sign up successful!")

                        switch_page("Recruiter")

                    except Exception as e:
                        st.error("Sign up failed: {}".format(e))



if __name__ == "__main__":
    start()