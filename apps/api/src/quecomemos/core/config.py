"""Application settings, loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed configuration. Never holds defaults for real secrets."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "quecomemos-api"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str
    test_database_url: str | None = None

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7

    allowed_origins: str = "http://localhost:5175"

    storage_endpoint_url: str | None = None
    storage_public_url: str | None = None
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket: str = "quecomemos-media"
    storage_region: str = "auto"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so settings are parsed once per process."""
    return Settings()
