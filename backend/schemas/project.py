"""
Pydantic schemas for project-related operations
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None
    document_type: str = "scene"
    order_index: int = 0
    parent_id: Optional[int] = None

class DocumentCreate(DocumentBase):
    project_id: int

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    order_index: Optional[int] = None
    parent_id: Optional[int] = None

class DocumentResponse(DocumentBase):
    id: int
    project_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CompendiumEntryBase(BaseModel):
    title: str
    content: Optional[str] = None
    entry_type: Optional[str] = None
    tags: Optional[List[str]] = None

class CompendiumEntryCreate(CompendiumEntryBase):
    project_id: int

class CompendiumEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    entry_type: Optional[str] = None
    tags: Optional[List[str]] = None

class CompendiumEntryResponse(CompendiumEntryBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
