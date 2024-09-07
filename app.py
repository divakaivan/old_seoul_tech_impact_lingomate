
import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json

# Initialize Elasticsearch
es_client = Elasticsearch('http://localhost:9200')

# Define the Elasticsearch index and its settings
index_name = "learning-english"

# Streamlit title and introduction
st.title("Language Learning Query System")
st.write("Enter your query below, and the system will search for relevant results in English and Korean, then generate a response.")

# Function to search Elasticsearch
def elastic_search(query):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ['category', 'situation_en^3', 'situation_kr^3', 'question_en', 'answer_en', 'question_kr', 'answer_kr'],
                        "type": "best_fields"
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)

    result_docs = []
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs

# Function to build a prompt for the LLM
def build_prompt(query, search_results):
    prompt_template = """
You are an English teacher who is helping students learn English expressions for different real-life situations. 
Based on the provided CONTEXT provide an appropriate response in English and Korean to the user's QUESTION.
Use only the facts from the CONTEXT to answer the QUESTION. Do not add any additional information.

return the situation, question, and answer in English and Korean. all sentences should be separated by a newline.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    for doc in search_results:
        context += f"Category: {doc['category']}\nSituation English: {doc['situation_en']}\nSituation Korean: {doc['situation_kr']}\nQuestion English: {doc['question_en']}\nAnswer English: {doc['answer_en']}\nAnswer Korean: {doc['answer_kr']}\n\n"

    prompt = prompt_template.format(question=query, context=context)
    return prompt

# Function to run RAG pipeline
def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    prompt_template = ChatPromptTemplate.from_template(prompt)
    model = OllamaLLM(model="llama3.1")
    chain = prompt_template | model
    answer = chain.invoke({"question": query})
    return answer

# Streamlit user input
user_query = st.text_input("Enter your question:")
if st.button("Search"):
    if user_query:
        with st.spinner("Searching..."):
            answer = rag(user_query)
            st.success("Query Completed!")
            st.write("Answer:", answer)
    else:
        st.warning("Please enter a query.")

