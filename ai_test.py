import os

import openai
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import  load_dotenv, find_dotenv
from langchain.schema import BaseOutputParser
import  re

import  streamlit as st

from utils import split_into_list_return_question_answers

from camera_input_live import camera_input_live
from utils import  *

class QuestionsAnswersParser(BaseOutputParser):
    def parse(self, text: str):
        # step1, separate the questions and answers sections
        questions_part, answers_part = text.split("Answers:", 1)

        # step 2 parse the questions
        questions = re.findall(r"Questions: (.+)", questions_part)

        # step 3: Parse Answers
        answers_text = answers_part.strip()
        answers = re.findall(r"[a-d]\) .+", answers_text)

        # step 4 combine quesions and answers
        combined_data = dict(zip(questions, answers))
        return combined_data


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
                                          messages=[{'role': 'system', 'content': 'You are a helpful researcher and programming assistant'},
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

def main():
    load_dotenv()
    initialize_state()
    st.set_page_config(page_title="neuradev.ai", layout="wide")
    st.header('neuradev.ai Candidate Test Platform')
    with st.sidebar:
        # controls = st.checkbox("Show controls")
        image = camera_input_live(show_controls=False)

        if image is not None:
            st.image(image)
        st.subheader('This builds a quiz based off a given context')
        quiz_context = st.text_area('Provide a topic or area for your quiz')
        num_questions = st.number_input('Enter the number of questions', min_value=1, max_value=100, value=1)
        quiz_type = st.selectbox('Select the quiz type', ['Multiple-Choice', 'True-False', 'Open-Ended'])


        if st.button('Start Coding Test'):
            with st.spinner('Generating interview questions'):
                quiz_response = create_prompt_template_returns_chain(num_questions=num_questions, quiz_type=quiz_type, quiz_context=quiz_context)
                questions, answers = split_questions_answers(quiz_response)
                st.session_state.answers = answers
                st.session_state.questions = questions
                st.session_state.question_type = quiz_type

        if st.button("Display Correct Answers"):
            # st.markdown(st.session_state.questions)
            # st.write("----")
            st.code(st.session_state.answers)
    col1, col2 = st.columns(2)
    with col1:
        questions_answers = split_into_list_return_question_answers(st.session_state.questions, st.session_state.answers )
        # st.write(questions_answers)
        st.markdown(st.session_state.questions)
    with col2:
        st.markdown('Enter or select your answers here')
        if st.session_state.question_type == 'Multiple-Choice':
            for question in range(num_questions):
                st.selectbox(f'Select your answer for question {question + 1}', ['a', 'b', 'c', 'd'])

        if st.session_state.question_type == 'True-False':
            for question in range(num_questions):
                st.selectbox(f'Select your answer for question {question + 1}', ['True', 'False'])

        if st.session_state.question_type == 'Open-Ended':
            for question in range(num_questions):
                st.text_area(f'Enter your answer here for question {question + 1}')

        if st.button('Submit Answers'):
            pass


if __name__ == "__main__":
    main()


