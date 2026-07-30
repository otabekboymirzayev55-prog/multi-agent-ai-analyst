"""
Feature 9: Supervisor graph (wiring).
Connects supervisor → specialist agent → back to supervisor, then
generate → critic → finish or revise. This is what turns four separate
functions into an actual multi-agent system.
"""
from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.agents.retriever import retriever_agent
from src.agents.web import web_agent
from src.agents.data_sql import data_agent
from src.agents.code_agent import code_agent
from src.agents.supervisor import supervisor
from src.agents.generate import generate_answer
from src.agents.critic import critic

MAX_REVISIONS = 2  # safety net: force an answer through after this many revisions


def _route_after_supervisor(state: AgentState) -> str:
    return state["plan"]


def _route_after_critic(state: AgentState) -> str:
    if state["critic_ok"] or state["revisions"] >= MAX_REVISIONS:
        return "finish"
    return "revise"


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor)
    g.add_node("retriever", retriever_agent)
    g.add_node("web", web_agent)
    g.add_node("data", data_agent)
    g.add_node("code", code_agent)
    g.add_node("generate", generate_answer)
    g.add_node("critic", critic)

    g.set_entry_point("supervisor")

    g.add_conditional_edges(
    "supervisor",
    _route_after_supervisor,
    {
        "retriever": "retriever",
        "web": "web",
        "data": "data",
        "code": "code",
        "finish": "generate",   # ← THIS was missing! finish → generate → critic → END
    }
)
    for agent_name in ["retriever", "web", "data", "code"]:
        g.add_edge(agent_name, "supervisor")

    g.add_edge("generate", "critic")
    g.add_conditional_edges("critic", _route_after_critic, {"finish": END, "revise": "supervisor"})

    return g.compile()
