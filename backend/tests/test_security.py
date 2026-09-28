"""Test security helpers: hashing password & token JWT-like (app/core/security.py)."""
import time
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.core import security


def test_hash_verify_password():
    stored = security.hash_password("password123")
    assert "$" in stored
    assert security.verify_password("password123", stored)
    assert not security.verify_password("salah", stored)


def test_hash_password_salt_konsisten():
    stored = security.hash_password("pass", salt="fixed-salt")
    assert security.verify_password("pass", stored)
    # salt yang sama -> hash sama
    assert security.hash_password("pass", "fixed-salt") == stored


def test_verify_password_format_salah_false():
    assert not security.verify_password("pass", "tanpa-dolar")
    assert not security.verify_password("pass", "")


def test_create_and_decode_access_token():
    token = security.create_token("U-1", "Admin")
    payload = security.decode_token(token)
    assert payload["sub"] == "U-1"
    assert payload["role"] == "Admin"
    assert payload["type"] == "access"


def test_create_refresh_token_expiry_lebih_lama():
    access = security.decode_token(security.create_token("U-1", "Admin", token_type="access"))
    refresh = security.decode_token(security.create_token("U-1", "Admin", token_type="refresh"))
    assert refresh["exp"] > access["exp"]


def test_decode_token_signature_salah_401():
    token = security.create_token("U-1", "Admin")
    tampered = token[:-3] + ("abc" if not token.endswith("abc") else "def")
    with pytest.raises(HTTPException) as exc:
        security.decode_token(tampered)
    assert exc.value.status_code == 401


def test_decode_token_kedaluwarsa_401():
    token = security.create_token("U-1", "Admin", expire_minutes=-1)
    with pytest.raises(HTTPException) as exc:
        security.decode_token(token)
    assert exc.value.status_code == 401


def test_decode_token_malformed_401():
    with pytest.raises(HTTPException):
        security.decode_token("bukan-token")


def test_create_access_refresh_token_dari_user():
    access = security.create_access_token({"id": "U-1", "role": "UMKM"})
    refresh = security.create_refresh_token({"id": "U-1", "role": "UMKM"})
    assert security.decode_token(access)["type"] == "access"
    assert security.decode_token(refresh)["type"] == "refresh"


def test_b64url_roundtrip():
    assert security._b64url_decode(security._b64url(b"hello")) == b"hello"
    assert security._b64url(b"") == ""


class _FakeRequest:
    def __init__(self, cookie=None):
        self.cookies = {"access_token": cookie} if cookie else {}


def test_get_token_dari_bearer():
    req = _FakeRequest()
    class Cred:
        scheme = "bearer"
        credentials = "TOKEN-BEARER"
    assert security.get_token(req, Cred()) == "TOKEN-BEARER"


def test_get_token_dari_cookie():
    req = _FakeRequest(cookie="TOKEN-COOKIE")
    assert security.get_token(req, None) == "TOKEN-COOKIE"


def test_get_token_tanpa_apapun_401():
    req = _FakeRequest()
    with pytest.raises(HTTPException) as exc:
        security.get_token(req, None)
    assert exc.value.status_code == 401


def _fake_request(headers):
    class FakeRequest:
        def __init__(self, hdrs, client_host="10.0.0.1"):
            self.headers = hdrs
            self.client = type("C", (), {"host": client_host})()

    return FakeRequest(headers)


def test_rate_limit_key_default_tidak_percaya_proxy(monkeypatch):
    """Default fail-safe (PRD NFR-SEC-1): X-Real-IP DIABAIKAN kecuali diaktifkan.

    Tanpa ini, backend yang terekspos langsung bisa dibypass rate-limit dengan
    memalsukan header X-Real-IP.
    """
    from app.main import _rate_limit_key

    monkeypatch.delenv("MAUEKSPOR_TRUST_PROXY", raising=False)
    spoofed = _fake_request({"x-real-ip": "103.1.2.3"})
    assert _rate_limit_key(spoofed) == "10.0.0.1"


def test_rate_limit_key_pakai_x_real_ip_saat_proxy_tepercaya(monkeypatch):
    """Di belakang proxy tepercaya (MAUEKSPOR_TRUST_PROXY=1), tiap user punya kuota.

    Bug lama: semua user tunnel share IP proxy → login ke-2 langsung 429 massal.
    """
    from app.main import _rate_limit_key

    monkeypatch.setenv("MAUEKSPOR_TRUST_PROXY", "1")

    # X-Real-IP dipercaya
    r = _fake_request({"x-real-ip": "103.1.2.3"})
    assert _rate_limit_key(r) == "103.1.2.3"

    # XFF sendirian (tanpa X-Real-IP) TIDAK dipercaya → IP socket
    r2 = _fake_request({"x-forwarded-for": "103.9.9.9, 172.18.0.5"})
    assert _rate_limit_key(r2) == "10.0.0.1"

    # Dua user berbeda via tunnel → key berbeda (tidak saling blokir)
    a = _fake_request({"x-real-ip": "1.1.1.1"})
    b = _fake_request({"x-real-ip": "2.2.2.2"})
    assert _rate_limit_key(a) != _rate_limit_key(b)


def test_csrf_wajib_untuk_mutasi_berbasis_cookie(monkeypatch):
    """PRD FR-AUTH-1: cookie-based mutation tanpa X-CSRF-Token harus 403.

    Bearer (jalur utama menuju API) tidak terpengaruh. Di dev/test CSRF default
    nonaktif (ergonomis), jadi paksa aktif di sini.
    """
    monkeypatch.setenv("MAUEKSPOR_ENABLE_CSRF", "1")
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        # Login untuk dapat cookie access_token.
        r = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert r.status_code == 200
        token = r.json()["meta"]["access_token"]
        assert c.cookies.get("access_token")

        # Cookie saja (tanpa Bearer, tanpa CSRF) → ditolak 403.
        blocked = c.post("/api/v1/products/", json={"name": "CSRF Test", "category": "Food", "origin": "ID"})
        assert blocked.status_code == 403

        # Dengan Bearer → lolos (tidak kena CSRF).
        ok = c.post(
            "/api/v1/products/",
            json={"name": "Bearer OK", "category": "Food", "origin": "ID"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert ok.status_code == 200

        # Dengan cookie + token CSRF valid → lolos.
        csrf = c.get("/api/v1/auth/csrf/").json()["data"]["csrf_token"]
        ok2 = c.post(
            "/api/v1/products/",
            json={"name": "CSRF OK", "category": "Food", "origin": "ID"},
            headers={"X-CSRF-Token": csrf},
        )
        assert ok2.status_code == 200


def test_csrf_aktif_otomatis_di_production(monkeypatch):
    """Di production cookie-based mutation wajib CSRF walau flag tidak diset."""
    monkeypatch.delenv("MAUEKSPOR_ENABLE_CSRF", raising=False)
    monkeypatch.setenv("MAUEKSPOR_ENVIRONMENT", "production")
    # Rebuild settings agar environment terbaca ulang.
    from app.core import config as cfg
    cfg.settings.environment = "production"
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as c:
            r = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
            assert r.status_code == 200
            blocked = c.post("/api/v1/tasks/", json={"title": "prod csrf"})
            assert blocked.status_code == 403
    finally:
        cfg.settings.environment = "development"
