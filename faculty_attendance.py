import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base

class FacultyAttendance(Base):
    __tablename__ = "faculty_attendance"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    faculty_id = Column(String(36), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(String(50), default="Present", nullable=False)  # Present, Absent, On Leave
    check_in_time = Column(String(50), nullable=True)
    check_out_time = Column(String(50), nullable=True)
    lecture_topic = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    faculty = relationship("Faculty", backref="attendance_logs")
