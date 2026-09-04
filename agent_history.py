import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base

class AgentConversation(Base):
    __tablename__ = "agent_conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(50), nullable=False)  # academic, career, project, rag, orchestrator
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    messages = relationship("AgentMessage", back_populates="conversation", cascade="all, delete-orphan")


class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("agent_conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(String, nullable=False)
    model_name = Column(String(100), nullable=True)
    metadata_json = Column(JSON, nullable=True)  # To capture thoughts, citations, tools used, etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    conversation = relationship("AgentConversation", back_populates="messages")
