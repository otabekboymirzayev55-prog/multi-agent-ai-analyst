"""
Feature 4: Web agent.
Searches the live web with Tavily for questions outside the local
documents. Skips gracefully (no crash) if no Tavily key is set — the
project still works without it, just without live web results.
"""
from src.config import TAVILY_API_KEY
from src.state import AgentState


def web_agent(state: AgentState) -> dict:
    if not TAVILY_API_KEY:
        # No key configured — skip gracefully, per the "Done when" for F4.
        return {"steps": state.get("steps", []) + ["web(skipped: no key)"]}

    from tavily import TavilyClient

    client = TavilyClient(api_key=TAVILY_API_KEY)
    results = client.search(state["question"])["results"]
    new_docs = [r["content"] for r in results]
    return {
        "documents": state.get("documents", []) + new_docs,
        "steps": state.get("steps", []) + ["web"],
    }
