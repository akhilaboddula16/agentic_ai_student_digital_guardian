import random
import string
from sqlalchemy.orm import Session
from backend.config import ADMIN_EMAILS, REGISTRATION_INVITE_CODE, REGISTRATION_MODE
from backend.models.user_model import User, ParentStudentPair
from backend.schemas.auth_schema import RegisterRequest, LoginRequest, PairRequest
from backend.security import assign_admin_role_if_eligible, ensure_password_hashed, hash_password, verify_password


def generate_pair_code() -> str:
    return "STU" + "".join(random.choices(string.digits, k=5))


def register_user(db: Session, data: RegisterRequest):
    if REGISTRATION_MODE == "closed":
        raise ValueError("Public registration is disabled")
    if REGISTRATION_MODE == "invite_only":
        if not REGISTRATION_INVITE_CODE or data.invite_code != REGISTRATION_INVITE_CODE:
            raise ValueError("A valid invite code is required")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("Email already registered")

    role = data.role.lower().strip()
    if role not in ["parent", "student"]:
        raise ValueError("Role must be parent or student")

    if data.email.lower() in ADMIN_EMAILS:
        role = "admin"

    pair_code = generate_pair_code() if role == "student" else None

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=role,
        pair_code=pair_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data: LoginRequest):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise ValueError("Invalid email or password")
    ensure_password_hashed(db, user, data.password)
    assign_admin_role_if_eligible(db, user)
    return user


def pair_student(db: Session, parent_id: int, data: PairRequest):
    parent = db.query(User).filter(User.id == parent_id, User.role.in_(["parent", "admin"])).first()
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


def get_all_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()
