"""
Document management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database.models import User, Project, Document
from schemas.project import DocumentCreate, DocumentUpdate, DocumentResponse
from core.security import get_current_active_user

router = APIRouter()

def verify_project_access(project_id: int, user_id: int, db: Session) -> Project:
    """Verify user has access to the project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id,
        Project.is_active == True
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project

@router.get("/project/{project_id}", response_model=List[DocumentResponse])
async def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for a project"""
    verify_project_access(project_id, current_user.id, db)
    
    documents = db.query(Document).filter(
        Document.project_id == project_id,
        Document.is_active == True
    ).order_by(Document.order_index).all()
    
    return documents

@router.post("/", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new document"""
    verify_project_access(document.project_id, current_user.id, db)
    
    db_document = Document(
        title=document.title,
        content=document.content,
        document_type=document.document_type,
        order_index=document.order_index,
        project_id=document.project_id,
        parent_id=document.parent_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify user has access to the project
    verify_project_access(document.project_id, current_user.id, db)
    
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify user has access to the project
    verify_project_access(document.project_id, current_user.id, db)
    
    # Update fields
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document (soft delete)"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify user has access to the project
    verify_project_access(document.project_id, current_user.id, db)
    
    document.is_active = False
    db.commit()
    
    return {"message": "Document deleted successfully"}
