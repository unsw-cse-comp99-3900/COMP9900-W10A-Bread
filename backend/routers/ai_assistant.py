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
from core.age_groups import AgeGroupConfig
from services.writing_prompts import writing_prompts_service

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
    age_group: Optional[str] = None  # Age group for age-appropriate suggestions

class WritingAssistanceResponse(BaseModel):
    result: str
    suggestions: Optional[List[str]] = None
    age_group: Optional[str] = None

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
        
        # Get AI response using intelligent model selection
        response = ai_service.chat(
            messages=messages,
            context=request.context,
            task_type='chat'
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
    """Get age-appropriate writing assistance from AI"""
    try:
        ai_service = AIService()

        # Use user's age group if not provided in request
        user_age_group = request.age_group or current_user.age_group

        result = ai_service.writing_assistance(
            text=request.text,
            assistance_type=request.assistance_type,
            user_age_group=user_age_group
        )

        return WritingAssistanceResponse(
            result=result.get("result", ""),
            suggestions=result.get("suggestions", []),
            age_group=result.get("age_group")
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

@router.get("/age-groups")
async def get_age_groups():
    """Get all available age groups"""
    try:
        age_groups = AgeGroupConfig.get_all_age_groups()
        return {
            "age_groups": age_groups,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving age groups: {str(e)}"
        )

@router.get("/writing-prompts/{project_id}")
async def get_writing_prompts(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get age-appropriate writing prompts for a project"""
    try:
        # Get project information
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Get writing prompts based on project name and user's age group
        prompts_data = writing_prompts_service.get_writing_prompts(
            project_name=project.name,
            age_group=current_user.age_group
        )

        return {
            "prompts": prompts_data["prompts"],
            "theme": prompts_data["theme"],
            "age_group": prompts_data["age_group"],
            "project_name": prompts_data["project_name"],
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving writing prompts: {str(e)}"
        )
