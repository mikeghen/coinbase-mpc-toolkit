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
    CREATE TABLE IF NOT EXISTS user_wallet (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL UNIQUE,
        wallet_id VARCHAR(255) NOT NULL,
        wallet_address VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')
cursor.close()
conn.close()
