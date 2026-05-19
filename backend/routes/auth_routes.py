from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.auth_schema import RegisterRequest, LoginRequest, PairRequest
from backend.security import create_access_token, get_current_user, revoke_user_tokens, serialize_user
from backend.services.auth_service import register_user, login_user, pair_student, get_students_for_parent
from backend.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data)
        return serialize_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = login_user(db, data)
        revoke_user_tokens(db, user.id)
        access_token, expires_at = create_access_token(db, user)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": expires_at.isoformat(),
            "user": serialize_user(user),
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/pair")
def pair(
    data: PairRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pair_record, student = pair_student(db, current_user.id, data)
        return {
            "message": "Student connected successfully",
            "parent_id": pair_record.parent_id,
            "student_id": student.id,
            "student_name": student.name,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    revoke_user_tokens(db, current_user.id)
    return {"message": "Logged out successfully"}


@router.get("/me/students")
def parent_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["parent", "admin"]:
        raise HTTPException(status_code=403, detail="Only parents and admins can access linked students")
    students = get_students_for_parent(db, current_user.id)
    return [
        {"id": s.id, "name": s.name, "email": s.email, "pair_code": s.pair_code}
        for s in students
    ]
