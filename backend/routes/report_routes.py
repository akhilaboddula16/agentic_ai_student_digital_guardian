from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.report_service import generate_daily_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/student/{student_id}/daily")
def daily_report(student_id: int, db: Session = Depends(get_db)):
    return {"student_id": student_id, "report": generate_daily_report(db, student_id)}
