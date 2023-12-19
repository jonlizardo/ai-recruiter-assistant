import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_pills import pills
from st_pages import show_pages, Page, hide_pages

import pandas as pd

from google.cloud.firestore_v1.base_query import FieldFilter

from datetime import datetime

from utils.db import db
from utils.auth import signout
from utils.init import initialize_app
from utils.cypher import calculate_hash
from utils.components import sidebar_logout, hide_seperator_from_sidebar
from utils.constants import categories, topics

import random
import string


def reset_state():
    del st.session_state.problem_hashes
    del st.session_state.selected_topic

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
    if 'problem_hashes' not in st.session_state:
        st.session_state.problem_hashes = []
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    
    
    # Form
    selected_topic = pills(
        "Select a test topic",
        options=topics,
    )
    if st.session_state.selected_topic != selected_topic:
        st.session_state.problem_hashes = []
    st.session_state.selected_topic = selected_topic
    all_problems = [document.to_dict() for document in db.collection("problems")
                    .where(filter=FieldFilter('topic', '==', selected_topic))
                    .get()]
    problem_dict = {}
    hash_selected_dict = {}
    for problem in all_problems:
        problem_dict[problem["hash"]] = problem
        hash_selected_dict[problem["hash"]] = False
    for hash in st.session_state.problem_hashes:
        print(hash)
        hash_selected_dict[hash] = True
    selected_problems = [problem_dict[hash] for hash in st.session_state.problem_hashes]
    unselected_problems = [problem for problem in all_problems if not hash_selected_dict[problem["hash"]]]
    estimated_test_time_limit = sum([problem["time_limit"] for problem in selected_problems])
    
    with st.form("new_test_form", border=False):
        with st.columns([1, 3])[0]:
            test_time_limit = st.number_input("Time limit (in minutes)", min_value=10, step=1, value=max(estimated_test_time_limit, 10))
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.container(border = False):
                st.subheader("Selected Problems")
                if len(selected_problems) > 0:
                    remove_submitted = st.form_submit_button("Remove from Test")
                    selected_data_df = pd.DataFrame(
                        {
                            "selected": [False for problem in selected_problems],
                            "Category": [problem["category"] for problem in selected_problems],
                            "Time Limit": [f"{problem['time_limit']} mins" for problem in selected_problems],
                            "Title": [problem["title"] for problem in selected_problems],
                            "Description": [problem["description"] for problem in selected_problems],
                        }
                    )
                    selecetd_edited_df = st.data_editor(
                        selected_data_df,
                        column_config={
                            "selected": st.column_config.CheckboxColumn(
                                "",
                                help="Select problems to add.",
                                default=False,
                            ),
                        },
                        disabled=["Title", "Time Limit", "Description", "Category"],
                        hide_index=True,
                    )
                    if remove_submitted:
                        selected_indices = selecetd_edited_df["selected"].to_list()
                        st.session_state.problem_hashes = [hash for i, hash in enumerate(st.session_state.problem_hashes) if not selected_indices[i]]
                        st.rerun()
                        
                    cols = st.columns([1, 1, 1])
                    with cols[1]:    
                        save_test = st.form_submit_button("Save Test", type="primary", use_container_width=True)
                    with cols[2]:    
                        reset_problems = st.form_submit_button("Reset", type="secondary", use_container_width=True)

                    if save_test:
                        with st.spinner("Saving..."):
                            try:
                                new_test_code = "".join(random.choices(string.digits, k=5))
                                db.collection("tests").document(new_test_code).set({
                                    "creator": st.session_state.user["email"],
                                    "created_at": datetime.now(),
                                    "topic": selected_topic,
                                    "participants": {},
                                    "time_limit": test_time_limit,
                                    "problems": selected_problems
                                })
                                st.success(f"Successfully saved! Test code: {new_test_code}")
                            except Exception as e:
                                st.error(f"Failed to save: {e}")

                    if reset_problems:
                        st.session_state.problem_hashes = []
                        st.rerun()
                        
                else:
                    st.write("No problem selected")
        with col2:
            with st.container(border = False):
                st.subheader("Problem Bank")
                add_submitted = st.form_submit_button("Add to Test")
                if len(unselected_problems) > 0:
                    unselected_data_df = pd.DataFrame(
                        {
                            "selected": [False for problem in unselected_problems],
                            "Category": [problem["category"] for problem in unselected_problems],
                            "Time Limit": [f"{problem['time_limit']} mins" for problem in unselected_problems],
                            "Title": [problem["title"] for problem in unselected_problems],
                            "Description": [problem["description"] for problem in unselected_problems],
                        }
                    )
                    unselected_edited_df = st.data_editor(
                        unselected_data_df,
                        column_config={
                            "selected": st.column_config.CheckboxColumn(
                                "",
                                help="Select problems to add.",
                                default=False,
                            ),
                        },
                        disabled=["Title", "Time Limit", "Description", "Category"],
                        hide_index=True,
                    )
                    if add_submitted:
                        selected_indices = unselected_edited_df["selected"].to_list()
                        st.session_state.problem_hashes += [problem["hash"] for i, problem in enumerate(unselected_problems) if selected_indices[i]]
                        st.rerun()
                else:
                    st.write("No problem to select")
                with st.expander("Create New Problem"):
                    st.text_input("Topic", value=selected_topic, disabled=True)
                    new_problem_title = st.text_input("Title")
                    new_problem_description = st.text_area("Description")
                    new_problem_category = st.selectbox("Category", categories, format_func=lambda category: f"{category} Problems")
                    new_problem_time_limit = st.number_input("Time Limit (mins)", step=1, min_value=5)
                    if st.form_submit_button("Save and Add"):
                        if not selected_topic:
                            st.error("Select a test topic")
                        elif not new_problem_title:
                            st.error("Title should not be empty.")
                        elif not new_problem_description:
                            st.error("Description should not be empty.")
                        elif not new_problem_category:
                            st.error("Select a category")
                        elif not new_problem_time_limit:
                            st.error("Enter time limit")
                        else:
                            with st.spinner("Saving..."):
                                try:
                                    hash = calculate_hash(new_problem_description)
                                    db.collection("problems").add({
                                        "topic": selected_topic,
                                        "title": new_problem_title,
                                        "description": new_problem_description,
                                        "time_limit": new_problem_time_limit,
                                        "category": new_problem_category,
                                        "created_at": datetime.now(),
                                        "creator": st.session_state.user["email"],
                                        "hash": hash
                                    })[1]
                                    st.session_state.problem_hashes.append(hash)
                                    st.success("Successfully saved")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to save: {e}")
                with st.expander("Random Select"):
                    problem_counts = [0] * len(categories)
                    for i, category in enumerate(categories):
                        problem_counts[i] = st.number_input(category, step=1, min_value=0, key=f"Problem Counts for {category}")
                    if st.form_submit_button("Randomly Select and Add"):
                        if sum(problem_counts) == 0:
                            st.error("You should be select one or more problems")
                        else:
                            for i, category in enumerate(categories):
                                problem_count = problem_counts[i]
                                category_problems = list(filter(lambda problem: problem['category'] == category, unselected_problems))
                                random_indices = random.sample(range(len(category_problems)), min(len(category_problems), problem_count))
                                for index in random_indices:
                                    st.session_state.problem_hashes.append(category_problems[index]["hash"])
                            st.rerun()

# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()

    if st.session_state.is_authenticated and st.session_state.role == "recruiter":
        create_new_test()
    else:
        switch_page('home')