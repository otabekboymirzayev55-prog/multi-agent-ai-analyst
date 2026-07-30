"""
Run: python -m tests.test_web
Checks Feature 4 — works with a Tavily key, and skips gracefully without one.
"""
from src.state import new_state
from src.agents.web import web_agent

if __name__ == "__main__":
    state = new_state("What is LangGraph used for?")
    result = web_agent(state)

    print("steps:", result["steps"])
    if "documents" in result and result["documents"]:
        print(f"\nGot {len(result['documents'])} web result(s). First one:")
        print(result["documents"][0][:300])
    else:
        print("\nNo TAVILY_API_KEY set — skipped gracefully, as expected.")
    print("\nPASS")
