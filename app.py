import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from prompt import build_prompt, recommend_prompt, parse_data
from data_helper import search 
import json

# Streamlit title and introduction
st.title("Language Learning Query System")
st.write("Enter your query below, and the system will search for relevant results in English and Korean, then generate a response.")


# Function to run RAG pipeline
def rag(query, type):
    print("query", query)
    search_results = search(query)
    if type == "question":
        prompt = build_prompt(query, search_results)
    if type == "category": 
        prompt = recommend_prompt(query, search_results)
    print("[rag answer - prompt", prompt)
    print("[rag answer done]----------")
    # prompt_template = ChatPromptTemplate.from_template(prompt)
    model = OllamaLLM(model="llama3.1")
    answer = model.invoke(prompt)
    print("final_answer", answer)
    return answer


entry_options = ["please select an option", "pick a category you are interested in", "Any question in your mind?"]
selected_option = st.selectbox("please select an option", entry_options)

def wrap_to_json(answer_text): 
    print("answer_text", answer_text)
    lines = answer_text.replace("###", "").strip()
    parsed_data = parse_data(lines)
    # for key, value in parsed_data.items(): 
    #     print(f"{key.capitalize()}: {value}")

    # print("lines", lines)
    return parsed_data
    # json_data = {}

    # for line in lines: 
    #     key, value = line.split(":", 1)
    #     json_data[key.strip()] = value.strip()
    # return json.dumps(json_data, indent=4)

    #convert the dictionary to json_String 
def ask_LLM(): 
    st.subheader("Ask LingoMate")
    user_query = st.text_input("Enter your question:")
    if st.button("Search"):
        if user_query:
            with st.spinner("Searching..."):
                answer = rag(user_query, "question")
                print("ollama answer: ", answer)    
                parsed_data = wrap_to_json(answer)
                print("parsed_data", parsed_data)

                question_english = parsed_data["Question English"]
                situation_english = parsed_data["Situation English"]
                situation_korean = parsed_data["Situation Korean"]
                answer_english = parsed_data["Answer English"]
                answer_korean = parsed_data["Answer Korean"]

                formatted_output = f"""
                Question English: {question_english}\n
                Situation English: {situation_english}\n
                Situation Korean: {situation_korean}\n
                Answer English: {answer_english}\n
                Answer Korean: {answer_korean}\n"""

                print("formatted", formatted_output)     

                st.success("Query Completed!")
                st.markdown(formatted_output)
        else:
            st.warning("Please enter a query.")



def suggest_categories(): 
    print("Will suggest_categories") 
    st.subheader("Pick one category")
    category_options = ["choose a category you are interested in", "Gym", "Museum", "Restaurant", "Shopping", "Travel"]
    selected_category = st.selectbox("choose a category you are interested in", category_options)
    if selected_category!= "choose a category you are interested in":
        st.write("You selected:", selected_category) 
        with st.spinner("Searching..."):
            answer = rag(selected_category, "category").replace("###", "").strip()
            parsed_data = wrap_to_json(answer)
            print("parsed_data", parsed_data)

            question_english = parsed_data["Question English"]
            situation_english = parsed_data["Situation English"]
            situation_korean = parsed_data["Situation Korean"]
            answer_english = parsed_data["Answer English"]
            answer_korean = parsed_data["Answer Korean"]

            formatted_output = f"""
            Question English: {question_english}\n
            Situation English: {situation_english}\n
            Situation Korean: {situation_korean}\n
            Answer English: {answer_english}\n
            Answer Korean: {answer_korean}\n"""

            print("formatted", formatted_output)     

            st.success("Query Completed!")
            st.markdown(formatted_output)
    else: 
        st.warning("Please select a category.")


if selected_option:
    if selected_option == "pick a category you are interested in":
        suggest_categories()
    else: 
        print("selected_option", selected_option)
        ask_LLM()

else: 
    st.subheader("Please select an option.")
# Display the selected option


    

    