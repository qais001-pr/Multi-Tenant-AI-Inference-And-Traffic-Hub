from config import create_connection
from fastapi import HTTPException #type:ignore
def add_user(email: str):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        if connection is None:
            return HTTPException(status_code=500,detail="Database Service Unavailable")
        cursor = connection.cursor()

        # Check existing user
        cursor.execute(
            "SELECT id, email FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return {
                "message": "User already exists",
                "data": {
                    "id": existing_user[0],
                    "email": existing_user[1]
                }
            }

        # Insert new user
        cursor.execute(
            "INSERT INTO users (email) VALUES (%s) RETURNING id, email",
            (email,)
        )

        user = cursor.fetchone()
        connection.commit()

        return {
            "message": "User created successfully",
            "data": {
                "id": user[0],
                "email": user[1]
            }
        }

    except Exception as error:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()