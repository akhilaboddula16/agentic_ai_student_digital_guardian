from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from backend.database import Base


class AppUsage(Base):
    __tablename__ = "app_usage"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_name = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    limit_minutes = Column(Integer, default=60)
    opened_at = Column(DateTime, default=datetime.now)
    is_blocked = Column(Boolean, default=False)
