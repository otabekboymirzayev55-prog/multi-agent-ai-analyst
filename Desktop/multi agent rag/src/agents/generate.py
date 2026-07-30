"""
Feature 9 (generate step) — PHASE 4 UPDATE: includes chat_history so
the generated answer is aware of what was already said in this conversation.
"""
from langchain_openai import ChatOpenAI

from src.config import GEMINI_API_KEY, PROXY_BASE_URL
from src.state import AgentState

_llm = ChatOpenAI(base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-flash-lite")


def generate_answer(state: AgentState) -> dict:
    evidence = "\n\n".join(state.get("documents", []))
    if state.get("sql_result"):
        evidence += f"\n\nSQL evidence:\n{state['sql_result']}"
    if state.get("code_result"):
        evidence += f"\n\nCode evidence:\n{state['code_result']}"

    # Include conversation history so follow-up answers make sense
    history_text = ""
    for msg in state.get("chat_history", []):
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = (
        f"Previous conversation:\n{history_text or '(none yet)'}\n\n"
        f"Current question: {state['question']}\n\n"
        f"Evidence gathered:\n{evidence or '(none)'}\n\n"
        "Write a clear, direct answer using ONLY the evidence above. "
        "If this is a follow-up question, refer back to the conversation naturally. "
        "If the evidence doesn't fully answer the question, say plainly what's missing."
    )
    answer = _llm.invoke(prompt).content.strip()
    return {"answer": answer, "steps": state.get("steps", []) + ["generate"]}
