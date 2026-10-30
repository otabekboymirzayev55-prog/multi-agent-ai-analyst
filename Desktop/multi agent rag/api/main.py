"""Public API with isolated, bounded in-memory chat sessions."""
import os
import logging
from collections import OrderedDict
from functools import lru_cache
from threading import Lock
from typing import Annotated
from uuid import uuid4
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Multi-Agent AI Analyst", version="1.1.0")
origins = os.getenv('ALLOWED_ORIGINS', 'https://multi-agent-ai-analyst-ui.onrender.com,http://localhost:5173').split(',')
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins], allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['Content-Type','X-Session-ID'])
histories = OrderedDict()
busy = Lock()

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    answer: str
    steps: list[str]
    question: str
    session_id: str

Session = Annotated[str | None, Header(alias='X-Session-ID', min_length=16, max_length=80, pattern=r'^[A-Za-z0-9_-]+$')]

@lru_cache(maxsize=1)
def get_graph():
    from src.graph import build_graph
    return build_graph()

@app.get('/health')
def health():
    return {'status': 'ok', 'configured': bool(os.getenv('GEMINI_API_KEY')), 'version': '1.1.0'}

@app.get('/history')
def history(session_id: Session = None):
    # No session identifier means no shared global history.
    with busy:
        messages = list(histories.get(session_id, [])) if session_id else []
    return {'history': messages, 'count': len(messages)}

@app.post('/chat', response_model=ChatResponse)
def chat(req: ChatRequest, session_id: Session = None):
    question = req.question.strip()
    if not question:
        raise HTTPException(422, 'Question cannot be blank')
    if not busy.acquire(blocking=False):
        raise HTTPException(429, 'The analyst is busy. Please try again shortly.')
    try:
        from src.state import new_state
        session_id = session_id or uuid4().hex
        previous = list(histories.get(session_id, []))
        result = get_graph().invoke(new_state(question, chat_history=previous), config={'recursion_limit': 25})
        answer = result.get('answer')
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError('No answer')
        histories[session_id] = (previous + [{'role':'user','content':question}, {'role':'assistant','content':answer}])[-10:]
        histories.move_to_end(session_id)
        while len(histories) > 200:
            histories.popitem(last=False)
        return ChatResponse(answer=answer, steps=result.get('steps', []), question=question, session_id=session_id)
    except HTTPException:
        raise
    except Exception:
        logging.getLogger(__name__).exception('Analyst request failed')
        raise HTTPException(503, 'The analysis service is unavailable. Please try again later.') from None
    finally:
        busy.release()
