from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    project_name: str = "AI Government Exam OS"
    api_v1_str: str = "/api/v1"
    
    # Postgres
    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    database_url: str
    
    # Redis
    redis_host: str
    redis_port: int
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cookie_secure: bool = False # False for local development
    use_httponly_cookies: bool = True
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
