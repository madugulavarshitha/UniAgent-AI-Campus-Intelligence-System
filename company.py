import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, index=True, nullable=False)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
