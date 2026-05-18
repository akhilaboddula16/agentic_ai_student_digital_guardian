def analysis_agent(state: dict) -> dict:
    duration = state.get("duration_minutes", 0)
    limit = state.get("limit_minutes", 60)

    if duration >= limit * 1.5:
        risk = "high"
    elif duration > limit:
        risk = "medium"
    else:
        risk = "low"

    state["risk_level"] = risk
    state.setdefault("agent_notes", []).append(
        f"Analysis Agent found risk level as {risk}"
    )
    return state
