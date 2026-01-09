from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings with production-ready defaults"""
    
    # API Keys
    groq_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    hf_token: str = ""
    
    # Model Configuration
    llm_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Qdrant Configuration
    collection_name: str = "research_papers"
    
    # Server Configuration
    port: int = int(os.getenv("PORT", 8000))
    host: str = "0.0.0.0"
    
    # CORS Configuration (will be updated after frontend deployment)
    cors_origins: str = "*"
    
    # Application Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()