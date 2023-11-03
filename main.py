import streamlit as st
from codeinterpreterapi import CodeInterpreterSession

from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
import os
from google.cloud import firestore
import openai
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import  load_dotenv, find_dotenv
from langchain.schema import BaseOutputParser
import  re
from utils import split_into_list_return_question_answers, ask_serp_agent, get_gorilla_response, return_code
import firebase_admin
from firebase_admin import credentials
from datetime import  datetime
import  asyncio
from camera_input_live import camera_input_live

cred = credentials.Certificate('neurakey.json')
try:
    firebase_admin.initialize_app(cred)
except:
    print('Already initialized')

db = firestore.Client.from_service_account_json("neurakey.json")


def create_prompt_template_returns_chain(num_questions=1, quiz_type='Multiple-Choice', quiz_context=''):
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a quiz with {num_questions} {quiz_type} questions about the following concept/content: {quiz_context}.

    The format of the quiz could be one of the following:
    - Multiple-choice: 
    - Questions:
        <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
        <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
        ....
    - Answers:
        <Answer1>: <a|b|c|d>
        <Answer2>: <a|b|c|d>
        ....
        Example:
        - Questions:
        - 1. What is the time complexity of a binary search tree?
            a. O(n)
            b. O(log n)
            c. O(n^2)
            d. O(1)
        - Answers: 
            1. b
    - True-false:
        - Questions:
            <Question1>: <True|False>
            <Question2>: <True|False>
            .....
        - Answers:
            <Answer1>: <True|False>
            <Answer2>: <True|False>
            .....
        Example:
        - Questions:
            - 1. What is a binary search tree?           
        - Answers:
            - 1. True

    - Open-ended:
    - Questions:
        <Question1>: 
        <Question2>:
    - Answers:    
        <Answer1>:
        <Answer2>:
    Example:
        Questions:
        - 1. What is a binary search tree?
        - 2. How are binary search trees implemented?

        - Answers: 
            1. A binary search tree is a data structure that is used to store data in a sorted manner.
            2. Binary search trees are implemented using linked lists.
    """

    prompt = PromptTemplate.from_template(template)
    prompt.format(num_questions=num_questions, quiz_type=quiz_type, quiz_context=quiz_context)
    chain = LLMChain(llm=ChatOpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY')),
                     prompt=prompt)
    return chain.run(num_questions=num_questions, quiz_type=quiz_type, quiz_context=quiz_context)


def get_response(prompt):
    response = openai.ChatCompletion.create(api_key='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',
                                            model='gpt-4',
                                            messages=[{'role': 'system',
                                                       'content': 'You are a helpful researcher and programming assistant'},
                                                      {'role': 'user', 'content': prompt}])
    return response['choices'][0]['message']['content']


def split_questions_answers(quiz_response):
    """Function that splits the questions and answers from the quiz response."""

    splitted = quiz_response.split("Answers:")
    print(f'Question and Answer list count is {len(splitted)}')
    questions = splitted[0]
    print(f'Questions are {questions}')

    if len(splitted) == 1:
        splitted2 = questions.split("Answer:")
        answers = splitted2[1]
    else:
        answers = quiz_response.split("Answers:")[1]
    print(f'Answers are {answers}')
    return questions, answers


def initialize_state():
    if 'questions' not in st.session_state:
        st.session_state.questions = ''
    if 'answers' not in st.session_state:
        st.session_state.answers = ''
    if 'question_type' not in st.session_state:
        st.session_state.question_type = ''
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = []

def get_coding_questions():
    doc_ref = db.collection('questions').get()
    return doc_ref

def score_candidate(firstname, lastname, score:int):
    db = firestore.Client.from_service_account_json("neurakey.json")
    db.collection("tests").add(
        {
        "first_name": firstname,
        'last_name': lastname,
        'score': score,
        "test_date": datetime.now()
    }
    )





# async def watch(t: st._DeltaGenerator):
#     while True:
#         t.markdown(
#             f"""
#             <p class="time">
#                 {str(datetime.now(    ))}
#             </p>
#             """, unsafe_allow_html=True)
#         await asyncio.sleep(1)
#         st.experimental_rerun()  # <-- here

def main():
    # with readme("streamlit-ace", st_ace, __file__):
    load_dotenv()
    initialize_state()
    questions = get_coding_questions()
    st.set_page_config('neuradev.ai coding platform', layout='wide')
    # st.markdown("""
    #     <style>
    #     [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
    #         gap: 0rem;
    #     }
    #     </style>
    #     """, unsafe_allow_html=True)

    c2, c1,  = st.columns([1, 3])

    with st.sidebar:
        # st.markdown(
        #     """
        #     <style>
        #     .time {
        #         font-size: 40px !important;
        #         font-weight: 100 !important;
        #         color: #ec5953 !important;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True
        # )
        #
        # test = st.empty()
        # while True:
        #     st._DeltaGenerator.markdown(
        #         f"""
        #            <p class="time">
        #                {str(datetime.now())}
        #            </p>
        #            """, unsafe_allow_html=True)
        #     await asyncio.sleep(1)
        #     st.experimental_rerun()  # <-- here

        # image = camera_input_live(show_controls=True)
        #
        # if image is not None:
        #
        #     st.image(image)
        st.subheader(f'Question: {st.session_state.question_index }')
        # for question in questions:
        #     # with CodeInterpreterSession() as session:
        #     #     response = session.generate_response(
        #     #         f'provide the code in python to solve the following question: {question}')
        #     #     st.session_state.correct_answers.append(response.content)
        if len(st.session_state.questions) <= st.session_state.question_index + 1:
            st.session_state.question_index = 1
        quiz_context = st.header(f"{questions[st.session_state.question_index].to_dict()['question']}")

        # num_questions = st.number_input('Enter the number of questions', min_value=1, max_value=100, value=1)
        # quiz_type = st.selectbox('Select the quiz type', ['Multiple-Choice', 'True-False', 'Open-Ended'])
        #st.markdown('Write a function to concatenate the results of two strings')
        # questions_answers = split_into_list_return_question_answers(st.session_state.questions,st.session_state.answers)
        # st.write(questions_answers)


        if st.button('Next Question', type='primary'):


            with st.sidebar:
                with st.expander("View Generated Solution"):
                    st.markdown(st.session_state.correct_answers[st.session_state.question_index])

            if st.session_state.question_index < len(questions):
                st.session_state.question_index += 1


    c2.subheader('IDE settings')


    with c1:
        st.subheader(f'Welcome {st.session_state.first_name} { st.session_state.last_name} - Enter your solution here ')
        st.markdown(st.session_state.questions)
        content = st_ace(
            placeholder=("Write your code here"),
            language= 'python',# c2.selectbox("Language mode", options=LANGUAGES, index=121),
            theme=c2.selectbox("Theme", options=THEMES, index=35),
            keybinding=c2.selectbox("Keybinding mode", options=KEYBINDINGS, index=3),
            font_size=c2.slider("Font size", 5, 24, 14),
            tab_size=c2.slider("Tab size", 1, 8, 4),
            # show_gutter=c2.checkbox("Show gutter", value=True),
            # show_print_margin=c2.checkbox("Show print margin", value=False),
            # wrap=c2.checkbox("Wrap enabled", value=False),
            auto_update= True, #c2.checkbox("Auto update", value=True),
            # readonly=c2.checkbox("Read-only", value=False),
            min_lines=25,
            key="ace",
        )

        if content:
            st.subheader("Submit When Ready")
            # st.code(content)
            if st.button('Submit Answer', type='primary'):
                # if len(st.session_state.questions) <= st.session_state.question_index + 1:
                #     st.success("End of test now scoring candidate")
                #     return
                progress_value = 0
                with st.spinner("Analyzing your submission"):
                    with CodeInterpreterSession() as session:
                        response = session.generate_response(f"compare the python code here:  {st.session_state.correct_answers[st.session_state.question_index]} with the python code here: {content}. Do both return the same results?")
                        with st.sidebar:
                            # st.markdown()

                            if 'yes' in response.content.lower():
                                st.success(response.content, icon="✅")
                                st.session_state.score += 1


                            else:
                                st.error(response.content, icon="🚨")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
   # asyncio.run(main())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
