"""Application configuration using Pydantic Settings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AI Life Insurance Sales Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = (
        "postgresql+asyncpg://lic_agent:lic_agent_password@localhost:5432/lic_agent_dev"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    session_ttl: int = 3600

    # LLM Configuration
    llm_provider: str = "ollama"
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

    @field_validator("encryption_key", "jwt_secret_key")
    @classmethod
    def validate_secret_length(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("Must be at least 32 characters long.")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        allowed_prefixes = (
            "postgresql+asyncpg://",
            "sqlite+aiosqlite://",
        )
        if not value:
            raise ValueError("database_url cannot be empty.")
        if not value.startswith(allowed_prefixes):
            raise ValueError(
                "database_url must use one of the supported async drivers "
                "(postgresql+asyncpg or sqlite+aiosqlite)."
            )
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if not value.startswith(("redis://", "rediss://")):
            raise ValueError("redis_url must start with redis:// or rediss://.")
        return value


settings = Settings()

__all__ = ["Settings", "settings"]
