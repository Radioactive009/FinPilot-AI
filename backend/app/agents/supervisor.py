# LangGraph Supervisor Agent
from typing import TypedDict, List
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages: List[dict]
    next_agent: str
    context: dict


# Placeholder for supervisor workflow
def run_supervisor(state: AgentState):
    # This supervisor decides which agent to call next
    return {"next_agent": "invoice_agent"}
