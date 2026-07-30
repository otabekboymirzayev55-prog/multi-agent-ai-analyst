"""
Run: python -m tests.test_retriever
Checks Feature 3 — the retriever should return chunks about churn when asked
a document question. Run src/ingest.py first.
"""
from src.state import new_state
from src.agents.retriever import retriever_agent

if __name__ == "__main__":
    state = new_state("Why did customers churn last quarter?")
    result = retriever_agent(state)

    print("--- Retrieved chunks ---")
    for i, chunk in enumerate(result["documents"], 1):
        print(f"\n[{i}] {chunk[:200]}...")

    print("\nsteps:", result["steps"])
    assert len(result["documents"]) > 0, "No chunks returned — did you run src/ingest.py first?"
    print("\nPASS: retriever returned chunks.")
