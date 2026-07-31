"""
Phase 5: FastAPI backend.
Endpoints:
  POST /chat     → send a question, get an answer
  GET  /history  → see conversation history
  GET  /health   → check if API is running
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

from src.graph import build_graph
from src.state import new_state

app = FastAPI(title="Multi-Agent AI Analyst", version="1.0.0")

# ── CORS: allow React frontend to talk to this API ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Build the AI graph once at startup ───────────────────────────────────────
graph = build_graph()

# ── In-memory chat history (resets when server restarts) ─────────────────────
chat_history: List[dict] = []

# ── Request/Response models ───────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    steps: List[str]
    question: str

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "message": "Multi-Agent AI Analyst is running!"}


@app.get("/history")
def get_history():
    return {"history": chat_history, "count": len(chat_history)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    global chat_history

    # Run the AI graph
    state = new_state(req.question, chat_history=chat_history)
    result = graph.invoke(state, config={"recursion_limit": 25})

    answer = result["answer"]
    steps = result["steps"]

    # Save to history
    chat_history.append({"role": "user", "content": req.question})
    chat_history.append({"role": "assistant", "content": answer})

    # Keep last 10 messages (5 turns)
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    return ChatResponse(answer=answer, steps=steps, question=req.question)