import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VidChat — AI Meeting Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── High-Density Modern CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-dark: #090a0f;
    --card-bg: rgba(18, 20, 29, 0.75);
    --card-border: rgba(255, 255, 255, 0.08);
    --card-hover: rgba(124, 58, 237, 0.3);
    --accent-purple: #8b5cf6;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --text-primary: #f3f4f6;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
}

/* Global resets for compact layout */
.stApp {
    background-color: var(--bg-dark) !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text-primary);
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 98% !important;
}

/* Reduce Streamlit element padding */
[data-testid="stVerticalBlock"] > div {
    gap: 0.75rem !important;
}

/* Header styling */
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.25rem;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    backdrop-filter: blur(16px);
    margin-bottom: 0.5rem;
}

.logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.logo-tag {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-cyan);
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.25);
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0d0e14 !important;
    border-right: 1px solid var(--card-border) !important;
}

/* Custom Cards */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    backdrop-filter: blur(12px);
    transition: all 0.2s ease-in-out;
}

.glass-card:hover {
    border-color: var(--card-hover);
}

.card-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.card-body {
    font-size: 0.88rem;
    line-height: 1.6;
    color: var(--text-primary);
}

/* Status dots */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--card-border);
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.dot-done { background: var(--accent-emerald); box-shadow: 0 0 6px var(--accent-emerald); }
.dot-active { background: var(--accent-purple); box-shadow: 0 0 6px var(--accent-purple); animation: blink 1.2s infinite; }
.dot-pending { background: var(--text-muted); }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Styled Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(13, 14, 20, 0.6);
    padding: 0.3rem;
    border-radius: 10px;
    border: 1px solid var(--card-border);
}

.stTabs [data-baseweb="tab"] {
    height: 2.2rem;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    color: var(--text-secondary) !important;
    padding: 0 1rem;
}

.stTabs [aria-selected="true"] {
    background: var(--accent-purple) !important;
    color: #ffffff !important;
}

/* Chat Container */
.chat-window {
    background: rgba(15, 17, 26, 0.85);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem;
    height: 480px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.chat-bubble-user {
    align-self: flex-end;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.35);
    color: #f3f4f6;
    padding: 0.65rem 0.9rem;
    border-radius: 12px 12px 2px 12px;
    font-size: 0.85rem;
    max-width: 85%;
    line-height: 1.5;
}

.chat-bubble-bot {
    align-self: flex-start;
    background: rgba(17, 24, 39, 0.9);
    border: 1px solid rgba(6, 182, 212, 0.3);
    color: #f3f4f6;
    padding: 0.65rem 0.9rem;
    border-radius: 12px 12px 12px 2px;
    font-size: 0.85rem;
    max-width: 85%;
    line-height: 1.5;
}

.transcript-area {
    background: rgba(10, 11, 16, 0.9);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.7;
    color: var(--text-secondary);
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialization ───────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
    "pending_question": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar Controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1rem">
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#fff">🎬 VidChat</div>
        <div style="font-size:0.75rem;color:var(--text-muted)">AI Video & Meeting Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    source = st.text_input("Source URL or Path", placeholder="YouTube link or local media file...")
    language = st.selectbox("Language Mode", ["english", "hinglish"], index=0, help="English uses local Whisper; Hinglish uses Sarvam AI STT")
    
    analyze_btn = st.button("⚡ Start Analysis", use_container_width=True, type="primary")

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown("<div style='font-size:0.75rem;font-weight:700;color:var(--text-secondary);margin-bottom:0.5rem'>PIPELINE STEPS</div>", unsafe_allow_html=True)
        steps_info = [
            ("audio", "🔊 Audio Extraction"),
            ("transcript", "📝 Transcription"),
            ("title", "🏷️ Title & Summary"),
            ("extract", "🔍 Insight Extraction"),
            ("rag", "🧠 Vector RAG Engine"),
        ]
        for key_name, label_text in steps_info:
            st_val = st.session_state.pipeline_steps.get(key_name, "done")
            dot_class = "dot-done" if st_val == "done" else ("dot-active" if st_val == "active" else "dot-pending")
            st.markdown(f"""
            <div class="status-pill" style="width:100%;margin-bottom:0.3rem">
                <span class="dot {dot_class}"></span>
                <span>{label_text}</span>
            </div>
            """, unsafe_allow_html=True)

# ─── Top Header Bar ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div>
        <span class="logo-text">VidChat</span>
        <span style="font-size:0.85rem;color:var(--text-muted);margin-left:0.5rem">| Intelligent Video Assistant</span>
    </div>
    <div>
        <span class="logo-tag">RAG Powered</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Pipeline Execution ─────────────────────────────────────────────────────────
if analyze_btn:
    if not source.strip():
        st.error("⚠️ Please enter a valid YouTube URL or local file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}
        
        status_box = st.empty()
        
        def set_step(name, state):
            st.session_state.pipeline_steps[name] = state
            
        try:
            status_box.info("⚙️ Processing media... check sidebar for step progress.")
            
            set_step("audio", "active")
            chunks = process_input(source)
            set_step("audio", "done")
            
            set_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            set_step("transcript", "done")
            
            set_step("title", "active")
            title = generate_title(transcript)
            summary = summarize(transcript)
            set_step("title", "done")
            
            set_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions = extract_key_decisions(transcript)
            questions = extract_questions(transcript)
            set_step("extract", "done")
            
            set_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            set_step("rag", "done")
            
            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            status_box.success("✅ Analysis Complete!")
            time.sleep(0.5)
            status_box.empty()
            st.rerun()
            
        except Exception as err:
            status_box.error(f"❌ Error during processing: {err}")

# ─── Main Workspace Dashboard (Split Layout) ────────────────────────────────────
if st.session_state.result:
    res = st.session_state.result
    
    # Title Banner
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom:0.75rem;border-left:4px solid var(--accent-purple)">
        <div class="card-label">📌 Meeting Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#ffffff">
            {res['title']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Split 2-Column Layout (Left: Intelligence Dashboard, Right: Interactive RAG Chat)
    col_dash, col_chat = st.columns([55, 45], gap="medium")
    
    # ── Left Column: Intelligence Dashboard Tabs ────────────────────────────────
    with col_dash:
        tab_summary, tab_insights, tab_transcript = st.tabs([
            "📋 Summary", 
            "💡 Action & Decisions", 
            "📝 Full Transcript"
        ])
        
        with tab_summary:
            st.markdown(f"""
            <div class="glass-card" style="min-height:360px">
                <div class="card-label">📋 Executive Summary</div>
                <div class="card-body">{res['summary']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with tab_insights:
            c1, c2 = st.columns(2, gap="small")
            with c1:
                st.markdown(f"""
                <div class="glass-card" style="border-top:3px solid var(--accent-emerald)">
                    <div class="card-label" style="color:var(--accent-emerald)">✅ Action Items</div>
                    <div class="card-body">{res['action_items']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="glass-card" style="border-top:3px solid var(--accent-cyan)">
                    <div class="card-label" style="color:var(--accent-cyan)">🔑 Key Decisions</div>
                    <div class="card-body">{res['key_decisions']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="glass-card" style="margin-top:0.5rem;border-top:3px solid var(--accent-amber)">
                <div class="card-label" style="color:var(--accent-amber)">❓ Open Questions & Follow-ups</div>
                <div class="card-body">{res['open_questions']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with tab_transcript:
            st.markdown(f'<div class="transcript-area">{res["transcript"]}</div>', unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Transcript (.txt)",
                data=res["transcript"],
                file_name="meeting_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )

    # ── Right Column: Interactive RAG Chat Box ──────────────────────────────────
    with col_chat:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem">
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#fff">
                💬 Chat with Meeting
            </div>
            <span style="font-size:0.7rem;color:var(--accent-cyan)">RAG Assistant Active</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggested prompt chips
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        if chip_col1.button("📋 Key Takeaways", use_container_width=True):
            st.session_state.pending_question = "What are the top 3 key takeaways from this meeting?"
        if chip_col2.button("✅ Action Items", use_container_width=True):
            st.session_state.pending_question = "List all action items and who is responsible for them."
        if chip_col3.button("🔑 Decisions Made", use_container_width=True):
            st.session_state.pending_question = "What key decisions were reached during this discussion?"

        # Chat Window Container
        chat_html = '<div class="chat-window">'
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_html += f'<div class="chat-bubble-user"><b>You:</b> {msg["content"]}</div>'
                else:
                    chat_html += f'<div class="chat-bubble-bot"><b>🤖 Assistant:</b> {msg["content"]}</div>'
        else:
            chat_html += """
            <div style="margin:auto;text-align:center;color:var(--text-muted)">
                <div style="font-size:2rem">💬</div>
                <div style="font-size:0.8rem;margin-top:0.4rem">Ask any question about your meeting transcript.</div>
            </div>
            """
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Chat Input Form
        with st.form(key="chat_form", clear_on_submit=True):
            input_val = st.text_input(
                "Ask a question",
                value=st.session_state.pending_question,
                placeholder="Ask about specific topics, owners, or decisions...",
                label_visibility="collapsed"
            )
            st.session_state.pending_question = ""  # Reset pending question
            
            c_send, c_clear = st.columns([4, 1])
            submit_chat = c_send.form_submit_button("Send Answer →", use_container_width=True, type="primary")
            clear_chat = c_clear.form_submit_button("🗑️", use_container_width=True)

        if submit_chat and input_val.strip():
            with st.spinner("Thinking..."):
                answer = ask_question(res["rag_chain"], input_val.strip())
            st.session_state.chat_history.append({"role": "user", "content": input_val.strip()})
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

        if clear_chat:
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty State (Hero Banner)
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:4rem 2rem;margin-top:2rem">
        <div style="font-size:3.5rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;color:#fff;margin-bottom:0.5rem">
            Welcome to VidChat
        </div>
        <div style="color:var(--text-secondary);font-size:0.9rem;max-width:480px;margin:0 auto 2rem auto;line-height:1.6">
            Transform any video or audio file into structured meeting notes, actionable insights, and an interactive RAG AI assistant.
        </div>
        <div style="display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap">
            <span class="logo-tag">⚡ Automated Speech-to-Text</span>
            <span class="logo-tag">📋 Map-Reduce Summaries</span>
            <span class="logo-tag">💬 Real-time RAG Q&A</span>
        </div>
    </div>
    """, unsafe_allow_html=True)