import random
import string
from sqlalchemy.orm import Session
from backend.models.user_model import User, ParentStudentPair
from backend.schemas.auth_schema import RegisterRequest, LoginRequest, PairRequest


def generate_pair_code() -> str:
    return "STU" + "".join(random.choices(string.digits, k=5))


def register_user(db: Session, data: RegisterRequest):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("Email already registered")

    role = data.role.lower().strip()
    if role not in ["parent", "student"]:
        raise ValueError("Role must be parent or student")

    pair_code = generate_pair_code() if role == "student" else None

    user = User(
        name=data.name,
        email=data.email,
        password=data.password,
        role=role,
        pair_code=pair_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data: LoginRequest):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.password != data.password:
        raise ValueError("Invalid email or password")
    return user


def pair_student(db: Session, data: PairRequest):
    parent = db.query(User).filter(User.id == data.parent_id, User.role == "parent").first()
    if not parent:
        raise ValueError("Parent not found")

    student = db.query(User).filter(User.pair_code == data.pair_code, User.role == "student").first()
    if not student:
        raise ValueError("Invalid student pair code")

    existing = db.query(ParentStudentPair).filter(
        ParentStudentPair.parent_id == parent.id,
        ParentStudentPair.student_id == student.id,
    ).first()
    if existing:
        return existing, student

    pair = ParentStudentPair(parent_id=parent.id, student_id=student.id)
    db.add(pair)
    db.commit()
    db.refresh(pair)
    return pair, student


def get_students_for_parent(db: Session, parent_id: int):
    pairs = db.query(ParentStudentPair).filter(ParentStudentPair.parent_id == parent_id).all()
    student_ids = [p.student_id for p in pairs]
    if not student_ids:
        return []
    return db.query(User).filter(User.id.in_(student_ids)).all()
