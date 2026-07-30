"""
Shared state — PHASE 4 UPDATE: added chat_history so the system
remembers previous turns in a conversation.
"""
from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    question: str                  # the user's question (current turn)
    chat_history: List[dict]       # NEW: list of {role, content} dicts from previous turns
    plan: str                      # which agent the supervisor picked next
    documents: List[str]           # chunks from the retriever and/or web agent
    sql_result: Optional[str]      # answer from the data/SQL agent
    code_result: Optional[str]     # answer from the code agent
    answer: str                    # the final drafted answer
    steps: List[str]               # a log of which agents ran, in order
    revisions: int                 # how many times the critic sent the answer back
    critic_ok: bool                # did the critic approve the last drafted answer?


def new_state(question: str, chat_history: List[dict] = None) -> AgentState:
    """Helper to start a fresh state for a new question, carrying history forward."""
    return {
        "question": question,
        "chat_history": chat_history or [],
        "plan": "",
        "documents": [],
        "sql_result": None,
        "code_result": None,
        "answer": "",
        "steps": [],
        "revisions": 0,
        "critic_ok": False,
    }
