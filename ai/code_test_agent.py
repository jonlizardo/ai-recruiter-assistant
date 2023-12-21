import streamlit as st

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

from codeinterpreterapi import CodeInterpreterSession

from dotenv import  load_dotenv
import os


load_dotenv()

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

def assess_code_with_gpt4(problem, code, explanation):
    class CodeTestResult(BaseModel):
        passed: bool = Field(description="answer if the candidate's solution code solves the problem or not.")
        code_quality: float = Field(description="rate the candidate's solution code quality from 0 to 5, should be 1-decimal number.")
        explanation_rating: float = Field(description="rate the candidate's explanation about the Solution code from 0 to 5 based on how detailed and concise it is.")
        overall_rating: float = Field(description="rate the overall solution for the problem, focus more on code itself, rather than explanation. should be 1-decimal number")
        reason: str = Field(description="answer the reason behind your answers, should be 2-7 sentences")
    
    parser = PydanticOutputParser(pydantic_object=CodeTestResult)
    
    chat_model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model='gpt-4', temperature=0)

    template = """You are a senior software developer. Assess the code given the problem.
{format_instructions}

Problem:
{problem}

Candidate's Solution Code:
{code}

Candidate's Explanation about the Solution Code:
{explanation}
"""
    prompt = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template(template)
        ],
        input_variables=["problem", "code", "explanation"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    _input = prompt.format_prompt(problem=problem, code=code, explanation=explanation if explanation else "No explanation is provided")

    output = chat_model(_input.to_messages())
    
    return parser.parse(output.content)
