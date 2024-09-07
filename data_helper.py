import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json


# Initialize Elasticsearch
es_client = Elasticsearch('http://localhost:9200')

# Define the Elasticsearch index and its settings
index_name = "learning-english"

# Function to search Elasticsearch
def search(query):
    search_query = {
        "size": 1,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ['category^8', 'situation_en', 'situation_kr', 'question_en', 'answer_en', 'question_kr', 'answer_kr'],
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