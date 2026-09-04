import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    credits = Column(Integer, nullable=False)
    
    subjects = relationship("Subject", back_populates="course", cascade="all, delete-orphan")
