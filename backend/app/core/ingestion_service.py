import os
import uuid
import logging
from ..utils.audio_processor import process_input
from .transcriber import transcribe_all
from .summarizer import summarize, generate_title
from .extractor import extract_action_items, extract_key_decisions, extract_questions
from .rag_engine import build_rag_chain
from .adversal_service import run_adversal_pipeline, parse_adversal_notes

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class IngestionManager:
    @staticmethod
    def process(source: str, language: str = "english", engine: str = "local") -> dict:
        session_id = str(uuid.uuid4())
        fallback_warning = None

        if engine == "adversal":
            try:
                logger.info(f"Starting Adversal AI Cloud ingestion for session {session_id}")
                output_dir = os.path.join(BASE_DIR, "data", "adversal_output", session_id)
                
                # Execute Adversal MCP pipeline with 6 minute timeout
                run_adversal_pipeline(source, output_dir, timeout_seconds=360)
                
                # Parse output notes and visual frame paths
                parsed = parse_adversal_notes(output_dir)
                
                # Ingest transcript / notes into ChromaDB vector store
                rag_chain = build_rag_chain(parsed["transcript"])

                return {
                    "session_id": session_id,
                    "engine": "adversal",
                    "title": parsed["title"],
                    "transcript": parsed["transcript"],
                    "summary": parsed["summary"],
                    "action_items": parsed["action_items"],
                    "key_decisions": parsed["key_decisions"],
                    "open_questions": parsed["open_questions"],
                    "images": parsed.get("images", []),
                    "rag_chain": rag_chain,
                    "fallback_warning": None
                }
            except Exception as e:
                logger.warning(f"Adversal AI Cloud pipeline failed for session {session_id}: {e}. Falling back to Local Pipeline.")
                fallback_warning = f"Adversal AI Cloud failed ({str(e)}). Automatically fell back to Local Pipeline."
                engine = "local"

        # Local Engine Pipeline (Default or Fallback)
        logger.info(f"Executing Local Pipeline ingestion for session {session_id}")
        chunks = process_input(source)
        transcript = transcribe_all(chunks, language)
        title = generate_title(transcript)
        summary_text = summarize(transcript)
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        rag_chain = build_rag_chain(transcript)

        return {
            "session_id": session_id,
            "engine": "local",
            "title": title,
            "transcript": transcript,
            "summary": summary_text,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions,
            "images": [],
            "rag_chain": rag_chain,
            "fallback_warning": fallback_warning
        }
