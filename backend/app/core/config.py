from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ATS Resume Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    
    # Or Gemini (free) ...optional
    OPENAI_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()