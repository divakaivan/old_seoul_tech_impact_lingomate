import streamlit as st
from elasticsearch import Elasticsearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json
from data_helper import search 



def validate_prompt(query, search_results):
    # add in future # Understanding cultural or contextual language use (e.g., polite phrases, idiomatic expressions)
    prompt_template = """
Your task is to validate if a query is relevant to language expressions. 
Language expressions include asking how to say something, asking for how to use language in various situations.
 
You can refer the examples in the context that can be used for an output. 
Use only the facts from the CONTEXT to answer the QUESTION. Do not add any additional information.
Do not add any additional information or change the structure. **Use only the facts from the provided CONTEXT.** Your response must be in markdown format, with all sentences separated by a newline.
Follow the below examples.font_size should be **12px**

If the query involves any of the following, it is **relevant**:
- Learning how to express something in a specific language (e.g., "How do I ask for direction in English?")
- Phrasing questions or statements for various contexts (e.g., "How do I introduce myself?")
- Understanding alternative ways to say something or synonym use

If the query is about:
- A technical issue
- Non-language-related topics (e.g., math, science, coding)
- General knowledge not related to language expressions
- Personal advice not related to language learning
- Casual chat like "I have no idea", "what are you up to?" 

Then it is **not relevant**.

Follow these instructions:
1. If the query is relevant to language expressions, return **True**.
2. If the query is irrelevant, return **False**.

Here is the query to validate:
QUERY: {query}
CONTEXT: {context}
""".strip() 
    context = ""
    for doc in search_results:
        context += f"Category: {doc['category']}\nSituation English: {doc['situation_en']}\nSituation Korean: {doc['situation_kr']}\nQuestion English: {doc['question_en']}\nAnswer English: {doc['answer_en']}\nAnswer Korean: {doc['answer_kr']}\n\n"
    prompt = prompt_template.format(query=query, context=context)
    return prompt

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

def validate_rag(query):
    print("validate query", query)
    search_results = search(query)
    prompt = validate_prompt(query, search_results)
    print("[rag prompt\n", prompt)
    print("-------[rag answer done]----------")
    prompt_template = ChatPromptTemplate.from_template(prompt)
    model = OllamaLLM(model="llama3.1", temperature = 0.1)
    answer = model.invoke(prompt)
    print("final answer", answer)
    return answer