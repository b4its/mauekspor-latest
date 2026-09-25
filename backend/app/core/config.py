import ast
import json
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
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
    cors_origins: list[str] | str = [
        "http://localhost:5188",
        "http://127.0.0.1:5188",
        "http://localhost:3015",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: Any) -> list[str]:
        default_origins = [
            "http://localhost:5188",
            "http://127.0.0.1:5188",
            "http://localhost:3015",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        if isinstance(v, str):
            v = v.strip()
            # Bersihkan tanda kutip pembungkus jika ada (mis. dari Make/shell/env: '["..."]' atau "['...']")
            while (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                v = v[1:-1].strip()
            if not v:
                return default_origins
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        items = [str(item).strip() for item in parsed if str(item).strip()]
                        return items if items else default_origins
                except Exception:
                    try:
                        parsed = ast.literal_eval(v)
                        if isinstance(parsed, (list, tuple, set)):
                            items = [str(item).strip() for item in parsed if str(item).strip()]
                            return items if items else default_origins
                    except Exception:
                        pass
            items = [item.strip().strip("'\"") for item in v.strip("[]").split(",") if item.strip().strip("'\"")]
            return items if items else default_origins
        if isinstance(v, (list, tuple, set)):
            items = [str(item).strip() for item in v if str(item).strip()]
            return items if items else default_origins
        return default_origins
    seed_admin_email: str = "admin@mauekspor.example"
    seed_admin_password: str = "admin123"
    seed_exporter_email: str = "rizal@kopigayo.example"
    seed_exporter_password: str = "rizal123"
    # Currency configuration: base = mata uang input biaya (default IDR),
    # display = mata uang output harga (default IDR, bisa USD/EUR/JPY/dll)
    base_currency: str = "IDR"
    display_currency: str = "IDR"
    fallback_rate: float = 1.0  # base→display fallback rate (IDR→IDR = 1.0)
    # Lingkungan deploy: "development" (default) atau "production".
    # Di production, secret default / password seed default akan MENGHENTIKAN boot.
    environment: str = "development"
    # Set MAUEKSPOR_ALLOW_INSECURE_DEFAULTS=1 untuk menonaktifkan fail-fast
    # (mis. CI/demo yang sengaja memakai default).
    allow_insecure_defaults: bool = False
    # Iterasi PBKDF2-HMAC-SHA256 untuk hashing password. Default 100_000 (kuat,
    # sesuai OWASP). Test suite menurunkannya via MAUEKSPOR_PBKDF2_ITERATIONS=1
    # agar login tidak memakan ~3.5s per hash (320 test × banyak login = ~10 menit).
    # Nilai ini TIDAK boleh diturunkan di production.
    pbkdf2_iterations: int = 100_000

    @model_validator(mode="after")
    def _guard_default_secret(self) -> "Settings":
        """Fail-fast di production bila secret/password masih default.

        Secret default menandatangani semua JWT (PEPPER = secret_key) → siapa pun
        bisa memalsukan token Admin. Sebelumnya hanya di-log (fail-open).
        """
        is_prod = self.environment.strip().lower() in {"production", "prod"}
        weak_secret = self.secret_key in {"", "change-me-in-production"}
        weak_seed = self.seed_admin_password in {"", "admin123"}
        # Iterasi PBKDF2 terlalu rendah melemahkan hashing password (brute-force).
        # Test/dev boleh rendah; production wajib kuat.
        weak_pbkdf2 = self.pbkdf2_iterations < 50_000
        if is_prod and (weak_secret or weak_seed or weak_pbkdf2) and not self.allow_insecure_defaults:
            problems = []
            if weak_secret:
                problems.append("MAUEKSPOR_SECRET_KEY")
            if weak_seed:
                problems.append("MAUEKSPOR_SEED_ADMIN_PASSWORD")
            if weak_pbkdf2:
                problems.append(
                    f"MAUEKSPOR_PBKDF2_ITERATIONS ({self.pbkdf2_iterations} < 50000)"
                )
            raise RuntimeError(
                "Refusing to start in production with insecure defaults: "
                + ", ".join(problems)
                + ". Set nilai acak yang kuat, atau MAUEKSPOR_ALLOW_INSECURE_DEFAULTS=1 untuk menonaktifkan guard ini."
            )
        if weak_secret:
            import logging
            logging.getLogger("mauekspor.config").warning(
                "MAUEKSPOR_SECRET_KEY masih default! Set variabel lingkungan MAUEKSPOR_SECRET_KEY "
                "ke nilai acak yang kuat sebelum deploy ke production."
            )
        return self


settings = Settings()
