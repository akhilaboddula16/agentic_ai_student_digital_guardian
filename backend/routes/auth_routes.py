from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.auth_schema import RegisterRequest, LoginRequest, PairRequest
from backend.services.auth_service import register_user, login_user, pair_student, get_students_for_parent

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "pair_code": user.pair_code,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = login_user(db, data)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "pair_code": user.pair_code,
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/pair")
def pair(data: PairRequest, db: Session = Depends(get_db)):
    try:
        pair_record, student = pair_student(db, data)
        return {
            "message": "Student connected successfully",
            "parent_id": pair_record.parent_id,
            "student_id": student.id,
            "student_name": student.name,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/parent/{parent_id}/students")
def parent_students(parent_id: int, db: Session = Depends(get_db)):
    students = get_students_for_parent(db, parent_id)
    return [
        {"id": s.id, "name": s.name, "email": s.email, "pair_code": s.pair_code}
        for s in students
    ]
