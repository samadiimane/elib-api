# app/core/config.py  (pydantic v2)
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./dev.db", alias="DATABASE_URL")

    # Accept either '["http://a","http://b"]' or 'http://a,http://b'
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )
    default_locale: str = Field(default="en", alias="DEFAULT_LOCALE")

    # storage
    storage_endpoint: str = Field(default="http://127.0.0.1:9000", alias="STORAGE_ENDPOINT")
    storage_bucket: str = Field(default="documents", alias="STORAGE_BUCKET")
    storage_access_key: str = Field(default="minio", alias="STORAGE_ACCESS_KEY")
    storage_secret_key: str = Field(default="minio12345", alias="STORAGE_SECRET_KEY")
    storage_region: str = Field(default="us-east-1", alias="STORAGE_REGION")
    storage_public_endpoint: str | None = Field(default=None, alias="STORAGE_PUBLIC_ENDPOINT")
    # Optional: if i ever want to build absolute public URLs (we’ll use presigned instead)
    storage_cdn_base: str | None = Field(default=None, alias="STORAGE_CDN_BASE")

    # auth
    auth_secret: str = Field(default="change-me", alias="AUTH_SECRET")
    access_token_exp_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXP_MINUTES")

    # external services
    rag_api_url: str = Field(default="http://rag-api:8001", alias="RAG_API_URL")

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

    @field_validator("default_locale")
    @classmethod
    def normalize_default_locale(cls, v: str) -> str:
        return (v or "en").strip().lower()

    @field_validator("storage_public_endpoint", "storage_cdn_base", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if v is None:
            return None
        value = str(v).strip()
        return value or None

settings = Settings()


if settings.database_url.startswith("sqlite:///./"):
    db_file = Path(__file__).resolve().parent.parent.parent / "dev.db"
    settings.database_url = f"sqlite:///{db_file.as_posix()}"
