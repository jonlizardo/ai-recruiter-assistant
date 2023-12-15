import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
from st_pages import show_pages, Page, hide_pages

import pandas as pd
import numpy as np

from google.cloud import firestore

from datetime import datetime
import random
import string

from utils.init import initialize_app
from utils.auth import signout
from utils.components import sidebar_logout, hide_navitems_from_sidebar, hide_seperator_from_sidebar, hide_sidebar
from utils.db import db

from ai.code_test_agent import assess_code

def reset_state():
    del st.session_state.test_started
    del st.session_state.participant_id
    del st.session_state.current_problem_index
    del st.session_state.submitted_current_problem

def candidate():
    # Page Config
    st.set_page_config(
        page_title="Test Room | Neuradev Coding Test Platform",
        initial_sidebar_state="expanded",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/candidate/1_Test_Room.py'),
    ])
    hide_pages(["create_new_test", "my_tests"])
    
    # Initialize session state
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'participant_id' not in st.session_state:
        st.session_state.participant_id = None
    if 'current_problem_index' not in st.session_state:
        st.session_state.current_problem_index = 0
    if 'submitted_current_problem' not in st.session_state:
        st.session_state.submitted_current_problem = False
    
    # Get test info
    test = db.collection("tests").document(st.session_state.test_code).get().to_dict()

    # If not started yet
    if not st.session_state.test_started:
        hide_sidebar()
    # If test started
    else:
        with st.sidebar:
            # Hide Navigation Items and Seperator from Sidebar
            hide_seperator_from_sidebar()
            hide_navitems_from_sidebar()
            
            # Add Components to sidebar
            st.header(f"⌚ Time Left: 82min 33s")
            # st.write(test['problems'][st.session_state.current_problem_index]['description'])
            df = pd.DataFrame(np.array([
                [
                    f"{i+1}. {problem['description']}",
                    '  ✔' if i < st.session_state.current_problem_index or (i == st.session_state.current_problem_index and st.session_state.submitted_current_problem)
                    else '⚫'
                ] for i, problem in enumerate(test['problems'])]), columns=("Problem", "Done"))
            
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={})
            
            with st.columns([1, 2])[0]:
                if st.session_state.current_problem_index < len(test["problems"]) - 1:
                    if st.button('Next Problem', type="primary", use_container_width=True, disabled=not st.session_state.submitted_current_problem):
                        st.session_state.current_problem_index += 1
                        st.session_state.submitted_current_problem = False
                        st.rerun()
                else:
                    st.button("Finish Test", type="primary", use_container_width=True, disabled=not st.session_state.submitted_current_problem)
    
    # Add Logout button to sidebar
    with st.sidebar:
        if st.columns([1, 2])[0].button("Sign out", use_container_width=True):
            reset_state()
            signout()
    
    # Main Section
    # If test not started
    if not st.session_state.test_started:
        if not test:
            st.header(f"😔 Oops! {st.session_state.user['first_name']}, there is no test with code {st.session_state.test_code}.")
            st.error(f"There is no test with code {st.session_state.test_code}")
            if st.columns([1, 2])[0].button("Sign out", key="Sign out button in main section", use_container_width=True):
                reset_state()
                signout()
        else:
            st.header(f"👋 Hi {st.session_state.user['first_name']}, welcome to the Test {st.session_state.test_code}!")
            with st.container(border=True):
                st.subheader("Test Details")
                st.write(f"✨ Topic: {test['topic']}")
                st.write(f"⛳ Total Problems: {len(test['problems'])}")
                st.write(f"⌚ Time Limit: {test['time_limit']} mins")
            cols = st.columns([1, 1, 2])
            with cols[0]:
                if st.button("Start Test", type="primary", use_container_width=True):
                    participant_id = "".join(random.choices(string.ascii_letters, k=10))
                    new_participant = {
                        "user": st.session_state.user,
                        "started_at": datetime.now(),
                        "finishd_at": None,
                        "solutions": [],
                        "overall_code_quality": 0,
                        "overall_rating": 0,
                        "total_passed": 0,
                    }
                    participants = test["participants"]
                    participants[participant_id] = new_participant
                    db.collection("tests").document(st.session_state.test_code).update({
                        "participants": participants
                    })
                    st.session_state.participant_id = participant_id
                    st.session_state.test_started = True
                    st.session_state.current_problem_index = 0
                    st.rerun()
            with cols[1]:
                if st.button("Sign Out", type="secondary", use_container_width=True):
                    signout()
    # If test started
    else:
        # st.subheader(f"Problem {st.session_state.current_problem_index + 1}. {test['problems'][st.session_state.current_problem_index]['description']}")
        st.subheader(f"Problem {st.session_state.current_problem_index + 1}")
        st.write(test['problems'][st.session_state.current_problem_index]['description'])
        # st.subheader(f"Enter your solution here")

        col1, col2 = st.columns([3, 2])
        language='python'
        language = col2.selectbox("Language mode", options=LANGUAGES, index=121)
        theme = col2.selectbox("Theme", options=THEMES, index=35)
        keybinding = col2.selectbox("Keybinding mode", options=KEYBINDINGS, index=3)
        font_size = col2.slider("Font size", 5, 24, 14)
        tab_size = col2.slider("Tab size", 1, 8, 4)
        wrap = col2.checkbox("Wrap enabled", value=False)
            
        with col1:
            with st.form("solution_form", border=False):
                solution_code = st_ace(
                    placeholder=("Write your code here"),
                    language=language,
                    theme=theme,
                    keybinding=keybinding,
                    font_size=font_size,
                    tab_size=tab_size,
                    wrap=wrap,
                    auto_update= True, #col2.checkbox("Auto update", value=True),
                    readonly=st.session_state.submitted_current_problem,
                    min_lines=30,
                    key="ace",
                )
                if st.columns([3, 2])[1].form_submit_button("🔥 Submit Solution" if not st.session_state.submitted_current_problem else "✔ Submitted", type="primary", disabled=st.session_state.submitted_current_problem, use_container_width=True):
                    if not solution_code:
                        st.error("Code should not be empty")
                    else:
                        passed, code_quality, overall_rating, reason = assess_code(problem=test["problems"][st.session_state.current_problem_index]["description"], code=solution_code)

                        participants = test["participants"]
                        participants[st.session_state.participant_id]["solutions"].append({
                            "code": solution_code,
                            "passed": passed,
                            "code_quality": code_quality,
                            "overall_rating": overall_rating,
                            "reason": reason,
                        })
                        
                        db.collection("tests").document(st.session_state.test_code).update({
                            "participants": participants
                        })
                        st.session_state.submitted_current_problem = True
                        st.rerun()

    
# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    if st.session_state.is_authenticated and st.session_state.role == "candidate":
        candidate()
    else:
        switch_page('home')