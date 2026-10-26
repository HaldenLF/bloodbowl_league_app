from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", hide_input_in_errors=True)
    
    database_url: str 
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_minutes: int = Field(default=1440, ge=1)
    test_database_url: str | None = None


settings = Settings()
