import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json
from data_helper import search 

def parse_data(text):
    # Split the text by newlines to get individual lines
    lines = text.strip().split("\n")    
    # Initialize variables to store values
    parsed_data = {
        "Category": "",
        "Situation English": "",
        "Situation Korean": "",
        "Question English": "",
        "Answer Korean": "",
        "Answer English": "",
    }

    # Parse each line
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)  
            key = key.strip().strip('"')
            value = value.strip().strip('"')
            print("key, value", key, value)
            print(f"Parsed key: {repr(key)}")  # Debugging output

            
            # Assign to the appropriate variable based on the key
            if key in parsed_data: 
                parsed_data[key] = value                
    return parsed_data

##Please **strictly follow the format below**. 

# Function to build a prompt for the LLM
def build_prompt(query, search_results):
    prompt_template = """
You are an English teacher who is helping students learn English expressions. 
Use only the facts from the CONTEXT to answer the QUESTION. Do not add any additional information.

Do not add any additional information or change the structure. **Use only the facts from the provided CONTEXT.** Your response must be in markdown format, with all sentences separated by a newline.
Follow the below examples.font_size should be **12px**

pleaes refer to the example below and write it in JSON format. 
Example 1
```
  "Question English":  "Where is the nearest subway station?",
  "Situation English": "Someone asks for directions to the nearest subway station.",
  "Situation Korean": 당신은 가장 가까운 지하철역으로 가는 길을 묻고 있습니다.",
  "Answer English": "Go straight for two blocks, then turn right.",
  "Answer Korean": "두 블록 앞으로 가서 오른쪽으로 가세요."
```
Example 2
```
"Question English":  "Where is the nearest subway station?",
  "Situation English": "You are at a restaurant and want to know if they offer outdoor seating.",
  "Situation Korean": "당신은 식당에 있으며 야외 좌석이 있는지 알고 싶습니다.",
  "Answer English": "Yes, we have a patio for outdoor dining.",
  "Answer Korean": "야외에서 식사할 수 있는 테라스가 있습니다."
```

### Instructions:

- Ensure that the **category** and **context** are taken into account.
- Provide **only one set** of expressions related to the provided category.
- **Follow the exact format**. Do not change the order or structure.
- **Do not generate extra information** beyond what is given in the context.

QUESTION: {question}

CONTEXT: {context}

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
Follow the below examples.font_size should be **12px**


### 
Example 1
```
  "Question English":  "Where is the nearest subway station?",
  "Situation English": "Someone asks for directions to the nearest subway station.",
  "Situation Korean": 당신은 가장 가까운 지하철역으로 가는 길을 묻고 있습니다.",
  "Answer English": "Go straight for two blocks, then turn right.",
  "Answer Korean": "두 블록 앞으로 가서 오른쪽으로 가세요."
```
Example 2
```
"Question English":  "Where is the nearest subway station?",
  "Situation English": "You are at a restaurant and want to know if they offer outdoor seating.",
  "Situation Korean": "당신은 식당에 있으며 야외 좌석이 있는지 알고 싶습니다.",
  "Answer English": "Yes, we have a patio for outdoor dining.",
  "Answer Korean": "야외에서 식사할 수 있는 테라스가 있습니다."
```
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
    # print("-------" )
    # print("prompt", prompt)
    # print("-------" )
    return prompt

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
    prompt_template = ChatPromptTemplate.from_template(prompt)
    model = OllamaLLM(model="llama3.1", temperature = 0.1)
    answer = model.invoke(prompt)
    print("final answer", answer)
    return answer