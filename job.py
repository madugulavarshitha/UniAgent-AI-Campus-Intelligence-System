import uuid
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    salary = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    vacancies = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    company = relationship("Company", back_populates="jobs")
    requirements = relationship("JobRequirement", back_populates="job", uselist=False, cascade="all, delete-orphan")
