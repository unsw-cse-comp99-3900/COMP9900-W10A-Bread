"""
AI Assistant routes for writing assistance
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database.database import get_db
from database.models import User, Project, Document, AIConversation
from core.security import get_current_active_user
from services.ai_service import AIService

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None
    document_id: Optional[int] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

class WritingAssistanceRequest(BaseModel):
    text: str
    assistance_type: str  # "improve", "continue", "summarize", "analyze"
    project_id: Optional[int] = None

class WritingAssistanceResponse(BaseModel):
    result: str
    suggestions: Optional[List[str]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with AI assistant"""
    try:
        ai_service = AIService()
        
        # Get or create conversation
        conversation = None
        if request.project_id:
            conversation = db.query(AIConversation).filter(
                AIConversation.user_id == current_user.id,
                AIConversation.project_id == request.project_id
            ).first()
        
        if not conversation:
            conversation = AIConversation(
                user_id=current_user.id,
                project_id=request.project_id,
                document_id=request.document_id,
                messages=[]
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Add user message to conversation
        messages = conversation.messages or []
        messages.append({"role": "user", "content": request.message})
        
        # Get AI response
        response = ai_service.chat(
            messages=messages,
            context=request.context
        )
        
        # Add AI response to conversation
        messages.append({"role": "assistant", "content": response})
        conversation.messages = messages
        
        db.commit()
        
        return ChatResponse(response=response, conversation_id=conversation.id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

@router.post("/writing-assistance", response_model=WritingAssistanceResponse)
async def get_writing_assistance(
    request: WritingAssistanceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get writing assistance from AI"""
    try:
        ai_service = AIService()
        
        result = ai_service.writing_assistance(
            text=request.text,
            assistance_type=request.assistance_type
        )
        
        return WritingAssistanceResponse(
            result=result.get("result", ""),
            suggestions=result.get("suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

@router.get("/conversations/{project_id}")
async def get_conversation_history(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get conversation history for a project"""
    conversation = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id,
        AIConversation.project_id == project_id
    ).first()
    
    if not conversation:
        return {"messages": []}
    
    return {"messages": conversation.messages or []}

@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear conversation history"""
    conversation = db.query(AIConversation).filter(
        AIConversation.id == conversation_id,
        AIConversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.messages = []
    db.commit()
    
    return {"message": "Conversation cleared successfully"}
