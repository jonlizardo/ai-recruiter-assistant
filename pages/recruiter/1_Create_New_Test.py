import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_pills import pills
from st_pages import show_pages, Page, hide_pages

from google.cloud import firestore

from utils.init import initialize_app
from utils.components import sidebar_logout
from utils.db import db


def create_new_test():
    # Page Config
    st.set_page_config(
        page_title="New Test | Neuradev Coding Test Platform",
        initial_sidebar_state="expanded",
    )
    
    # Show/Hide Pages on Sidebar
    show_pages([
        Page(path='Home.py'),
        Page(path='pages/recruiter/1_Create_New_Test.py'),
        Page(path='pages/recruiter/2_My_Tests.py'),
    ])
    hide_pages(["candidate"])
    
    # Add Logout button to sidebar
    sidebar_logout()
    
    # Header
    st.header("Create New Test")
    
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
            index=-1
        )
        
        col1, col2 = st.columns([1, 1])

        with col1:
            with st.container(border=True):
                st.subheader("Problems")
                for i, problem in enumerate(st.session_state.problems):
                    st.write(f"{i + 1}. {problem['description']}")

        with col2:
            with st.container(border=True):
                st.subheader("Select Problems")
                tabs = st.tabs(["Add New Problem", "Select From Existing Problems"])
                with tabs[0]:
                    new_problem_description = st.text_area("Description")
                    new_problem_category = st.selectbox("Category", ("Basic", "Algorithm", "Practice"))
                    if st.form_submit_button("Save and Add", type="primary"):
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
                                        "created_at": firestore.SERVER_TIMESTAMP,
                                        "creator": "test_user_id"
                                    })[1]
                                    st.session_state.problems.append(new_problem.get().to_dict())
                                    st.success("Successfully saved")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to save: {e}")
                        
                with tabs[1]:
                    st.write('hi')
            
        st.form_submit_button("Save Test", type="primary")


# Run the Streamlit app
if __name__ == '__main__':
    initialize_app()
    
    create_new_test()

    # if st.session_state.is_authenticated and st.session_state.role == "recruiter":
    #     create_new_test()
    # else:
    #     switch_page('home')