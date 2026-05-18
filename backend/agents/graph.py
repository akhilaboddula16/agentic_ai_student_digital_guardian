from backend.agents.monitoring_agent import monitoring_agent
from backend.agents.analysis_agent import analysis_agent
from backend.agents.decision_agent import decision_agent
from backend.agents.action_agent import action_agent


def run_usage_agent_workflow(usage_data: dict) -> dict:
    """
    Simple agentic workflow for fresher-level project.
    Later you can replace this with LangGraph StateGraph.
    """
    state = monitoring_agent(usage_data)
    state = analysis_agent(state)
    state = decision_agent(state)
    state = action_agent(state)
    return state
