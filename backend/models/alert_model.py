from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.now)
