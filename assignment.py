import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    due_date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(String(50), nullable=False)  # Submitted, Pending, Overdue
    score = Column(Float, nullable=True)
    
    student = relationship("Student", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")
