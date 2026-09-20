from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path absolut ke .env di dalam direktori backend, agar konfigurasi terbaca
# walau proses di-start dari direktori kerja mana pun (mis. via systemd/dokker).
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), env_prefix="MAUEKSPOR_", extra="ignore"
    )

    app_name: str = "MauEkspor API"
    api_version: str = "0.2.0"
    # Database: SQLite default untuk dev/test lokal, PostgreSQL untuk production/Docker.
    # Contoh PostgreSQL: postgresql://mauekspor:mauekspor@db:5432/mauekspor
    database_url: str = "sqlite:///./mauekspor.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = [
        "http://localhost:5188",
        "http://127.0.0.1:5188",
        "http://localhost:3015",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    seed_admin_email: str = "admin@mauekspor.example"
    seed_admin_password: str = "admin123"
    seed_exporter_email: str = "rizal@kopigayo.example"
    seed_exporter_password: str = "rizal123"

    @model_validator(mode="after")
    def _warn_default_secret(self) -> "Settings":
        """Peringatkan di log bila secret_key masih default (risiko token forgery)."""
        if self.secret_key == "change-me-in-production":
            import logging
            logging.getLogger("mauekspor.config").warning(
                "MAUEKSPOR_SECRET_KEY masih default! Set variabel lingkungan MAUEKSPOR_SECRET_KEY "
                "ke nilai acak yang kuat sebelum deploy ke production."
            )
        return self


settings = Settings()
