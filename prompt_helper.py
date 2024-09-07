import streamlit as st
from prompt_creator import rag
from data_helper import parse_data

def wrap_to_json(answer_text): 
    print("answer_text", answer_text)
    lines = answer_text.replace("###", "").strip()
    return parse_data(lines)


def ask_LLM(user_query): 
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
            Situation English: {situation_english}\n
            Situation Korean: {situation_korean}\n
            Question English: {question_english}\n
            Answer English: {answer_english}\n
            Answer Korean: {answer_korean}\n"""

            print("formatted", formatted_output)     

            st.success("Query Completed!")
            st.markdown(formatted_output)
    else: 
        st.warning("Please select a category.")
