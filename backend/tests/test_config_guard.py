"""Test fail-fast guard konfigurasi di production (app/core/config.py).

Fokus: secret/password/iterasi PBKDF2 yang lemah harus MENGHENTIKAN boot di
production, tapi tetap boleh di dev/test (atau saat allow_insecure_defaults=1).
"""
import pytest

from app.core.config import Settings


def _make(**overrides) -> Settings:
    base = dict(
        environment="production",
        secret_key="a-very-strong-random-secret-key-value",
        seed_admin_password="a-strong-admin-password",
        pbkdf2_iterations=100_000,
    )
    base.update(overrides)
    return Settings(**base)


def test_production_ok_dengan_konfigurasi_kuat():
    s = _make()
    assert s.environment == "production"


def test_production_tolak_secret_default():
    with pytest.raises(RuntimeError, match="MAUEKSPOR_SECRET_KEY"):
        _make(secret_key="change-me-in-production")


def test_production_tolak_password_seed_default():
    with pytest.raises(RuntimeError, match="MAUEKSPOR_SEED_ADMIN_PASSWORD"):
        _make(seed_admin_password="admin123")


def test_production_tolak_iterasi_pbkdf2_rendah():
    with pytest.raises(RuntimeError, match="MAUEKSPOR_PBKDF2_ITERATIONS"):
        _make(pbkdf2_iterations=1)


def test_production_tolak_beberapa_masalah_sekaligus():
    with pytest.raises(RuntimeError) as exc:
        _make(secret_key="change-me-in-production", seed_admin_password="admin123", pbkdf2_iterations=1)
    msg = str(exc.value)
    assert "MAUEKSPOR_SECRET_KEY" in msg
    assert "MAUEKSPOR_SEED_ADMIN_PASSWORD" in msg
    assert "MAUEKSPOR_PBKDF2_ITERATIONS" in msg


def test_allow_insecure_defaults_menonaktifkan_guard():
    s = _make(secret_key="change-me-in-production", seed_admin_password="admin123",
              pbkdf2_iterations=1, allow_insecure_defaults=True)
    assert s.environment == "production"


def test_development_boleh_pakai_default_lemah():
    # Di dev, default lemah tidak boleh menghentikan boot.
    s = Settings(environment="development", secret_key="change-me-in-production",
                 seed_admin_password="admin123", pbkdf2_iterations=1)
    assert s.pbkdf2_iterations == 1


def test_pbkdf2_iterations_dipakai_oleh_hash_password():
    """hash_password harus menghormati settings.pbkdf2_iterations."""
    from app.core import security
    from app.core.config import settings

    original = settings.pbkdf2_iterations
    try:
        # iterasi rendah -> cepat, tapi verify tetap benar (memakai salt tersimpan)
        settings.pbkdf2_iterations = 1
        stored = security.hash_password("rahasiaku", salt="fixedsalt")
        assert security.verify_password("rahasiaku", stored)
        assert not security.verify_password("salah", stored)
    finally:
        settings.pbkdf2_iterations = original


def test_cors_origins_parsing_formats():
    """cors_origins harus tahan terhadap berbagai format env var (quotes, JSON, CSV)."""
    # 1. Single quotes wrapping JSON array (seperti export Make / env file)
    s1 = Settings(cors_origins="'[\"http://host1:5188\", \"http://host2:5188\"]'")
    assert s1.cors_origins == ["http://host1:5188", "http://host2:5188"]

    # 2. Raw JSON array string
    s2 = Settings(cors_origins='["http://host1:5188", "http://host2:5188"]')
    assert s2.cors_origins == ["http://host1:5188", "http://host2:5188"]

    # 3. Python-style single quotes in list string
    s3 = Settings(cors_origins="['http://host1:5188', 'http://host2:5188']")
    assert s3.cors_origins == ["http://host1:5188", "http://host2:5188"]

    # 4. Comma-separated strings
    s4 = Settings(cors_origins="http://host1:5188, http://host2:5188")
    assert s4.cors_origins == ["http://host1:5188", "http://host2:5188"]

    # 5. Single URL string
    s5 = Settings(cors_origins="http://host1:5188")
    assert s5.cors_origins == ["http://host1:5188"]

    # 6. Empty string -> fallback default
    s6 = Settings(cors_origins="")
    assert "http://localhost:5188" in s6.cors_origins

    # 7. Direct list
    s7 = Settings(cors_origins=["http://custom:5188"])
    assert s7.cors_origins == ["http://custom:5188"]

