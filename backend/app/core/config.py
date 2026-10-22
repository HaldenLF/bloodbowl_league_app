from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", hide_input_in_errors=True)
    
    database_url: str 
    jwt_secret: SecretStr = Field(min_length=32)
    access_token_minutes: int = Field(default=1440, ge=1)

settings = Settings()
