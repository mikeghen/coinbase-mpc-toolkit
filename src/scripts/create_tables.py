import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "chatbot"),
    user=os.getenv("DB_USER", "postgress"),
    password=os.getenv("DB_PASSWORD", "postgress"),
    host=os.getenv("DB_HOST", "db"),
    port=os.getenv("DB_PORT", "5432")
)
conn.autocommit = True

cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.close()
conn.close()
