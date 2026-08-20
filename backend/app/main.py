import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .core.ingestion_service import IngestionManager
from .core.rag_engine import ask_question

app = FastAPI(title="VidChat API", version="1.1.0")

# Enable CORS for React frontend (Vite port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active session RAG chains
sessions = {}

class AnalyzeRequest(BaseModel):
    source: str
    language: str = "english"
    engine: str = "local"  # "local" or "adversal"

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "VidChat API"}

@app.post("/api/analyze")
def analyze_video(req: AnalyzeRequest):
    if not req.source.strip():
        raise HTTPException(status_code=400, detail="Source URL or file path is required")
    
    try:
        result = IngestionManager.process(req.source.strip(), req.language, req.engine)
        sessions[result["session_id"]] = result["rag_chain"]
        
        return {
            "session_id": result["session_id"],
            "engine": result["engine"],
            "title": result["title"],
            "transcript": result["transcript"],
            "summary": result["summary"],
            "action_items": result["action_items"],
            "key_decisions": result["key_decisions"],
            "open_questions": result["open_questions"],
            "images": result.get("images", []),
            "fallback_warning": result.get("fallback_warning")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_with_meeting(req: ChatRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired. Please re-analyze media.")
    
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        rag_chain = sessions[req.session_id]
        answer = ask_question(rag_chain, req.question.strip())
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
