import streamlit as st
from codeinterpreterapi import CodeInterpreterSession
from st_pages import show_pages, hide_pages, Page
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from streamlit_pills import pills
from utils import *


st.set_page_config(page_title="Hiring Manager", layout="wide")
show_pages([
    Page("start.py","Start"),
    Page("main.py","Main"),
    Page("recruiter.py", "Recruiter")


])
hide_pages(['Start', 'Main', 'Recruiter'])
def recruiter():
    
    if st.session_state.active_page == "Create New Test":
        create_coding_tests()
    
    if st.session_state.active_page == "My Tests":
        my_tests()
    


def create_coding_tests():
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = ""
    if 'split_questions' not in st.session_state:
        st.session_state.split_questions = []
    if 'generated_answers' not in st.session_state:
        st.session_state.generated_answers = ""
    if 'final_questions' not in st.session_state:
        st.session_state.final_questions = []

    if 'final_answers' not in st.session_state:
        st.session_state.final_answers = []

    st.header("Create a Candidate Coding Test", divider="red")


    if 'pill_index' not in st.session_state:
        st.session_state.pill_index = 0
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = []
    subject_options = ["", "Node JS", "Python", "Machine Learning & Deep Learning", "Java", "Javascript", "ASP.NET",
         "C#", "PHP", "MY SQL", "SQL Server", "GOLang", "C++", "Data Structures & Algorithms", "Ruby & Rails", "Rust", "LangChain", "llamaIndex", "Object Oriented Programming", "Unity", "Swift", "Objective-C" ],

    index=st.session_state.pill_index,
    selected = pills(
        "Select a test topic",
        options=["", "Node JS", "Python", "Machine Learning & Deep Learning", "Java", "Javascript", "ASP.NET",
         "C#", "PHP", "MY SQL", "SQL Server", "GOLang", "C++", "Data Structures & Algorithms", "Ruby & Rails", "Rust", "LangChain", "llamaIndex", "Object Oriented Programming", "Unity", "Swift", "Objective-C" ],

        index=st.session_state.pill_index,
    )
    if selected:
        st.session_state.selected_topics.append(selected)

    total_questions = st.number_input("How many questions would you like to generate?", min_value=1, max_value=100)

    level = st.selectbox("Level of Difficulty", ("Beginner", "Intermediate", "Advanced", "Expert"))

    duration = st.number_input("Test Duration (mins)", min_value=10, max_value=500, step=5)

    if  st.button("Generate Questions"):

        st.session_state.generated_questions = ""
        st.session_state.generated_answers = ""
        st.session_state.final_answers.clear()
        st.session_state.final_questions.clear()

        with st.spinner("Generating interview questions.. please wait"):
            quiz_response = create_prompt_template_returns_chain(num_questions=total_questions, quiz_type="Open Ended",
                                                                 quiz_context=selected, level=level)
            questions, answers = split_questions_answers(quiz_response)
            st.session_state.generated_answers = answers
            st.session_state.generated_questions = questions


            # with CodeInterpreterSession() as session:
            #     response = session.generate_response(
            #         f'Generate {total_questions} interview questions on the following subject: {selected}. Return just the questions and nothing else.')
            #     st.session_state.generated_questions = (response.content)
            #     st.session_state.split_questions = response.content.split("\n")
            #     print("This is the first split question")
            #     print(st.session_state.split_questions[0])

        with st.expander("Your Generated Questions", expanded=True):
            st.markdown(st.session_state.generated_questions)

            st.markdown(f"Answers: \n\n{st.session_state.generated_answers}")



    if len(st.session_state.generated_questions) > 0:
        st.subheader("Add your own questions to this list (optional)")
        # with st.form("add_mine") :
        col1, col2 = st.columns(2)
        with col1:
            my_question = st.text_area("Enter question here")
        with col2:
            my_answer = st.text_area("Enter the answer here")
        if st.button("Add this question") and my_question and my_answer:
            st.session_state.final_questions.append(my_question)
            st.session_state.final_answers.append(my_answer)
            st.success("Added this question")
            # st.session_state.generated_questions =  st.session_state.generated_questions.split("\n")
    try:
        st.session_state.generated_questions = st.session_state.generated_questions.split("\n")
        st.session_state.generated_answers = st.session_state.generated_answers.split("\n")
        for question in st.session_state.generated_questions:
            if any(substring in question for substring in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
                print(question)
                st.session_state.final_questions.append(question)
        for answer in st.session_state.generated_answers:
            if any(substring in answer for substring in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
                print(answer)
                st.session_state.final_answers.append(answer)
    except:
        pass

    st.write(st.session_state.final_questions)
    st.write(st.session_state.final_answers)

    if len(st.session_state.generated_questions) > 0:
        if st.button("Create A Test", type='primary'):
            import random
            import string
            rand = "".join(random.choices(string.digits, k=5))
            create_test_return_code(questions=st.session_state.final_questions, answers=st.session_state.final_answers,
                                    code=rand, expiry="2029-01-01", owner=st.session_state.user_email, subject_area=selected, num_questions=total_questions, level=level, duration=duration, participants=dict())
            st.success(f"Test created successfully with code {rand}. Please share this code with the candidate.")
            st.session_state.generated_questions = ""
            st.session_state.generated_answers = ""
            st.session_state.final_answers.clear()
            st.session_state.final_questions.clear()

def side_bar():
    if "index" not in st.session_state:
        st.session_state.index = 0
    selected = option_menu(
        menu_title=None,
        options=[
            "Create New Test",
            "My Tests",
            "Log out",
        ],
        icons=[
            "file-plus-fill",
            "newspaper",
            "box-arrow-right",
        ],
        menu_icon=None,
        default_index=st.session_state.index,
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent",
            }
        },
    )

    if selected == "Create New Test":
        st.session_state.active_page = "Create New Test"

    if selected == "My Tests":
        st.session_state.active_page = "My Tests"

    if selected == "Log out":
        # st.session_state.pop("authenticated")
        # st.session_state.pop("user_email")
        switch_page("start")

def my_tests():
    st.header("My Tests", divider="red")
    my_tests = get_my_tests(owner=st.session_state.user_email)

    # create streamlit table with my_tests array data
    # st.table([
    #     {
    #         "questions": '\n'.join(test.get('questions')),
    #         "date_created": test.get('date_created'),
    #     }
    #     for test in my_tests
    # ])

    tabs = st.tabs([test.id for test in my_tests])
    for i, tab in enumerate(tabs):
        test = my_tests[i]
        with tab:
            st.text(f"Subject: {test.get('subject') if test.get('subject') else 'N/A' } | Total {test.get('num_questions')} questions | Difficulty level: {test.get('difficulty_level')} |Duration: {test.get('duration')} mins | Expires at {test.get('expiry')}")
            st.text(f"Created by {test.get('owner')} at {test.get('date_created').strftime('%Y-%m-%d %H:%M:%S')}")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Problems')
                for j, question in enumerate(test.get('questions')):
                    st.write(question)
            with col2:
                st.subheader('Participants')
                participants = list(test.to_dict()['participants'].values())

                for j, participant in enumerate(participants):
                    score = sum(answer["passed"] for k, answer in enumerate(participant['answers']))
                    total = test.get('num_questions')
                    with st.expander(f"{participant['first_name']} {participant['last_name']} ({participant['id']}) | {f'Finished | Score: {score}/{total}' if participant['finished'] else 'In progress'}"):
                        if len(participant['answers']) > 0:
                            answer_tabs = st.tabs([f"Problem {k + 1}" for k, answer in enumerate(participant['answers'])])
                            for k, answer_tab in enumerate(answer_tabs):
                                answer = participant['answers'][k]
                                with answer_tab:
                                    if answer['passed']:
                                        st.success('Passed')
                                    else:
                                        st.error('Failed')
                                    st.write(answer['description'])
if __name__ == '__main__':
    with st.sidebar:
        side_bar()
    recruiter()