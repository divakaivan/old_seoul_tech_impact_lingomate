import streamlit as st
import psycopg2
import ast

DB_PARAMS = {
    'dbname': 'database',
    'user': 'username',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}

def fetch_conversations():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        query = "SELECT id, timestamp FROM conversations ORDER BY timestamp DESC"
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        conn.close()
        
        formatted_data = [(row[0], row[1].strftime('%Y-%m-%d %H:%M:%S')) for row in rows]
        return formatted_data
    except Exception as e:
        st.error(f"Error fetching conversations: {e}")
        return []

def fetch_conversation_details(conversation_id):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        query = """
            SELECT 
                c.question,
                c.search_results,
                c.answer,
                c.token_usage,
                c.response_time
            FROM conversations c
            WHERE c.id = %s
        """
        with conn.cursor() as cur:
            cur.execute(query, (conversation_id,))
            result = cur.fetchone()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error fetching conversation details: {e}")
        return None

st.title('LangMate RAG Tracing')

conversations = fetch_conversations()
if conversations:

    ids, timestamps = zip(*conversations)
    selected_dropdown_id = st.selectbox('Select a Conversation ID', ids)
    selected_search_id = st.text_input('Or Enter a Conversation ID')
    
    if selected_search_id and selected_search_id in ids:
        selected_id = selected_search_id
    else:
        selected_id = selected_dropdown_id
    
    if selected_id:
        details = fetch_conversation_details(selected_id)
        if details:
            question, search_results, answer, token_usage, response_time = details
            try:
                search_results = ast.literal_eval(search_results)
            except (ValueError, SyntaxError) as e:
                st.error(f"Error parsing search results: {e}")
                search_results = "Unable to parse search results."

            st.write(f"#### Details for Conversation ID: {selected_id}")
            st.write(f"#### User Query:\n{question}")
            st.write(f"#### Retrieved Context:\n")
            if isinstance(search_results, (list, dict)):
                st.json(search_results)  # Display as JSON if it's a list or dictionary
            else:
                st.write(search_results)
            st.write(f"#### Answer:\n{answer}")
            st.write(f"#### Token Usage:\n{token_usage}")
            st.write(f"#### Response Time:\n{response_time} seconds")
        else:
            st.write('No details available for the selected conversation ID')
else:
    st.write('No conversation data available')
