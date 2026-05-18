from sqlalchemy.orm import Session
from backend.services.usage_service import get_usage_summary
from backend.agents.report_agent import report_agent


def generate_daily_report(db: Session, student_id: int):
    summary = get_usage_summary(db, student_id)
    return report_agent(summary)
