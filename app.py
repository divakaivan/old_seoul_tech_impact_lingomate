import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from prompt_creator import build_prompt, recommend_prompt, rag, validate_rag
from data_helper import search, parse_data
from prompt_helper import ask_LLM, suggest_categories
import json

# Streamlit title and introduction
st.title("Language Learning Query System")
st.write("Enter your query below, and the system will search for relevant results in English and Korean, then generate a response.")

def validate_query(query): 
    if query in entry_options: 
        return None 
    result = validate_rag(query).replace("**", "")
    print("validate_query result", result)
    return result

entry_options = ["please select an option", "pick a category you are interested in", "Any question in your mind?"]
selected_option = st.selectbox("please select an option", entry_options)
print("selected_option", selected_option)


if selected_option!= "please select an option":
    if selected_option == "pick a category you are interested in":
        suggest_categories()
    else: 
        user_query = st.text_input("Any question in your mind?")
        print("selected_question", selected_option)
        if st.button("Search"):
            if user_query:
                result = validate_query(user_query).strip()
                print("result", result)
                if(result == "False"): 
                    print("result is", result)
                    st.warning("Sorry! I'm here to help with language expressions.\nCould you ask me something related to that?")
                else: 
                    ask_LLM(user_query)


else: 
    st.subheader("Please select an option.")
# Display the selected option


    

    