import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50), nullable=False)  # Beginner, Intermediate, Expert
    
    student = relationship("Student", back_populates="skills_list")
