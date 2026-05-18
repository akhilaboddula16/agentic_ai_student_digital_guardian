from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.usage_schema import UsageCreate
from backend.services.usage_service import add_usage, get_usage_by_student, get_usage_summary

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.post("/add")
def create_usage(data: UsageCreate, db: Session = Depends(get_db)):
    record, alert, state = add_usage(db, data)
    return {
        "usage": {
            "id": record.id,
            "student_id": record.student_id,
            "app_name": record.app_name,
            "duration_minutes": record.duration_minutes,
            "limit_minutes": record.limit_minutes,
            "is_blocked": record.is_blocked,
        },
        "alert": {
            "id": alert.id,
            "message": alert.message,
            "severity": alert.severity,
        },
        "agent_workflow": state,
    }


@router.get("/student/{student_id}")
def student_usage(student_id: int, db: Session = Depends(get_db)):
    records = get_usage_by_student(db, student_id)
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "app_name": r.app_name,
            "duration_minutes": r.duration_minutes,
            "limit_minutes": r.limit_minutes,
            "opened_at": str(r.opened_at),
            "is_blocked": r.is_blocked,
        }
        for r in records
    ]


@router.get("/student/{student_id}/summary")
def student_summary(student_id: int, db: Session = Depends(get_db)):
    return get_usage_summary(db, student_id)
