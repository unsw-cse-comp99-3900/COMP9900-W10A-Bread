"""
Database models for Writingway
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    birth_date = Column(Date, nullable=True)  # Birth date for calculating age group
    age_group = Column(String(20), nullable=True)  # Age group identifier, e.g. 'early_primary'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

    def get_current_age_group(self):
        """Get current age group"""
        if self.birth_date:
            from core.age_groups import AgeGroupConfig
            return AgeGroupConfig.get_age_group_by_birth_date(self.birth_date)
        return None

    def update_age_group(self):
        """Update age group field"""
        current_age_group = self.get_current_age_group()
        if current_age_group:
            self.age_group = current_age_group.value

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    cover_image = Column(String(500))  # URL or file path
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    compendium_entries = relationship("CompendiumEntry", back_populates="project")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    document_type = Column(String(50), default="scene")  # scene, chapter, character, etc.
    order_index = Column(Integer, default=0)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("documents.id"))  # For hierarchical structure
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    parent = relationship("Document", remote_side=[id])
    children = relationship("Document")

class CompendiumEntry(Base):
    __tablename__ = "compendium_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    entry_type = Column(String(50))  # character, location, item, etc.
    tags = Column(JSON)  # List of tags
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="compendium_entries")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme = Column(String(50), default="light")
    language = Column(String(10), default="en")
    font_size = Column(Integer, default=14)
    auto_save = Column(Boolean, default=True)
    ai_settings = Column(JSON)  # AI provider preferences, API keys, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    messages = Column(JSON)  # List of conversation messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
