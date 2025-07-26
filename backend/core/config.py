"""
Configuration settings for the Writingway backend
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./writingway.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Services
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Multiple Gemini API Keys for rotation
    gemini_api_key_1: Optional[str] = None
    gemini_api_key_2: Optional[str] = None
    gemini_api_key_3: Optional[str] = None
    gemini_api_key_4: Optional[str] = None
    gemini_api_key_5: Optional[str] = None
    gemini_api_key_6: Optional[str] = None
    gemini_api_key_7: Optional[str] = None
    gemini_api_key_8: Optional[str] = None
    gemini_api_key_9: Optional[str] = None
    gemini_api_key_10: Optional[str] = None
    
    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"  # Allow extra fields for dynamic API keys
    )

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
