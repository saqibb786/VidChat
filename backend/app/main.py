import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .utils.audio_processor import process_input
from .core.transcriber import transcribe_all
from .core.summarizer import summarize, generate_title
from .core.extractor import extract_action_items, extract_key_decisions, extract_questions
from .core.rag_engine import build_rag_chain, ask_question

app = FastAPI(title="VidChat API", version="1.0.0")

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
        chunks = process_input(req.source.strip())
        transcript = transcribe_all(chunks, req.language)
        title = generate_title(transcript)
        summary_text = summarize(transcript)
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        rag_chain = build_rag_chain(transcript)
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = rag_chain
        
        return {
            "session_id": session_id,
            "title": title,
            "transcript": transcript,
            "summary": summary_text,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions
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
