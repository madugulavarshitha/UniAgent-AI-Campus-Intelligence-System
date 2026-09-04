from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.api.dependencies import get_current_user, get_current_student
from app.models.student import Student
from app.crud.agent import (
    get_conversations_by_user, 
    get_conversation, 
    create_conversation, 
    add_message_to_conversation
)
from app.schemas.agent import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationDetailResponse, 
    MessageCreate, 
    MessageResponse
)
from app.models.user import User
from app.models.agent_history import AgentMessage
from app.services.agent_orchestrator import agent_orchestrator

router = APIRouter(prefix="/agent", tags=["agent"])

@router.get("/conversations", response_model=List[ConversationResponse])
def read_conversations(
    agent_type: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_conversations_by_user(db, user.id, agent_type)

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def start_conversation(
    conv_in: ConversationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_conversation(db, user.id, conv_in)

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def read_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    return conv

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: str,
    msg_in: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
    add_message_to_conversation(
        db, 
        conversation_id=conversation_id, 
        sender="user", 
        content=msg_in.content
    )
    
    all_msgs = db.query(AgentMessage).filter(
        AgentMessage.conversation_id == conversation_id
    ).order_by(AgentMessage.created_at.asc()).all()
    
    history = []
    for m in all_msgs:
        history.append({
            "role": "user" if m.sender == "user" else "model",
            "content": m.content
        })
        
    result = agent_orchestrator.run_query(
        db=db,
        user_id=user.id,
        messages=history,
        agent_type=conv.agent_type
    )
    
    db_msg = add_message_to_conversation(
        db,
        conversation_id=conversation_id,
        sender="assistant",
        content=result["response"],
        model_name="gemini-1.5-flash",
        metadata_json={"thoughts": result["thoughts"]}
    )
    
    return db_msg

@router.get("/academic-insights")
def get_academic_insights(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    history = [
        {"role": "user", "content": "Analyze my academic performance and attendance logs. Highlight warnings and suggest remediation steps."}
    ]
    result = agent_orchestrator.run_query(
        db=db,
        user_id=student.user_id,
        messages=history,
        agent_type="academic"
    )
    return {"insights": result["response"]}

