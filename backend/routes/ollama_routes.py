from fastapi import APIRouter,HTTPException #type: ignore
from controller.ollama import ollama_receive_message,get_history
ollama_router = APIRouter()
@ollama_router.get('/chat')
def get_message_from_user(mess:str,user_id:int):
    return ollama_receive_message(message=mess,userid=user_id)

@ollama_router.get('/get-history')
def get_message_from_user(user_id:int):
    return get_history(user_id=user_id)