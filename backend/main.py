from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import uvicorn # type: ignore
import requests # type: ignore 
import json
import os
from config import create_tables,connect_with_ollama
from dotenv import load_dotenv # type: ignore
from routes.emails_routes import emails_router
from routes.ollama_routes import ollama_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()
connect_with_ollama()
create_tables()

app.include_router(emails_router, prefix="/api")
app.include_router(ollama_router, prefix="/api")

@app.get('/')
def read_root_and_connect_with_postgress():
    
    return {"status": "healthy", "message": "Server is Running"}


if __name__ == "__main__":
    uvicorn.run(app)