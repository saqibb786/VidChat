import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .core.ingestion_service import IngestionManager
from .core.rag_engine import ask_question
from .utils.audio_processor import BASE_DIR, DOWNLOAD_DIR

app = FastAPI(title="VidChat API", version="1.2.0")

# Enable CORS for React frontend (Vite port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving extracted images & data
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=DATA_DIR), name="static")

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

@app.post("/api/upload")
async def upload_media_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, file.filename)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        return {"filepath": file_path, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
