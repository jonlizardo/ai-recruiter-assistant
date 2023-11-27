import streamlit as st
from codeinterpreterapi import CodeInterpreterSession
from streamlit_pills import pills

def recruiter():
    st.set_page_config(page_title="Hiring Manager", layout="wide")
    create_coding_tests()

def create_coding_tests():
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []

    st.header("Create a Candidate Coding Test", divider="red")


    if 'pill_index' not in st.session_state:
        st.session_state.pill_index = 0
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = []
    subject_options = ["", "Node JS", "Python", "Machine Learning & Deep Learning", "Java", "Javascript", "ASP.NET",
         "C#", "PHP", "MY SQL", "SQL Server", "GOLang", "C++", "Data Structures & Algorithms", "Ruby & Rails", "Rust", "LangChain", "llamaIndex", "Object Oriented Programming", "Unity", "Agile Methodology", "Scrum" ],

    index=st.session_state.pill_index,
    selected = pills(
        "Select a test topic",
        options=["", "Node JS", "Python", "Machine Learning & Deep Learning", "Java", "Javascript", "ASP.NET",
         "C#", "PHP", "MY SQL", "SQL Server", "GOLang", "C++", "Data Structures & Algorithms", "Ruby & Rails", "Rust", "LangChain", "llamaIndex", "Object Oriented Programming", "Unity", "Agile Methodology", "Scrum" ],

        index=st.session_state.pill_index,
    )
    if selected:
        st.session_state.selected_topics.append(selected)

    total_questions = st.number_input("How many questions would you like to generate?", min_value=1, max_value=100)

    if  st.button("Generate Questions"):
        st.session_state.generated_questions.clear()
        with st.spinner("Generating interview questions.. please wait"):

            with CodeInterpreterSession() as session:
                response = session.generate_response(
                    f'Generate {total_questions} interview questions on the following subject: {selected}. Return just the questions and nothing else.')
                st.session_state.generated_questions.append(response.content)
        with st.expander("Your Generated Questions"):
            st.markdown(response.content)
            split_questions = response.content.split("\n")
            print(split_questions[0])


            if len(st.session_state.generated_questions) > 0:
                st.subheader("Add your own questions to this list (optional)")
                with st.form("add_mine"):
                    my_questions = st.text_area("Enter question here")
                    my_add_button = st.form_submit_button("Add this question")


if __name__ == '__main__':
    recruiter()