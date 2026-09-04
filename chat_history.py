import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.database.connection import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(50), nullable=False)  # advisor, mentor, researcher, rag
    messages_json = Column(Text, nullable=False)  # JSON text blob of messages
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
