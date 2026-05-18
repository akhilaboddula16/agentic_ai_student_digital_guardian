def report_agent(summary: dict) -> str:
    if not summary:
        return "No usage data available today."

    lines = ["Daily Usage Report:"]
    for app, minutes in summary.items():
        lines.append(f"- {app}: {minutes} minutes")

    highest_app = max(summary, key=summary.get)
    lines.append(f"Most used app: {highest_app}")
    return "\n".join(lines)
