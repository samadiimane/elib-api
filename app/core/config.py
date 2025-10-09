# app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Dev default: local SQLite file (no install needed)
    DATABASE_URL: str = Field(default="sqlite:///./dev.db")

settings = Settings()
