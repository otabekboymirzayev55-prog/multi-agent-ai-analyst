from src.llm import create_chat_model
import os
"""
Feature 5: Data agent (text-to-SQL).
Writes a SQL query from a plain-English question, runs it against the
sample company.db database, and returns the result. This is how the
system answers "how many...", "average...", "total..." questions.

PROXY UPDATE: now uses ChatOpenAI pointed at the official Gemini API instead
of calling Google directly. Model: gemini-3.5-flash-lite (per mentor's spec —
high-volume calls use the lighter model).
"""
from langchain_community.utilities import SQLDatabase

from src.config import SQLITE_DB_PATH
from src.state import AgentState
from src.safe_tools import read_sql

_db = SQLDatabase.from_uri(f"sqlite:///{SQLITE_DB_PATH}")
_llm = create_chat_model()


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
        result = str(read_sql(SQLITE_DB_PATH, sql))

    return {
        "sql_result": f"SQL: {sql}\nResult: {result}",
        "steps": state.get("steps", []) + ["data(sql)"],
    }
