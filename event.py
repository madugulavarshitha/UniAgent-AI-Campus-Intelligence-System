import uuid
import datetime
from sqlalchemy import Column, String, DateTime
from app.database.connection import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
