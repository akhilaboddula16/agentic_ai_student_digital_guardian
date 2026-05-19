from sqlalchemy.orm import Session
from backend.models.usage_model import AppUsage
from backend.models.alert_model import Alert
from backend.models.user_model import User
from backend.schemas.usage_schema import UsageCreate
from backend.agents.graph import run_usage_agent_workflow


def add_usage(db: Session, usage: UsageCreate):
    student = db.query(User).filter(User.id == usage.student_id, User.role == "student").first()
    if not student:
        raise ValueError("Student not found")

    state = run_usage_agent_workflow(usage.model_dump())

    record = AppUsage(
        student_id=usage.student_id,
        app_name=usage.app_name,
        duration_minutes=usage.duration_minutes,
        limit_minutes=usage.limit_minutes,
        is_blocked=state["should_block"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    alert = Alert(
        student_id=usage.student_id,
        app_name=usage.app_name,
        message=state["alert_message"],
        severity=state["severity"],
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return record, alert, state


def get_usage_by_student(db: Session, student_id: int):
    return db.query(AppUsage).filter(AppUsage.student_id == student_id).order_by(AppUsage.opened_at.desc()).all()


def get_usage_summary(db: Session, student_id: int):
    records = db.query(AppUsage).filter(AppUsage.student_id == student_id).all()
    summary = {}
    for r in records:
        summary[r.app_name] = summary.get(r.app_name, 0) + r.duration_minutes
    return summary
