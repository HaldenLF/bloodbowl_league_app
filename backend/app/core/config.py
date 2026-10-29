from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, model_validator
from pathlib import Path
from typing import Literal

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", hide_input_in_errors=True)
    
    environment: Literal["development", "production"] = "development"
    database_url: str 
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_minutes: int = Field(default=1440, ge=1)
    cors_origins: list[str] = []
    test_database_url: str | None = None
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def no_wildcard_cors_in_production(self):
        if self.is_production and "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must list exact origins in production, never *")
        return self

settings = Settings()
