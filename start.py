import streamlit as st
from st_pages import show_pages, Page, hide_pages
from streamlit_extras.switch_page_button import switch_page
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from codeinterpreterapi import CodeInterpreterSession
cred = credentials.Certificate('neurakey.json')
try:
    firebase_admin.initialize_app(cred)
except:
    print('Already initialized')

db = firestore.Client.from_service_account_json("neurakey.json")
show_pages([
    Page("start.py","Start"),
    Page("main.py","Main")


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
    st.header("Neuradev AI Coding Challenge")
    st.text("Welcome to your neuradev.ai coding challenge")
    st.session_state.first_name = st.text_input("Enter your first name")
    st.session_state.last_name = st.text_input("Enter your last name")
    if st.button('Start Coding Challenge'):
        if 'correct_answers' not in st.session_state:
            st.session_state.correct_answers = []
        questions = get_coding_questions()
        for question in questions:
            print(question.to_dict())
            print(question.id)
            st.session_state.correct_answers.append(question.to_dict()['answer'])
            # with CodeInterpreterSession() as session:
            #     response = session.generate_response(
            #         f'provide the code in python to solve the following question: {question.to_dict()}')
            #     st.session_state.correct_answers.append(response.content)
            #     db.collection("questions").document(question.id).set({'answer': response.content}, merge=True)
        st.session_state.question_index = 1
        switch_page('Main')


if __name__ == "__main__":
    start()