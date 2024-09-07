import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

from zoneinfo import ZoneInfo

tz = ZoneInfo("Asia/Seoul")

def get_db_connection():
    """Get a connection to the database."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "database"),
        user=os.getenv("POSTGRES_USER", "username"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        options='-c client_encoding=UTF8'
    )

def init_db():
    """Initialize the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    username TEXT,
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    token_usage INTEGER NOT NULL,
                    search_results TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    username TEXT NOT NULL,
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()

def save_conversation(conversation_id, question, answer_data, username, timestamp=None):
    """Save a conversation to the database."""
    if timestamp is None:
        timestamp = datetime.now()

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (username, id, question, answer, response_time, token_usage, search_results, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) 
                DO UPDATE SET
                    username = EXCLUDED.username,
                    question = EXCLUDED.question,
                    answer = EXCLUDED.answer,
                    response_time = EXCLUDED.response_time,
                    token_usage = EXCLUDED.token_usage,
                    search_results = EXCLUDED.search_results,
                    timestamp = EXCLUDED.timestamp
                """,
                (
                    username,
                    conversation_id,
                    question,
                    answer_data["answer"],
                    answer_data["response_time"],
                    answer_data["token_usage"],
                    answer_data["search_results"],
                    timestamp,
                ),
            )
        conn.commit()
    finally:
        conn.close()

def save_feedback(conversation_id, username, feedback, timestamp=None):
    """Save feedback for a given conversation."""
    if timestamp is None:
        timestamp = datetime.now(tz)
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (conversation_id, username, feedback, timestamp) VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))",
                (username, conversation_id, feedback, timestamp),
            )
        conn.commit()
    finally:
        conn.close()

def load_conversations(username):
    """Load all conversations for a given username."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM conversations WHERE username = %s ORDER BY timestamp DESC", (username,))
            return cur.fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    get_db_connection()
    init_db()
    print("Database initialized.")
