from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn
from typing import List, Optional

class Settings(BaseSettings):
    SERVICE_NAME: str = "DAG Service"

    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here"

 
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]


    POSTGRES_URL: PostgresDsn  

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    class Config:
        env_file = ".env"  
        env_file_encoding = "utf-8"


settings = Settings()