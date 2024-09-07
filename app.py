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

# Function to build a prompt for the LLM
def build_prompt(query, search_results):
    prompt_template = """
You are an English teacher who is helping students learn English expressions for different real-life situations. 
Based on the provided CONTEXT provide an appropriate response in English and Korean to the user's QUESTION.
Use only the facts from the CONTEXT to answer the QUESTION. Do not add any additional information.

Please **strictly follow the format below**. Do not add any additional information or change the structure. **Use only the facts from the provided CONTEXT.** Your response must be in markdown format, with all sentences separated by a newline.
Format should be followed. 
### Format:

Question Korean: [The provided question]\n
Question English: [Your Question in English]\n
Situation Korean: [The Situation in Korean]\n
Situation English: [The Situation in English]\n
Answer Korean: [Your Answer in Korean]\n
Answer English: [Your Answer in English]\n

### Example:

Question Korean: 가까운 지하철역 가는 법 알려주세요.\n
Question English: Where is the nearest subway station? \n
Situation Korean: 당신은 가장 가까운 지하철역으로 가는 길을 묻고 있습니다.\n
Situation English: Someone asks for directions to the nearest subway station.\n
Answer Korean: 두 블록 앞으로 가서 오른쪽으로 가세요.\n
Answer English: Go straight for two blocks, then turn right.\n

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    for doc in search_results:
        context += f"Category: {doc['category']}\nSituation English: {doc['situation_en']}\nSituation Korean: {doc['situation_kr']}\nQuestion English: {doc['question_en']}\nAnswer English: {doc['answer_en']}\nAnswer Korean: {doc['answer_kr']}\n\n"

    prompt = prompt_template.format(question=query, context=context)
    return prompt

def recommend_prompt(category, search_results):
    print("here's recommend_prompt")
    prompt_template = """
 
You are an English teacher helping students learn English expressions for real-life situations. 
You are tasked with providing **only one set** of expressions related to the provided category.

Please **strictly follow the format below**. Do not add any additional information or change the structure. **Use only the facts from the provided CONTEXT.** Your response must be in markdown format, with all sentences separated by a newline.
Format should be followed and font_size should be **12px**

### Format:

Question Korean: [The provided question]\n
Question English: [Your Question in English]\n
Situation Korean: [The Situation in Korean]\n
Situation English: [The Situation in English]\n
Answer Korean: [Your Answer in Korean]\n
Answer English: [Your Answer in English]\n

### Example:

Question Korean: 가까운 지하철역 가는 법 알려주세요.\n
Question English: Where is the nearest subway station? \n
Situation Korean: 당신은 가장 가까운 지하철역으로 가는 길을 묻고 있습니다.\n
Situation English: Someone asks for directions to the nearest subway station.\n
Answer Korean: 두 블록 앞으로 가서 오른쪽으로 가세요.\n
Answer English: Go straight for two blocks, then turn right.\n

### Instructions:

- Ensure that the **category** and **context** are taken into account.
- Provide **only one set** of expressions related to the provided category.
- **Follow the exact format**. Do not change the order or structure.
- **Do not generate extra information** beyond what is given in the context.

CATEGORY: {category}

CONTEXT: {context}
""".strip()
    context = ""
    for doc in search_results:
        context += f"Category: {doc['category']}\nSituation English: {doc['situation_en']}\nSituation Korean: {doc['situation_kr']}\nQuestion English: {doc['question_en']}\nAnswer English: {doc['answer_en']}\nAnswer Korean: {doc['answer_kr']}\n\n"

    prompt = prompt_template.format(category=category, context=context)
    print("-------" )
    print("prompt", prompt)
    print("-------" )
    return prompt

# Function to run RAG pipeline
def rag(query, type):
    print("query", query)
    search_results = elastic_search(query)
    if type == "question":
        prompt = build_prompt(query, search_results)
    if type == "category": 
        prompt = recommend_prompt(query, search_results)
    print("[rag answer - prompt", prompt)
    print("[rag answer done]----------")
    # prompt_template = ChatPromptTemplate.from_template(prompt)
    model = OllamaLLM(model="llama3.1")
    answer = model.invoke(prompt)
    return answer


entry_options = ["please select an option", "pick a category you are interested in", "Any question in your mind?"]
selected_option = st.selectbox("please select an option", entry_options)


def ask_LLM(): 
    st.subheader("Ask LingoMate")
    user_query = st.text_input("Enter your question:")
    if st.button("Search"):
        if user_query:
            with st.spinner("Searching..."):
                answer = rag(user_query, "question")
                st.success("Query Completed!")
                st.write("Answer:", answer)
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


    

    