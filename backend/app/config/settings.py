"""
Application environment variables configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"
    database_url: str = "sqlite:///./compliance_sentinel.db"
    demo_mode: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CCS_",
        extra="ignore",
    )


settings = Settings()
