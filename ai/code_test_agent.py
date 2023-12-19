import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser

from codeinterpreterapi import CodeInterpreterSession

from dotenv import  load_dotenv, find_dotenv


def assess_code(problem, code, explanation):
    with st.spinner("Analyzing your submission"):
        with CodeInterpreterSession(llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)) as session:
            response = session.generate_response(
                f"""- Problem
{problem}

- Code
{code}

- Explanation
{explanation}

- Question
1. Does the above Python code solve the given problem correctly? Just answer with Yes or No. Answer No when you cannot determine.
2. How would you rate the code quality from 1 to 5? Just answer with one-decimal number between 1 and 5. Answer 1 when you cannot determine.
3. How would you rate the explanation about the code from 1 to 5? Just answer with one-decimal number between 1 and 5. Answer 1 when you cannot determine.
4. How would you rate the solution(code and explanation) overall? Just answer with one-decimal number between 1 and 5. Answer 1 when you cannot determine.
5. What's the reason behind your answer? Just answer with 2-7 sentences""")
            
            i1, i2, i3, i4, i5 = 0, response.content.index("\n2. "), response.content.index("\n3. "), response.content.index("\n4. "), response.content.index("\n5. ")
            passed = True if response.content[i1+3:i2].lower() == 'yes' else False
            code_quality = float(response.content[i2+3:i3])
            explanation_rating = float(response.content[i3+3:i4])
            overall_rating = float(response.content[i4+3:i5])
            reason = response.content[i5+3:]
            
            return passed, code_quality, explanation_rating, overall_rating, reason
