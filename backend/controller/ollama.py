from config import create_connection
from fastapi import HTTPException #type: ignore
import requests
import json
import os
from dotenv import load_dotenv #type: ignore
load_dotenv()


def ollama_receive_message(message: str, userid: int):
    llama_url = os.getenv('OLLAMA_LLAMA_URL')
    url = llama_url.rstrip("/") + "/api/chat"

    payload = {
        "model": "llama3.2:latest",
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Ollama server error"
            )

        response_data = response.json()

        saved = store_response_in_postgres_db(
            user_id=userid,
            prompt=message,
            responsedata=response_data
        )

        if not saved:
            raise HTTPException(
                status_code=500,
                detail="Failed to store response in DB"
            )

        return {
            "status_code": 200,
            "detail": response_data
        }

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama server is unreachable"
        )

def store_response_in_postgres_db(user_id: int, prompt: str, responsedata: dict):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        if connection is None:
            return False

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO ai_responses (user_id, prompt, response_data)
            VALUES (%s, %s, %s)
            """,
            (user_id, prompt, json.dumps(responsedata))
        )

        connection.commit()
        return True

    except Exception as error:
        print("DB Error:", error)
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_history(user_id: int):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="DB unreachable")

        cursor = connection.cursor()

        cursor.execute(
            "SELECT response_data FROM ai_responses WHERE user_id=%s",
            (user_id,)
        )

        rows = cursor.fetchall()

        return {
            "status_code": 200,
            "result": rows
        }

    except Exception as error:
        print("Error:", error)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()