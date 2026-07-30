"""
Feature 7: Supervisor / Router.
Routes question to the right agent. Forces finish if agents already ran.
"""
from langchain_openai import ChatOpenAI
from src.config import GEMINI_API_KEY, PROXY_BASE_URL
from src.state import AgentState

_llm = ChatOpenAI(base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-flash-lite")
VALID_ROUTES = {"retriever", "web", "data", "code", "finish"}

def supervisor(state: AgentState) -> dict:
    steps = state.get("steps", [])

    # ── Safety net: if any agent ran 2+ times already, force finish ──
    from collections import Counter
    agent_counts = Counter(s.split("→")[-1] for s in steps if "→" in s)
    if any(v >= 2 for v in agent_counts.values()):
        return {
            "plan": "finish",
            "steps": steps + ["supervisor→finish(forced)"]
        }

    # ── Also force finish if we already have useful results ──
    has_results = (
        state.get("sql_result") or
        state.get("code_result") or
        len(state.get("documents", [])) > 0
    )
    if has_results and len(steps) >= 3:
        return {
            "plan": "finish",
            "steps": steps + ["supervisor→finish(has_results)"]
        }

    # ── Normal LLM routing ────────────────────────────────────────────
    history_text = ""
    for msg in state.get("chat_history", []):
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = (
        f"Previous conversation:\n{history_text or '(none yet)'}\n\n"
        f"Current question: {state['question']}\n"
        f"Agents already run: {steps}\n"
        f"Documents collected: {len(state.get('documents', []))}\n"
        f"SQL result: {state.get('sql_result')}\n"
        f"Code result: {state.get('code_result')}\n\n"
        "Pick ONE agent to run next, or say finish if you have enough info.\n"
        "Rules:\n"
        "- Questions about customers/revenue/churn → data\n"
        "- Questions about documents/policies → retriever\n"
        "- Questions needing current info → web\n"
        "- Questions needing calculation → code\n"
        "- If any agent already ran and gave results → finish\n\n"
        "Reply with ONLY one word: retriever, web, data, code, or finish"
    )
    raw = _llm.invoke(prompt).content.strip().lower()
    first_word = raw.split()[0] if raw.split() else "finish"
    route = first_word if first_word in VALID_ROUTES else "finish"
    return {
        "plan": route,
        "steps": steps + [f"supervisor→{route}"]
    }