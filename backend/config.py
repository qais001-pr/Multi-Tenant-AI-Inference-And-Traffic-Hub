import os
from dotenv import load_dotenv # type: ignore
load_dotenv()
import psycopg2 #type: ignore
from fastapi import HTTPException #type: ignore
import requests
def create_connection():
    connection = psycopg2.connect(
        host=os.getenv('POSTGRESS_HOST'),
        database=os.getenv('POSTGRESS_DATABASE'),
        user=os.getenv('PROSTGRESS_USER'),
        password=os.getenv('POSTGRESS_PASSWORD'),
        port=os.getenv('POSTGRESS_PORT')
        )
    if connection is None:
        return HTTPException(status_code=500,detail="Database Service Unavailable")
    return connection
def create_tables():
    try:
        connection = create_connection()
        if connection is None:
            return HTTPException(status_code=500,detail="Database Service Unavailable")
        else:
            print('Database Connected Successfully')
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE
        );
    """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_responses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            prompt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response_data TEXT NOT NULL
        );
    """)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if connection:
            connection.close()
def connect_with_ollama():
    try:
        response = requests.get(
            os.getenv("OLLAMA_LLAMA_URL"),
            timeout=5
        )

        response.raise_for_status()

        print("Ollama is Running")
        print(response.json())

        return True

    except Exception as e:
        print(f"Unable to connect to Ollama: {e}")
        return False