from pathlib import Path

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
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    seed_admin_email: str = "admin@mauekspor.example"
    seed_admin_password: str = "admin123"
    seed_exporter_email: str = "rizal@kopigayo.example"
    seed_exporter_password: str = "rizal123"


settings = Settings()
