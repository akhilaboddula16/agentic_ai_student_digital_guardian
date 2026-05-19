from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.alert_model import Alert
from backend.models.token_model import AuthToken
from backend.models.usage_model import AppUsage
from backend.models.user_model import ParentStudentPair, User


def list_users_with_metrics(db: Session):
    usage_counts = {
        row[0]: row[1]
        for row in db.query(AppUsage.student_id, func.count(AppUsage.id)).group_by(AppUsage.student_id).all()
    }
    alert_counts = {
        row[0]: row[1]
        for row in db.query(Alert.student_id, func.count(Alert.id)).group_by(Alert.student_id).all()
    }
    student_links = {
        row[0]: row[1]
        for row in db.query(
            ParentStudentPair.parent_id,
            func.count(ParentStudentPair.id),
        ).group_by(ParentStudentPair.parent_id).all()
    }

    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "pair_code": user.pair_code,
            "created_at": user.created_at.isoformat(),
            "usage_events": usage_counts.get(user.id, 0),
            "alerts": alert_counts.get(user.id, 0),
            "linked_students": student_links.get(user.id, 0),
        }
        for user in users
    ]


def delete_user_cascade(db: Session, user_id: int):
    db.query(ParentStudentPair).filter(
        (ParentStudentPair.parent_id == user_id) | (ParentStudentPair.student_id == user_id)
    ).delete(synchronize_session=False)
    db.query(AppUsage).filter(AppUsage.student_id == user_id).delete(synchronize_session=False)
    db.query(Alert).filter(Alert.student_id == user_id).delete(synchronize_session=False)
    db.query(AuthToken).filter(AuthToken.user_id == user_id).delete(synchronize_session=False)
    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()


def reset_student_data(db: Session, student_id: int):
    db.query(AppUsage).filter(AppUsage.student_id == student_id).delete(synchronize_session=False)
    db.query(Alert).filter(Alert.student_id == student_id).delete(synchronize_session=False)
    db.commit()


def reset_demo_data(db: Session):
    db.query(ParentStudentPair).delete(synchronize_session=False)
    db.query(AppUsage).delete(synchronize_session=False)
    db.query(Alert).delete(synchronize_session=False)
    db.query(AuthToken).delete(synchronize_session=False)
    db.commit()
