"""
Guest mode API routes - No authentication required
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from services.ai_service import AIService
from services.writing_prompts import writing_prompts_service
from core.age_groups import AgeGroup

router = APIRouter(prefix="/guest", tags=["guest"])

# Pydantic models for guest mode
class GuestWritingAssistanceRequest(BaseModel):
    text: str
    assistance_type: str  # "improve", "continue", "summarize", "analyze"
    age_group: Optional[str] = "high_school"  # Allow age group selection

class GuestWritingAssistanceResponse(BaseModel):
    result: str
    suggestions: Optional[List[str]] = None
    age_group: str

class GuestWritingPromptsRequest(BaseModel):
    project_name: str = "My Writing Project"
    age_group: Optional[str] = "high_school"  # Allow age group selection

class GuestWritingPromptsResponse(BaseModel):
    prompts: List[dict]
    theme: Optional[str] = None
    age_group: str
    project_name: str

@router.get("/health")
async def guest_health_check():
    """Health check for guest mode"""
    return {"status": "Guest mode available", "age_group": "high_school"}

@router.post("/writing-assistance", response_model=GuestWritingAssistanceResponse)
async def guest_writing_assistance(request: GuestWritingAssistanceRequest):
    """Get writing assistance for guest users (no authentication required)"""
    try:
        ai_service = AIService()

        # Use selected age group or default to high school
        age_group = request.age_group or AgeGroup.HIGH_SCHOOL.value

        result = ai_service.writing_assistance(
            text=request.text,
            assistance_type=request.assistance_type,
            user_age_group=age_group
        )

        return GuestWritingAssistanceResponse(
            result=result.get("result", ""),
            suggestions=result.get("suggestions", []),
            age_group=age_group
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

@router.post("/writing-prompts", response_model=GuestWritingPromptsResponse)
async def guest_writing_prompts(request: GuestWritingPromptsRequest):
    """Get writing prompts for guest users (no authentication required)"""
    try:
        # Use selected age group or default to high school
        age_group = request.age_group or AgeGroup.HIGH_SCHOOL.value

        prompts_data = writing_prompts_service.get_writing_prompts(
            project_name=request.project_name,
            age_group=age_group
        )

        return GuestWritingPromptsResponse(
            prompts=prompts_data["prompts"],
            theme=prompts_data["theme"],
            age_group=age_group,
            project_name=request.project_name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving writing prompts: {str(e)}"
        )

@router.get("/age-groups")
async def guest_age_groups():
    """Get available age groups for guest users (informational only)"""
    try:
        from core.age_groups import AgeGroupConfig
        age_groups = AgeGroupConfig.get_all_age_groups()
        
        return {
            "age_groups": age_groups,
            "guest_age_group": AgeGroup.HIGH_SCHOOL.value,
            "guest_age_group_name": "High School (Ages 17-18)",
            "note": "Guest mode uses High School level suggestions. Register to access age-appropriate content.",
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving age groups: {str(e)}"
        )

@router.get("/demo-content")
async def guest_demo_content():
    """Get demo content for guest users to try"""
    return {
        "demo_projects": [
            {
                "name": "Adventure Story",
                "description": "Write an exciting adventure tale",
                "sample_text": "The old map crackled in my hands as I studied the mysterious symbols..."
            },
            {
                "name": "Science Fiction",
                "description": "Create a futuristic story",
                "sample_text": "The year was 2150, and humanity had just discovered..."
            },
            {
                "name": "Mystery Novel",
                "description": "Craft a thrilling mystery",
                "sample_text": "Detective Sarah noticed something odd about the crime scene..."
            },
            {
                "name": "Fantasy Epic",
                "description": "Build a magical world",
                "sample_text": "The ancient dragon's eyes glowed as it spoke the forgotten words..."
            }
        ],
        "tips": [
            "Try different writing assistance types: improve, continue, analyze",
            "Use writing prompts to get started when you're stuck",
            "Guest mode provides high school level suggestions",
            "Register for age-appropriate content and to save your work"
        ]
    }
