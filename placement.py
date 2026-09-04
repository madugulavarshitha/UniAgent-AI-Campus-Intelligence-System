import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from app.database.connection import Base

class PlacementJob(Base):
    __tablename__ = "placement_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)  # Comma-separated skills
    min_cgpa = Column(Float, default=0.0)
    vacancies = Column(Integer, default=1)
    package_details = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
