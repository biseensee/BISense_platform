"""Centralized application configuration.

All configuration comes from environment variables (12-factor). Never
hardcode secrets or connection strings elsewhere in the codebase — import
`get_settings()` instead. Settings are cached with `lru_cache` so the
environment is parsed once per process.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────
    app_name: str = "BI Platform"
    app_env: str = Field(default="local", pattern="^(local|staging|production)$")
    debug: bool = False
    api_prefix: str = "/api/v1"
    backend_cors_origins: list[str] = Field(default_factory=list)

    # ── Security ───────────────────────────────────────────────────────
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # ── Database ───────────────────────────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "bi_platform"
    postgres_password: str = "postgres"
    postgres_db: str = "bi_platform"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30

    # ── Redis ──────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    query_cache_ttl_seconds: int = 300

    # ── Object storage ─────────────────────────────────────────────────
    s3_endpoint_url: AnyHttpUrl | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "bi-platform-artifacts"

    # ── Observability ──────────────────────────────────────────────────
    log_level: str = "INFO"
    log_json: bool = True
    otel_exporter_otlp_endpoint: str | None = None
    prometheus_metrics_path: str = "/metrics"

    # ── Datasource secrets encryption ─────────────────────────────────
    datasource_encryption_key: str

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy DSN (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values populated from env
