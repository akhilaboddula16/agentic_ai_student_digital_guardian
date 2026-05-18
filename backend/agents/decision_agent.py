def decision_agent(state: dict) -> dict:
    duration = state.get("duration_minutes", 0)
    limit = state.get("limit_minutes", 60)

    should_block = duration > limit
    state["should_block"] = should_block
    state["decision"] = "block_app" if should_block else "allow_app"
    state.setdefault("agent_notes", []).append(
        "Decision Agent decided to block app" if should_block else "Decision Agent allowed app"
    )
    return state
