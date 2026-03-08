"""
Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated configuration
with automatic .env file loading.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

env_state = os.getenv("ENVIRONMENT", "development")
env_files = (".env", f".env.{env_state}")


class Settings(BaseSettings):
    """
    Central configuration for the Opportunity Navigator backend.
    Values are loaded from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=env_files,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # --- Bright Data API ---
    bright_data_api_key: str = ""
    bright_data_dataset_id: str = ""

    # --- Google Gemini API ---
    gemini_api_key: str = ""

    # --- Application Settings ---
    environment: str = "development"
    frontend_origin: str = "http://localhost:8080,http://localhost:5173,http://localhost:3000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated origins into a list for CORS middleware."""
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    @property
    def is_bright_data_configured(self) -> bool:
        """Check if Bright Data credentials are provided."""
        return bool(self.bright_data_api_key and self.bright_data_dataset_id)

    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API key is provided."""
        return bool(self.gemini_api_key)


# Singleton settings instance
settings = Settings()
