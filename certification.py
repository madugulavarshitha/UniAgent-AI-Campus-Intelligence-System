import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(Date, default=datetime.date.today, nullable=False)
    
    student = relationship("Student", back_populates="certifications")
