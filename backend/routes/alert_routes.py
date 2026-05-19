from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user_model import User
from backend.security import ensure_student_access, get_current_user
from backend.services.alert_service import get_alerts_by_student

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/student/{student_id}")
def student_alerts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_access(db, current_user, student_id)
    alerts = get_alerts_by_student(db, student_id)
    return [
        {
            "id": a.id,
            "student_id": a.student_id,
            "app_name": a.app_name,
            "message": a.message,
            "severity": a.severity,
            "created_at": str(a.created_at),
        }
        for a in alerts
    ]
