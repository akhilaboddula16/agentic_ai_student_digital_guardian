def action_agent(state: dict) -> dict:
    app_name = state.get("app_name", "Unknown App")
    duration = state.get("duration_minutes", 0)
    limit = state.get("limit_minutes", 60)

    if state.get("should_block"):
        message = f"Alert: {app_name} crossed the limit. Used {duration} mins, allowed {limit} mins. Block simulated."
        severity = "high"
    else:
        message = f"Info: {app_name} used for {duration} mins. Within allowed limit."
        severity = "low"

    state["alert_message"] = message
    state["severity"] = severity
    state.setdefault("agent_notes", []).append("Action Agent created alert/action message")
    return state
