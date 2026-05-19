import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.config import ADMIN_EMAILS, TOKEN_TTL_MINUTES
from backend.database import get_db
from backend.models.token_model import AuthToken
from backend.models.user_model import ParentStudentPair, User

_bearer = HTTPBearer(auto_error=False)
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )
    return "scrypt${}${}${}${}${}".format(
        _SCRYPT_N,
        _SCRYPT_R,
        _SCRYPT_P,
        base64.urlsafe_b64encode(salt).decode("utf-8"),
        base64.urlsafe_b64encode(derived).decode("utf-8"),
    )


def is_hashed_password(value: str) -> bool:
    return value.startswith("scrypt$")


def verify_password(password: str, stored_value: str) -> bool:
    if not is_hashed_password(stored_value):
        return hmac.compare_digest(password, stored_value)

    try:
        _, n, r, p, salt_b64, derived_b64 = stored_value.split("$", 5)
        salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
        expected = base64.urlsafe_b64decode(derived_b64.encode("utf-8"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def ensure_password_hashed(db: Session, user: User, plain_password: str):
    if is_hashed_password(user.password):
        return
    user.password = hash_password(plain_password)
    db.add(user)
    db.commit()
    db.refresh(user)


def assign_admin_role_if_eligible(db: Session, user: User):
    if user.email.lower() in ADMIN_EMAILS and user.role != "admin":
        user.role = "admin"
        db.add(user)
        db.commit()
        db.refresh(user)


def create_access_token(db: Session, user: User) -> tuple[str, datetime]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES)
    db.add(AuthToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    db.commit()
    return raw_token, expires_at


def revoke_user_tokens(db: Session, user_id: int):
    db.query(AuthToken).filter(AuthToken.user_id == user_id).delete()
    db.commit()


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "pair_code": user.pair_code,
    }


def _lookup_user_from_token(
    db: Session,
    credentials: HTTPAuthorizationCredentials | None,
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
    token_row = db.query(AuthToken).filter(AuthToken.token_hash == token_hash).first()
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    if token_row.expires_at < datetime.utcnow():
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")

    user = db.query(User).filter(User.id == token_row.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    assign_admin_role_if_eligible(db, user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    return _lookup_user_from_token(db, credentials)


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this resource")
        return current_user

    return _dependency


def ensure_student_access(db: Session, current_user: User, student_id: int):
    if current_user.role == "admin":
        return
    if current_user.role == "student" and current_user.id == student_id:
        return
    if current_user.role == "parent":
        pair = (
            db.query(ParentStudentPair)
            .filter(
                ParentStudentPair.parent_id == current_user.id,
                ParentStudentPair.student_id == student_id,
            )
            .first()
        )
        if pair:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this student")


def ensure_usage_write_access(db: Session, current_user: User, student_id: int):
    if current_user.role == "admin":
        return
    if current_user.role == "student" and current_user.id == student_id:
        return
    if current_user.role == "parent":
        ensure_student_access(db, current_user, student_id)
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot write usage for this student")
