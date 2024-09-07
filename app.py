import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from prompt import build_prompt, recommend_prompt
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
    print(lines)
    return lines
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
                json_output = wrap_to_json(answer)
                print("json_output", json_output)
                data = json.loads(str(answer))
                # 필드 추출 및 f-string을 사용한 문자열 출력
                question_english = data["Question English"]
                situation_english = data["Situation English"]
                situation_korean = data["Situation Korean"]
                answer_english = data["Answer English"]
                answer_korean = data["Answer Korean"]

                # f-string을 사용하여 출력
                formatted_output = f"""
                Question English: {question_english}
                Situation English: {situation_english}
                Situation Korean: {situation_korean}
                Answer English: {answer_english}
                Answer Korean: {answer_korean}"""

                # 출력 
                print(formatted_output)     

                st.success("Query Completed!")
                st.markdown(answer)
        else:
            st.warning("Please enter a query.")



def suggest_categories(): 
    print("not it's going to suggest_categories") 
    st.subheader("Pick one category")
    category_options = ["choose a category you are interested in", "Gym", "Museum", "Restaurant", "Shopping", "Travel"]
    selected_category = st.selectbox("choose a category you are interested in", category_options)
    st.write("You selected:", selected_category)
    if selected_category: 
        with st.spinner("Searching..."):
            answer = rag(selected_category, "category")
            clean_answer = answer.replace("###", "").strip()
            st.success("Query Completed!")
            styled_answer = f'<p style="font-size:10px;">{answer}</p>'
            st.markdown(styled_answer, unsafe_allow_html=True)
    else: 
        st.warning("Please select a category.")


if selected_option:
    if selected_option == "pick a category you are interested in":
        print("it goes to the", selected_option)
        suggest_categories()
    else: 
        print("selected_option", selected_option)
        ask_LLM()

else: 
    st.warning("Please select an option.")
# Display the selected option


    

    