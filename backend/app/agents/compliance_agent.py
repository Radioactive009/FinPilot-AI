# LangGraph Compliance Agent placeholder
from app.agents.supervisor import AgentState


def run_compliance_agent(state: AgentState):
    # Verify policy matching
    return {"messages": [{"role": "assistant", "content": "Compliance verified."}]}
