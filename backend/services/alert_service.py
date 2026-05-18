from sqlalchemy.orm import Session
from backend.models.alert_model import Alert


def get_alerts_by_student(db: Session, student_id: int):
    return db.query(Alert).filter(Alert.student_id == student_id).order_by(Alert.created_at.desc()).all()
