import os

import openai
from langchain.agents import AgentType, initialize_agent
from langchain.embeddings.openai import  OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import pinecone
from pypdf import PdfReader
from langchain.llms.openai import  OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain import HuggingFaceHub
from langchain.schema import Document
from langchain import SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool
from langchain.tools import Tool
from langchain_experimental.agents.agent_toolkits import create_python_agent
from codeinterpreterapi import CodeInterpreterSession, settings

# Function to get response from Gorilla Server
def get_gorilla_response(prompt, model):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("An error occurred:", e)

def ask_serp_agent(question):
    # initialize the search chain
    search = SerpAPIWrapper(serpapi_api_key=os.environ.get('SERP_API_KEY'))

    python_agent_executor = create_python_agent(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        tool=PythonREPLTool(),
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # create a search tool
    tools = [
        Tool(
            name="Intermediate Answer",
            func=search.run,
            description='useful for when you need to ask with search '
        ),
        Tool(name="PythonAgent", func=python_agent_executor.run,
             description="""useful when you need to transform natural language and write from it python and execute
                 the python code, returning the results of the code execution,
                 """)
    ]

    llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")

    # initialize the search enabled agent
    self_ask_with_search = initialize_agent(
        tools,
        llm,
        agent_type="self-ask-with-search",
        verbose=True
    )
    answer = self_ask_with_search(
    question
    )
    print(f"Answer is {answer}")
    return answer

#EXTRACT INFO FROM PDF FILE
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

#ITERATE OVER FILES THAT USER UPLOADED
def create_docs(user_pdf_list, unique_id):
    docs = []
    for index, filename in enumerate(user_pdf_list):
        chunks = get_pdf_text(filename)

        #add items to our list including data and meta data
        docs.append(Document(page_content=chunks,
                             metadata={"name": filename.name,"id": index,
                             "type": filename.type, "size": filename.size, "unique_id":unique_id}))

    return docs

#CREATE embeddings instance
def create_embeddings_load_data():
    embeddings = OpenAIEmbeddings()
    # embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings

def push_to_pinecone(pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings, docs):
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    print("done...2")
    Pinecone.from_documents(documents=docs, embedding=embeddings, index_name=pinecone_index_name)

def pull_from_pinecone(pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings):
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    print("done...2")
    index_name = pinecone_index_name
    index = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
    return index

#get us relevant documents from vector store based on user input
def similar_docs(query, k, pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings, unique_id ):
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    index_name = pinecone_index_name
    index = pull_from_pinecone(pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings)

    # similar_docs =  index.similarity_search(query=query, k=int(k), filter={"unique_id": unique_id})
    similar_docs = index.similarity_search(query=query, k=int(k))
    print(similar_docs)
    return similar_docs

def get_summary(current_doc):
    llm = OpenAI(temperature=0, model_name='gpt-3.5-turbo-16k')
    llm = HuggingFaceHub(repo_id='pszemraj/led-large-book-summary', model_kwargs={"temperature": 1e-10})
    chain = load_summarize_chain(llm=llm, chain_type="map_reduce")
    summary = chain.run([current_doc])
    return summary

def split_into_list_return_question_answers(questions, answers):
    q = questions.split('\n')
    a = answers.split('\n')
    del q[0:4]
    del a[0]

    print(f'Length of Question list is {len(q)}')
    print(f'Length of Answer list is {len(a)}')
    main_list = []
    for index, item in enumerate(a):
        print(index, item)
        main_list.append({'question': q[index] , 'right_answer': a[index]})
    return main_list

def return_code(question):
    with CodeInterpreterSession() as session:
        response = session.generate_response(question)
        response.show()