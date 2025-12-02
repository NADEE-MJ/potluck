"""Application configuration and settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    admin_password: str
    secret_key: str
    database_url: str = "sqlite:///./potluck.db"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
