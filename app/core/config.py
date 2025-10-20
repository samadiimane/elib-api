# app/core/config.py  (pydantic v2)
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./dev.db", alias="DATABASE_URL")

    # Accept either '["http://a","http://b"]' or 'http://a,http://b'
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, list):
            return v
        if not v:
            return []
        s = str(v).strip()
        if s.startswith("["):
            import json
            try:
                arr = json.loads(s)
                return [str(x).strip() for x in arr if str(x).strip()]
            except Exception:
                # fall back to CSV
                pass
        return [x.strip() for x in s.split(",") if x.strip()]

settings = Settings()
