"""
Main entry point — PHASE 4 UPDATE: keeps a chat_history list that grows
with every turn, so the system remembers what was said earlier.

Run: python -m main
"""
from src.graph import build_graph
from src.state import new_state

RECURSION_LIMIT = 25


def main():
    app = build_graph()
    chat_history = []  # grows with every question/answer pair

    print("Multi-Agent AI Analyst — ask a question, or type 'quit' to exit.")
    print("It now remembers your previous questions in this session!\n")
    print("Try:")
    print("  'How many customers have churned?'")
    print("  then: 'Why did they leave?'")
    print("  then: 'Which plan had the most churn?'\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue

        # Pass the full history so agents know what was already discussed
        state = new_state(question, chat_history=chat_history)
        result = app.invoke(state, config={"recursion_limit": RECURSION_LIMIT})

        answer = result["answer"]
        print(f"\nAssistant: {answer}")
        print(f"(path: {' → '.join(result['steps'])})\n")

        # Add this turn to history for the next question
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})

        # Keep history to last 10 messages (5 turns) so it doesn't grow forever
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]


if __name__ == "__main__":
    main()
