from src.llm import create_chat_model
import os
"""
Feature 8: Critic / Verifier.
Checks the drafted answer against evidence. Approves or sends back for revision.
Uses plain text parsing instead of structured output (proxy compatibility).
"""
from src.state import AgentState

_llm = create_chat_model()

def critic(state: AgentState) -> dict:
    evidence = "\n\n".join(state.get("documents", []))
    if state.get("sql_result"):
        evidence += f"\n\nSQL: {state['sql_result']}"
    if state.get("code_result"):
        evidence += f"\n\nCode: {state['code_result']}"

    prompt = (
        f"Question: {state['question']}\n"
        f"Evidence:\n{evidence or '(none)'}\n\n"
        f"Drafted answer: {state['answer']}\n\n"
        "Is this answer correct and supported by the evidence?\n"
        "Reply ONLY: YES or NO"
    )
    raw = _llm.invoke(prompt).content.strip().upper()
    approved = raw.startswith("YES")
    tag = "ok" if approved else "revise"
    return {
        "critic_ok": approved,
        "revisions": state.get("revisions", 0) + (0 if approved else 1),
        "steps": state.get("steps", []) + [f"critic({tag})"],
    }
