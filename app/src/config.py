"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Find project root (where .env file is located)
# This file is at app/src/config.py, so project root is 2 levels up
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "AI Life Insurance Sales Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    company_name: str = "Life Insurance Company"  # Company name for identifying company vs competitor policies
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    session_ttl: int = 3600
    
    # LLM Configuration
    llm_provider: str = "ollama"  # ollama, openai, anthropic
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    
    # Cloud LLM Providers (optional)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    
    # LLM Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500
    llm_timeout: int = 30
    
    # Voice/Audio Configuration
    voice_enabled: bool = True
    stt_provider: str = "openai"  # openai, ollama
    tts_provider: str = "openai"  # openai, elevenlabs, google
    tts_voice: str = "alloy"  # Default voice for TTS
    default_language: str = "en"  # Default language code
    
    # Security
    encryption_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # File Storage
    file_storage_path: str = "./data"
    enable_file_storage: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    enable_rate_limiting: bool = True  # Enable/disable rate limiting middleware
    
    class Config:
        env_file = str(ENV_FILE)  # Use absolute path to .env in project root
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

