"""
KRISHIVA AI — Central Configuration Management
Provides typed environment configuration using Pydantic Settings.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "KRISHIVA AI"
    APP_VERSION: str = "1.0.0"
    ENV: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database Configuration (PostgreSQL primary, SQLite local fallback)
    DATABASE_URL: str = "sqlite:///./krishiva_local.db"
    DB_ECHO: bool = False

    # Google Gemini AI Integration
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"

    # Agricultural Market Data
    DATA_GOV_IN_API_KEY: Optional[str] = None
    ENAM_BASE_URL: str = "https://enam.gov.in/web/trading-details"

    # Weather Providers
    WEATHER_PROVIDER: str = "open-meteo"
    WEATHER_API_KEY: Optional[str] = None

    # Paths
    DATA_RAW_DIR: str = "data/raw"
    DATA_PROCESSED_DIR: str = "data/processed"
    DATA_REFERENCE_DIR: str = "data/reference"
    MODELS_DIR: str = "models/saved"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
