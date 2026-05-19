from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.usage_schema import DeviceUsageSyncRequest, UsageCreate
from backend.security import ensure_student_access, ensure_usage_write_access, get_current_user
from backend.services.usage_service import add_usage, get_usage_by_student, get_usage_summary
from backend.models.user_model import User

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.post("/add")
def create_usage(
    data: UsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_usage_write_access(db, current_user, data.student_id)
    try:
        record, alert, state = add_usage(db, data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
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


@router.post("/sync")
def sync_usage(
    data: DeviceUsageSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts can sync device usage",
        )
    payload = UsageCreate(
        student_id=current_user.id,
        app_name=data.app_name,
        duration_minutes=data.duration_minutes,
        limit_minutes=data.limit_minutes,
    )
    try:
        record, alert, state = add_usage(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
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
def student_usage(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_access(db, current_user, student_id)
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
def student_summary(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_student_access(db, current_user, student_id)
    return get_usage_summary(db, student_id)
