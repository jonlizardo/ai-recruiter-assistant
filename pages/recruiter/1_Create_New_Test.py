import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_pills import pills
from st_pages import show_pages, Page, hide_pages

from datetime import datetime

from utils.db import db
from utils.auth import signout
from utils.init import initialize_app
from utils.components import sidebar_logout, hide_seperator_from_sidebar
from utils.constants import categories

import random
import string


def reset_state():
    del st.session_state.problems

def create_new_test():
    # Page Config
    st.set_page_config(
        page_title="New Test | Neuradev Coding Test Platform",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/recruiter/1_Create_New_Test.py'),
        Page(path='pages/recruiter/2_My_Tests.py'),
    ])
    hide_pages(["candidate"])
    
    # Hide seperator on Sidebar
    hide_seperator_from_sidebar()
    
    # Add Logout button to sidebar
    with st.sidebar:
        if st.columns([1, 2])[0].button("Sign out", use_container_width=True):
            reset_state()
            signout()
    
    # Header
    st.header("Create New Test")
    
    # Initialize session state
    if 'problems' not in st.session_state:
        st.session_state.problems = []
    
    # Form
    with st.form("new_test_form", border=False):
        selected_topic = pills(
            "Select a test topic",
            options=[
                "Node JS", "Python", "Machine Learning & Deep Learning", "Java", "Javascript", "ASP.NET", "C#",
                "PHP", "MY SQL", "SQL Server", "GOLang", "C++", "Data Structures & Algorithms","Ruby & Rails",
                "Rust", "LangChain", "llamaIndex", "Object Oriented Programming", "Unity", "Swift", "Objective-C"
            ],
        )
        
        with st.columns([1, 3])[0]:
            time_limit = st.number_input("Time limit (in minutes)", min_value=10, step=5)
        
        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=False):
                    st.subheader("Problems")
                    if len(st.session_state.problems) == 0:
                        st.write("No problem selected")
                    else:
                        for i, problem in enumerate(st.session_state.problems):
                            st.write(f"{i + 1}. {problem['description']}")
                        
                        cols = st.columns([1, 1, 1])
                        with cols[1]:    
                            save_test = st.form_submit_button("Save Test", type="primary")
                        with cols[2]:    
                            reset_problems = st.form_submit_button("Reset", type="secondary")

                        if save_test:
                            with st.spinner("Saving..."):
                                try:
                                    new_test_code = "".join(random.choices(string.digits, k=5))
                                    db.collection("tests").document(new_test_code).set({
                                        "creator": st.session_state.user["email"],
                                        "created_at": datetime.now(),
                                        "topic": selected_topic,
                                        "participants": {},
                                        "time_limit": time_limit,
                                        "problems": st.session_state.problems
                                    })
                                    st.success(f"Successfully saved! Test code: {new_test_code}")
                                except Exception as e:
                                    st.error(f"Failed to save: {e}")

                        if reset_problems:
                            st.session_state.problems = []
                            st.rerun()

            with col2:
                with st.container(border=False):
                    st.subheader("Select Problems")
                    tabs = st.tabs(["Select From Existing Problems", "Add New Problem"])
                    with tabs[0]:
                        problem_counts = [0] * len(categories)
                        for i, category in enumerate(categories):
                            col1, col2 = st.columns([1, 1])
                            col1.text(category)
                            problem_counts[i] = col2.number_input("Count", step=1, label_visibility="collapsed", min_value=0, key=f"Problem Counts for {category}")
                        if st.form_submit_button("Random Select"):
                            if sum(problem_counts) == 0:
                                st.error("You should be select one or more problems")
                            else:
                                all_problems = [document.to_dict() for document in db.collection("problems").where('topic', '==', selected_topic).get()]
                                for i, category in enumerate(categories):
                                    problem_count = problem_counts[i]
                                    category_problems = list(filter(lambda problem: problem['category'] == category, all_problems))
                                    random_indices = random.sample(range(len(category_problems)), min(len(category_problems), problem_count))
                                    for index in random_indices:
                                        st.session_state.problems.append(category_problems[index])
                                st.rerun()
                                
                    with tabs[1]:
                        st.text_input("Topic", value=selected_topic, disabled=True)
                        new_problem_description = st.text_area("Description")
                        new_problem_category = st.selectbox("Category", ("Basic", "Algorithm", "Practice"))
                        if st.form_submit_button("Save and Add"):
                            if not selected_topic:
                                st.error("Select a test topic")
                            elif not new_problem_description:
                                st.error("Description should not be empty.")
                            elif not new_problem_category:
                                st.error("Select a category")
                            else:
                                with st.spinner("Saving..."):
                                    try:
                                        new_problem = db.collection("problems").add({
                                            "topic": selected_topic,
                                            "description": new_problem_description,
                                            "category": new_problem_category,
                                            "created_at": datetime.now(),
                                            "creator": st.session_state.user["email"],
                                        })[1]
                                        st.session_state.problems.append(new_problem.get().to_dict())
                                        st.success("Successfully saved")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to save: {e}")


# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()

    if st.session_state.is_authenticated and st.session_state.role == "recruiter":
        create_new_test()
    else:
        switch_page('home')