"""
Feature 6: Code agent.
Writes and runs Python for calculations that an LLM can't reliably do
by just "thinking" — real math, aggregation, percentages.

PROXY UPDATE: now uses ChatOpenAI pointed at the mentor's proxy instead
of calling Google directly. Model: gemini-flash-lite (per mentor's spec —
high-volume calls use the lighter model).

Watch out (from the guide): this runs model-written code. For this local
starter version that's the same sandboxed REPL LangChain provides; if you
ever deploy this publicly, keep a runtime cap and don't give it filesystem
or network access.
"""
from langchain_experimental.tools import PythonREPLTool
from langchain_openai import ChatOpenAI

from src.config import GEMINI_API_KEY, PROXY_BASE_URL
from src.state import AgentState

_py = PythonREPLTool()
_llm = ChatOpenAI(base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-flash-lite")


def code_agent(state: AgentState) -> dict:
    prompt = (
        f"Write ONLY Python code (no explanation, no markdown fences) that "
        f"computes the answer to: {state['question']}\n"
        f"End with a print() statement showing the final result."
    )
    code = _llm.invoke(prompt).content.strip()
    code = code.replace("```python", "").replace("```", "").strip()

    result = _py.run(code)
    return {
        "code_result": result,
        "steps": state.get("steps", []) + ["code"],
    }
