from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://propviz:propviz@localhost:5432/propviz"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        # Railway/Heroku inject postgres:// or postgresql:// — asyncpg needs postgresql+asyncpg://
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # ── Redis / Celery ────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # ── Storage (AWS S3 or Cloudflare R2) ────────────────────────────────────
    storage_bucket: str = "propviz-assets"
    storage_region: str = "ap-southeast-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    # Leave blank for AWS S3; set to https://<account>.r2.cloudflarestorage.com for R2
    storage_endpoint_url: str = ""
    cdn_base_url: str = ""  # e.g. https://cdn.yourapp.com

    # ── Anthropic ─────────────────────────────────────────────────────────────
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-7"

    # ── Google Gemini (free-tier alternative to Anthropic) ────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # ── Groq (free-tier alternative, fast inference) ──────────────────────────
    groq_api_key: str = ""
    groq_vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    groq_text_model: str = "llama-3.3-70b-versatile"

    # ── ElevenLabs ────────────────────────────────────────────────────────────
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel (warm, professional)

    # ── Runway Gen-4 ─────────────────────────────────────────────────────────
    runway_api_key: str = ""
    runway_video_duration: int = 5  # seconds per clip

    # ── Replicate (fallback image generation) ────────────────────────────────
    replicate_api_token: str = ""

    # ── App ───────────────────────────────────────────────────────────────────
    debug: bool = False
    secret_key: str = "change-me-in-production"
    allowed_origins: list[str] = ["http://localhost:3000"]
    max_upload_size_mb: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
