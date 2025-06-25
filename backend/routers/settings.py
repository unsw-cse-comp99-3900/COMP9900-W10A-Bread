"""
User settings routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from database.database import get_db
from database.models import User, UserSettings
from core.security import get_current_active_user

router = APIRouter()

class SettingsResponse(BaseModel):
    theme: str
    language: str
    font_size: int
    auto_save: bool
    ai_settings: Optional[Dict[str, Any]] = None

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    font_size: Optional[int] = None
    auto_save: Optional[bool] = None
    ai_settings: Optional[Dict[str, Any]] = None

@router.get("/", response_model=SettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SettingsResponse(
        theme=settings.theme,
        language=settings.language,
        font_size=settings.font_size,
        auto_save=settings.auto_save,
        ai_settings=settings.ai_settings
    )

@router.put("/", response_model=SettingsResponse)
async def update_user_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update fields
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return SettingsResponse(
        theme=settings.theme,
        language=settings.language,
        font_size=settings.font_size,
        auto_save=settings.auto_save,
        ai_settings=settings.ai_settings
    )
