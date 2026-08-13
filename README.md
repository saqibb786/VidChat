# 🎬 VidChat — AI Video & Meeting Intelligence Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![LangChain](https://img.shields.io/badge/RAG-LangChain-1C3C3C?style=flat-square)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/VectorStore-ChromaDB-FF6F61?style=flat-square)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**VidChat** is an intelligent, full-stack Video & Audio Meeting Assistant powered by **FastAPI**, **React (Vite)**, **OpenAI Whisper**, **Sarvam AI STT**, and **Mistral AI RAG**. It transforms any YouTube video or local media file into structured executive summaries, actionable insights, key decisions, and an interactive context-bounded Q&A chat environment.

---

## ✨ Features

- 🎥 **YouTube & Local Media Processing**: Accepts any YouTube URL or local audio/video file (`.mp4`, `.mp3`, `.wav`, `.m4a`).
- 🎙️ **Multi-Language Speech-to-Text**:
  - **English**: High-accuracy local transcription using **OpenAI Whisper** (`base`).
  - **Hinglish**: Real-time speech recognition & translation using **Sarvam AI STT** (`saaras:v2.5`).
- 📋 **Automated Map-Reduce Summaries**: Generates concise executive summaries, actionable takeaways, key decisions, and unresolved follow-up questions using **Mistral AI** (`mistral-small-latest`).
- 🧠 **Context-Bounded Vector RAG**: Splits transcripts, generates HuggingFace embeddings (`all-MiniLM-L6-v2`), persists vector stores in **ChromaDB**, and enables conversational Q&A.
- 🎨 **Modern Glassmorphism UI**: High-density React interface featuring a collapsible sidebar, 2-column split workspace, tabbed insights, formatted Markdown output parsing (`react-markdown`), and 1-click transcript `.txt` downloads.

---

## 🏗️ Architecture Pipeline

```
  ┌─────────────────────────────────────────────────────────────┐
  │                   Media Source Input                        │
  │              (YouTube URL or Local File)                    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 backend/app/utils/                          │
  │           yt-dlp + pydub Audio Conversion (16kHz WAV)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────┴──────────────────────────────┐
  │                   backend/app/core/                         │
  │  Whisper STT (English)  │  Sarvam AI Translation (Hinglish)  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               Mistral AI Map-Reduce Engine                  │
  │  Summary  │  Action Items  │  Key Decisions  │  Questions   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               ChromaDB Vector RAG Engine                    │
  │     HuggingFace Embeddings + LangChain LCEL RAG Chain       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               Full-Stack React + Vite Web UI                │
  │           FastAPI Backend (8000) ◄─► React UI (5173)         │
  └─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Directory Structure

```
VidChat/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI REST API endpoints (/api/analyze, /api/chat, /api/health)
│   │   ├── core/
│   │   │   ├── extractor.py     # Action Items, Key Decisions, Open Questions
│   │   │   ├── rag_engine.py    # LangChain + ChromaDB RAG chain
│   │   │   ├── summarizer.py   # Title & Map-Reduce summarization
│   │   │   ├── transcriber.py  # OpenAI Whisper & Sarvam AI STT
│   │   │   └── vector_store.py # Chroma vector database persist store
│   │   └── utils/
│   │       └── audio_processor.py # yt-dlp, pydub, ffmpeg audio conversion
│   ├── data/                    # Isolated runtime storage (downloads/ & vector_db/)
│   └── .env                     # API credentials
│
├── frontend/                    # Vite + React Frontend Client
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx       # Top logo banner & status indicators
│   │   │   ├── Sidebar.jsx      # Collapsible control panel & pipeline tracker
│   │   │   ├── Dashboard.jsx    # Left-column tabs (Summary, Insights, Transcript)
│   │   │   ├── ChatBox.jsx      # Right-column RAG Assistant Chatbox
│   │   │   └── FormattedText.jsx# Clean Markdown parser (react-markdown)
│   │   ├── styles/
│   │   │   └── index.css        # Glassmorphism dark theme styling
│   │   ├── App.jsx              # Main App state & API client
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .env                        # Root API credentials
├── .gitignore
├── pyproject.toml
├── Requirements.txt
└── README.md
```

---

## 🚀 Local Installation & Setup Guide

### 1. Prerequisites
- **Python**: `>=3.12`
- **Node.js**: `>=18.0`
- **Package Managers**: `uv` (or `pip`) and `npm`

### 2. Environment Configuration
Create a `.env` file at the root directory:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
WHISPER_MODEL=base
```

### 3. Backend Setup & Launch
Install backend Python dependencies and start the FastAPI server:

```bash
# Sync Python virtual environment dependencies
uv sync

# Launch FastAPI backend server
uv run uvicorn backend.app.main:app --reload --port 8000
```
Backend API will run at **`http://localhost:8000`** *(API docs at `http://localhost:8000/docs`)*.

### 4. Frontend Setup & Launch
Open a second terminal inside the `frontend` folder:

```bash
cd frontend

# Install Node modules
npm install

# Start Vite React dev server
npm run dev
```
Open your browser at **`http://localhost:5173`**.

---

## ☁️ Free Deployment Guide

### Option 1: Deploy Backend on Render (Free Tier)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com/) and click **New + -> Web Service**.
3. Connect your `VidChat` repository.
4. Set settings:
   - **Root Directory**: `.`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r Requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables (`MISTRAL_API_KEY`, `SARVAM_API_KEY`).
6. Click **Deploy Web Service**.

### Option 2: Deploy Frontend on Vercel (Free Tier)
1. Sign in to [Vercel](https://vercel.com/) and click **Add New -> Project**.
2. Import your `VidChat` repository.
3. Set settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable if needed:
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com/api`
5. Click **Deploy**.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
