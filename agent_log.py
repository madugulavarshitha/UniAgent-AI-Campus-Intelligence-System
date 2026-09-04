import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.database.connection import Base

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    trace_json = Column(Text, nullable=True)  # Store step JSON arrays
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
