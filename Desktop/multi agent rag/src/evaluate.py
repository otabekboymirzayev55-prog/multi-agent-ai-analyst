"""
Feature 11: Evaluation harness.
Runs a set of test questions automatically and scores the system on:
  1. Did the answer contain the expected keywords?
  2. Did the right agents get called?
  3. Did the critic approve the answer?

Run: python -m src.evaluate
Results are saved to data/eval_results.json so you can track improvement over time.
"""
import json
import time
from datetime import datetime

from src.graph import build_graph
from src.state import new_state

EVAL_FILE = "data/eval_questions.json"
RESULTS_FILE = "data/eval_results.json"


def score_answer(answer: str, expected_keywords: list) -> dict:
    """Check how many expected keywords appear in the answer."""
    answer_lower = answer.lower()
    hits = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    score = len(hits) / len(expected_keywords) if expected_keywords else 1.0
    return {"hits": hits, "misses": [kw for kw in expected_keywords if kw.lower() not in answer_lower], "score": score}


def score_agents(steps: list, expected_agents: list) -> dict:
    """Check whether the expected agent types were called."""
    steps_str = " ".join(steps).lower()
    hits = [a for a in expected_agents if a in steps_str]
    score = len(hits) / len(expected_agents) if expected_agents else 1.0
    return {"hits": hits, "misses": [a for a in expected_agents if a not in steps_str], "score": score}


def main():
    with open(EVAL_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    app = build_graph()
    results = []
    total_keyword_score = 0.0
    total_agent_score = 0.0
    total_critic_ok = 0

    print(f"Running evaluation on {len(questions)} questions...\n")
    print("=" * 60)

    for q in questions:
        print(f"[{q['id']}] {q['question']}")
        start = time.time()

        state = new_state(q["question"])
        result = app.invoke(state, config={"recursion_limit": 25})
        elapsed = round(time.time() - start, 1)

        kw_score = score_answer(result["answer"], q["expected_keywords"])
        ag_score = score_agents(result["steps"], q["expected_agents"])
        critic_ok = result.get("critic_ok", False)

        total_keyword_score += kw_score["score"]
        total_agent_score += ag_score["score"]
        total_critic_ok += int(critic_ok)

        status = "✅ PASS" if kw_score["score"] >= 0.5 and critic_ok else "❌ FAIL"
        print(f"  {status} | keywords {kw_score['score']*100:.0f}% | agents {ag_score['score']*100:.0f}% | critic={'ok' if critic_ok else 'failed'} | {elapsed}s")
        if kw_score["misses"]:
            print(f"  Missing keywords: {kw_score['misses']}")
        if ag_score["misses"]:
            print(f"  Missing agents:   {ag_score['misses']}")
        print(f"  Answer: {result['answer'][:120]}...")
        print()

        results.append({
            "id": q["id"],
            "question": q["question"],
            "answer": result["answer"],
            "steps": result["steps"],
            "keyword_score": kw_score,
            "agent_score": ag_score,
            "critic_ok": critic_ok,
            "revisions": result.get("revisions", 0),
            "elapsed_seconds": elapsed,
        })

    n = len(questions)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": n,
        "avg_keyword_score": round(total_keyword_score / n * 100, 1),
        "avg_agent_score": round(total_agent_score / n * 100, 1),
        "critic_pass_rate": round(total_critic_ok / n * 100, 1),
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Keyword score:    {summary['avg_keyword_score']}%")
    print(f"  Agent routing:    {summary['avg_agent_score']}%")
    print(f"  Critic pass rate: {summary['critic_pass_rate']}%")
    print(f"\nFull results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
