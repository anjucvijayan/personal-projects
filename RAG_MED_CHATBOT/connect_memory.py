import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()


# set llm (mistral with hugging face)
HF_TOKEN = os.getenv("HF_TOKEN")
#print(HF_TOKEN)
HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"

def load_llm(HUGGINGFACE_REPO_ID):
    llm = HuggingFaceEndpoint(
        repo_id =HUGGINGFACE_REPO_ID,
        temperature = 0.5,
        model_kwargs = {"token":HF_TOKEN,
        'max_length':"512"}
    )
    return llm


# connect llm with FAISS
custom_prompt_template = """
use the pieces of information provides in the context to answer user's question.
if you don't know the answer, just say that you don't know,don't try to make up an answer. Don't provide anything out of the given context.

context :{context}
Question : {question}
start the answer directly. No small talk please.
"""
def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template = custom_prompt_template,input_variables ={"context","Question"} )
    return prompt

DB_FAISS_PATH = "vectorstore/db_faiss"
embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L12-v2")
db = FAISS.load_local(DB_FAISS_PATH,embedding_model,allow_dangerous_deserialization = True)

# create chain
qa_chain = RetrievalQA.from_chain_type(
    llm = load_llm(HUGGINGFACE_REPO_ID),
    chain_type = "stuff",
    retriever = db.as_retriever(search_kwargs = {'k':3}),
    return_source_documents = True,
    chain_type_kwargs = {'prompt':set_custom_prompt(custom_prompt_template)}
)

#invoke with single query

#user_query = input("Write a query here...")
#response = qa_chain.invoke({'query':user_query})
#print(response['result'].strip())
#pages = [doc.metadata['page'] for doc in response['source_documents']]
#print(pages)

def response(user_query):
    response = qa_chain.invoke({'query':user_query})
    pages = [doc.metadata['page'] for doc in response['source_documents']]
    result = response['result'].strip() + str(pages)
    
    print(result)
    return result

#response(user_query)
