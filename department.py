import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    
    students = relationship("Student", back_populates="department")
    subjects = relationship("Subject", back_populates="department")
