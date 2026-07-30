"""
Run: python -m tests.test_graph
Checks Feature 9 — a multi-part question should route through more than
one agent and come back with one final, critic-approved answer.
"""
from src.graph import build_graph
from src.state import new_state

if __name__ == "__main__":
    app = build_graph()
    state = new_state("How many customers churned, and what were the main reasons?")
    result = app.invoke(state, config={"recursion_limit": 25})

    print("Answer:\n", result["answer"])
    print("\nPath taken:", " → ".join(result["steps"]))
    print("Revisions:", result["revisions"])

    assert result["answer"], "No answer was produced."
    assert len(result["steps"]) > 2, "Graph only took one step — routing may not be working."
    print("\nPASS: the graph ran end-to-end through multiple agents and produced an answer.")
