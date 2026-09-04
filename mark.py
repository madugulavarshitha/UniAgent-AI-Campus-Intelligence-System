import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Mark(Base):
    __tablename__ = "marks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # internal, external
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    
    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")
