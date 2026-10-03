import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "CompanyLens"
    api_v1_str: str = "/api/v1"
    environment: str = "development"
    data_mode: str = "development" # "development" | "mock" | "production"
    
    # Postgres
    database_url: str = "sqlite:///./companylens.db"
    postgres_server: Optional[str] = "localhost"
    postgres_user: Optional[str] = "companylens"
    postgres_password: Optional[str] = "companylens_secret"
    postgres_db: Optional[str] = "companylens_db"
    postgres_port: Optional[int] = 5432
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Security & Tokens
    secret_key: str = "companylens_secure_jwt_secret_key"
    nextauth_secret: Optional[str] = "companylens_nextauth_secure_secret_token_here"
    access_token_expire_minutes: int = 60
    cookie_secure: bool = False
    use_httponly_cookies: bool = True
    
    # Rate Limiting
    rate_limit_anonymous: int = 10     # 10 searches per minute
    rate_limit_authenticated: int = 30 # 30 searches per minute
    
    # External Connectors
    gst_provider_base_url: Optional[str] = None
    gst_provider_client_id: Optional[str] = None
    gst_provider_client_secret: Optional[str] = None
    gst_provider_api_key: Optional[str] = None
    
    pan_provider_base_url: Optional[str] = None
    pan_provider_client_id: Optional[str] = None
    pan_provider_client_secret: Optional[str] = None
    pan_provider_api_key: Optional[str] = None
    
    mca_data_source_url: str = "https://data.gov.in/catalog/company-master-data"
    
    financial_provider_base_url: Optional[str] = None
    financial_provider_api_key: Optional[str] = None
    
    sentry_dsn: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
