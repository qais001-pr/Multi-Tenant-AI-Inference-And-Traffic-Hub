from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import uvicorn # type: ignore
from config import create_tables,connect_with_ollama
from dotenv import load_dotenv # type: ignore
from routes.emails_routes import emails_router
from routes.ollama_routes import ollama_router
from config import create_connection

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

@app.get('/healthz')
def liveness():
    return {"status": "alive"}

@app.get('/ready')
def readiness():
    try:
        conn = create_connection()
        if conn is None:
            return {"status": "not ready"}, 500
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return {"status": "not ready"}, 500


if __name__ == "__main__":
    uvicorn.run(app)