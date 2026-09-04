import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(String(50), nullable=False)  # present, absent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    student = relationship("Student", back_populates="attendance_logs")
    subject = relationship("Subject", back_populates="attendance_records")
