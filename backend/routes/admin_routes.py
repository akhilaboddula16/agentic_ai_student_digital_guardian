from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user_model import User
from backend.security import get_current_user, require_roles
from backend.services.admin_service import delete_user_cascade, list_users_with_metrics, reset_demo_data, reset_student_data

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def admin_list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return {"current_user_id": current_user.id, "users": list_users_with_metrics(db)}


@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account")
    delete_user_cascade(db, user_id)
    return {"message": "User deleted successfully"}


@router.delete("/students/{student_id}/data")
def admin_reset_student_data(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    reset_student_data(db, student_id)
    return {"message": "Student usage and alerts cleared successfully", "student_id": student_id}


@router.post("/reset-demo-data")
def admin_reset_demo(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    reset_demo_data(db)
    return {"message": "Demo data reset successfully", "admin_id": current_user.id}
