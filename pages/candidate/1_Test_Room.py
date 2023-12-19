import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
from streamlit.components.v1 import html
from st_pages import show_pages, Page, hide_pages

import pandas as pd
import numpy as np

from google.cloud import firestore

from datetime import datetime, timezone, timedelta
import random
import string
import math

from utils.init import initialize_app
from utils.auth import signout
from utils.components import sidebar_logout, hide_navitems_from_sidebar, hide_seperator_from_sidebar, hide_sidebar
from utils.db import db

from ai.code_test_agent import assess_code

def reset_state():
    del st.session_state.test_started
    del st.session_state.test_finished
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
    if 'test_finished' not in st.session_state:
        st.session_state.test_finished = False
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
            # st.header(test["participants"][st.session_state.participant_id]["started_at"])
            time_elapsed = datetime.now(timezone.utc) - datetime.strptime(f"{test['participants'][st.session_state.participant_id]['started_at']}", "%Y-%m-%d %H:%M:%S.%f%z")
            time_left = timedelta(minutes=test["time_limit"]).total_seconds() - time_elapsed.total_seconds()
            mins = time_left // 60
            secs = time_left % 60

            html(f"""<div id='timer' style='font-size: 28px; font-weight: 700; margin-bottom: 12px; color: white'> ⌚ Time Left: <span id='timer-content'>---</div>
<script>
let timeLeft = Math.floor({time_left});
const interval = window.setInterval(() => {{
    timeLeft--;
    if (timeLeft === 0) {{
        clearInterval(interval);
        const overlayElement = document.createElement('div');
        overlayElement.style.position = "absolute";
        overlayElement.style.left = '0';
        overlayElement.style.top = '0';
        overlayElement.style.width = '100%';
        overlayElement.style.height = '100%';
        overlayElement.style.background = '#00000077';
        overlayElement.style['z-index'] = '99999';
        window.parent.document.querySelector('[data-testid=stSidebar]').nextSibling.appendChild(overlayElement)
        document.getElementById("timer").innerHTML = " ⌚ Timer is over!"
    }}
    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    const formatted = (mins ? (mins + "min ") : "") + secs + "s";
    document.getElementById("timer-content").innerHTML = formatted;
}}, 1000);
</script>
<style>
body {{
    background-color: #262730
}}
</style>""", height=50)
            # st.write(test['problems'][st.session_state.current_problem_index]['description'])
            # df = pd.DataFrame(np.array([
            #     [
            #         f"{i+1}. {problem['description']}",
            #         '  ✔' if i < st.session_state.current_problem_index or (i == st.session_state.current_problem_index and st.session_state.submitted_current_problem)
            #         else '⚫'
            #     ] for i, problem in enumerate(test['problems'])]), columns=("Problem", "Done"))
            
            # st.dataframe(df, use_container_width=True, hide_index=True, column_config={})
            
            data_df = pd.DataFrame(
                {
                    "Done": ['  ✔' if i < st.session_state.current_problem_index or (i == st.session_state.current_problem_index and st.session_state.submitted_current_problem)
                        else '⚫' for i, problem in enumerate(test['problems'])],
                    "No": [i+1 for i, problem in enumerate(test["problems"])],
                    "Category": [problem["category"] for problem in test["problems"]],
                    "Time Limit": [f"{problem['time_limit']} mins" for problem in test["problems"]],
                    "Title": [problem["title"] for problem in test["problems"]],
                    "Description": [problem["description"] for problem in test["problems"]],
                }
            )
            st.dataframe(data_df, hide_index=True, column_config={
                "Done": st.column_config.TextColumn("")
            })
            
            with st.columns([1, 2])[0]:
                if st.session_state.current_problem_index < len(test["problems"]) - 1:
                    if st.button('Next Problem', type="primary", use_container_width=True, disabled=not st.session_state.submitted_current_problem):
                        st.session_state.current_problem_index += 1
                        st.session_state.submitted_current_problem = False
                        st.rerun()
                else:
                    if st.button("Finish Test", type="primary", use_container_width=True, disabled=not st.session_state.submitted_current_problem or st.session_state.test_finished):
                        participants = test["participants"]
                        me = st.session_state.participant_id
                        solutions = participants[me]["solutions"]
                        overall_rating = sum([solution["overall_rating"] for solution in solutions]) / len(solutions)
                        overall_code_quality = sum([solution["code_quality"] for solution in solutions]) / len(solutions)
                        total_passed = len([solution for solution in solutions if solution["passed"]])
                        finished_at = datetime.now()
                        
                        participants[me]["overall_rating"] = overall_rating
                        participants[me]["overall_code_quality"] = overall_code_quality
                        participants[me]["total_passed"] = total_passed
                        participants[me]["finished_at"] = finished_at

                        db.collection("tests").document(st.session_state.test_code).update({
                            "participants": participants
                        })
                        
                        st.success("🎆 You have successfully completed the test!")
                        st.session_state.test_finished = True
                        st.rerun()
                        
    
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
                        "started_at": datetime.now(timezone.utc),
                        "finished_at": None,
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
    # If test in progress
    elif not st.session_state.test_finished:
        problem = test['problems'][st.session_state.current_problem_index]
        st.subheader(f"Problem {st.session_state.current_problem_index + 1}. {problem['title']}")
        st.write(problem['description'])

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
                solution_explanation = st.text_area("Explanation")
                if st.columns([3, 2])[1].form_submit_button("🔥 Submit Solution" if not st.session_state.submitted_current_problem else "✔ Submitted", type="primary", disabled=st.session_state.submitted_current_problem, use_container_width=True):
                    if not solution_code:
                        st.error("Code should not be empty")
                    else:
                        passed, code_quality, explanation_rating, overall_rating, reason = assess_code(problem=test["problems"][st.session_state.current_problem_index]["description"], code=solution_code, explanation=solution_explanation)

                        participants = test["participants"]
                        participants[st.session_state.participant_id]["solutions"].append({
                            "code": solution_code,
                            "explanation": solution_explanation,
                            "passed": passed,
                            "code_quality": code_quality,
                            "explanation_rating": explanation_rating,
                            "overall_rating": overall_rating,
                            "reason": reason,
                        })
                        
                        db.collection("tests").document(st.session_state.test_code).update({
                            "participants": participants
                        })
                        st.session_state.submitted_current_problem = True
                        st.rerun()
    # If test finished
    else:
        my_test = test['participants'][st.session_state.participant_id]
        solutions = my_test['solutions']
        st.subheader(f"🎉 Congrats {st.session_state.user['first_name']}!")
        st.subheader(f"You have successfully completed the test.")
        with st.container(border=True):
            st.write(f"🔥 Overall Rating: {round(my_test['overall_rating'], 1)}/5")
            st.write(f"✨ Solved problems: {len([solution for solution in solutions if solution['passed']])}/{len(test['problems'])}")
            st.write(f"📚 Code quality: {round(my_test['overall_code_quality'], 1)}/5")
    
# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    if st.session_state.is_authenticated and st.session_state.role == "candidate":
        candidate()
    else:
        switch_page('home')