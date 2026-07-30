"""
Feature 5: Data agent (text-to-SQL).
Writes a SQL query from a plain-English question, runs it against the
sample company.db database, and returns the result. This is how the
system answers "how many...", "average...", "total..." questions.

PROXY UPDATE: now uses ChatOpenAI pointed at the mentor's proxy instead
of calling Google directly. Model: gemini-flash-lite (per mentor's spec —
high-volume calls use the lighter model).
"""
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from src.config import GEMINI_API_KEY, PROXY_BASE_URL, SQLITE_DB_PATH
from src.state import AgentState

_db = SQLDatabase.from_uri(f"sqlite:///{SQLITE_DB_PATH}")
_llm = ChatOpenAI(base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-flash-lite")


def data_agent(state: AgentState) -> dict:
    prompt = (
        f"You write SQLite queries.\nSchema:\n{_db.get_table_info()}\n\n"
        f"Write ONE SQLite SELECT query that answers this question: "
        f"{state['question']}\n"
        f"Return ONLY the raw SQL — no explanation, no markdown formatting."
    )
    sql = _llm.invoke(prompt).content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    # Read-only guard — never let the model run anything but a SELECT.
    if not sql.lower().startswith("select"):
        result = "Refused: generated query was not a SELECT statement."
    else:
        result = _db.run(sql)

    return {
        "sql_result": f"SQL: {sql}\nResult: {result}",
        "steps": state.get("steps", []) + ["data(sql)"],
    }
