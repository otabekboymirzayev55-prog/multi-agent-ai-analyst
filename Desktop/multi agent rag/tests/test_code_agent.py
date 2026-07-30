"""
Run: python -m tests.test_code_agent
Checks Feature 6 — a math question should return the correct computed answer.
(15% of 240 is 36.)
"""
from src.state import new_state
from src.agents.code_agent import code_agent

if __name__ == "__main__":
    state = new_state("What is 15% of 240?")
    result = code_agent(state)

    print("code_result:", result["code_result"])
    print("steps:", result["steps"])
    print("\nCheck by eye: the correct answer is 36.")
