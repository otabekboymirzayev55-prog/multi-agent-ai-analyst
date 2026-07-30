"""
Run: python -m tests.test_memory
Checks Feature 10 — a follow-up question should produce a relevant answer
that makes sense in the context of the previous question, proving the
system is using chat_history correctly.
"""
from src.graph import build_graph
from src.state import new_state

if __name__ == "__main__":
    app = build_graph()

    # Turn 1
    q1 = "How many customers have churned?"
    r1 = app.invoke(new_state(q1), config={"recursion_limit": 25})
    a1 = r1["answer"]
    print(f"Q1: {q1}")
    print(f"A1: {a1}\n")

    # Turn 2 — a follow-up that only makes sense if history is remembered
    history = [
        {"role": "user", "content": q1},
        {"role": "assistant", "content": a1},
    ]
    q2 = "Why did they leave?"
    r2 = app.invoke(new_state(q2, chat_history=history), config={"recursion_limit": 25})
    a2 = r2["answer"]
    print(f"Q2: {q2}")
    print(f"A2: {a2}\n")

    print("Path Q2:", " → ".join(r2["steps"]))

    # The follow-up answer should mention churn reasons, not be confused
    assert any(word in a2.lower() for word in ["price", "usage", "churn", "reason", "left"]), \
        "Follow-up answer doesn't seem to understand the context — memory may not be working."
    print("\nPASS: follow-up question was answered in context.")
