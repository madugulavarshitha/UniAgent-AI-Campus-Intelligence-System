import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class JobRequirement(Base):
    __tablename__ = "job_requirements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    min_cgpa = Column(Float, default=0.0, nullable=False)
    required_skills = Column(String(1000), nullable=True)  # comma separated list
    required_branch = Column(String(255), nullable=True)
    
    job = relationship("Job", back_populates="requirements")
