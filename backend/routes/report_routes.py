from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user_model import User
from backend.security import ensure_student_access, get_current_user
from backend.services.report_service import generate_daily_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/student/{student_id}/daily")
def daily_report(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_access(db, current_user, student_id)
    return {"student_id": student_id, "report": generate_daily_report(db, student_id)}
