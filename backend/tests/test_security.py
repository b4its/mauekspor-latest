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


def test_rate_limit_key_pakai_x_forwarded_for():
    """Di belakang ngrok/nginx, tiap user asli (XFF) harus punya kuota sendiri.

    Bug: semua user tunnel share IP proxy → login ke-2 langsung 429 massal.
    """
    from app.main import _rate_limit_key

    class FakeRequest:
        def __init__(self, headers, client_host="10.0.0.1"):
            self.headers = headers
            self.client = type("C", (), {"host": client_host})()

    # XFF ada → pakai IP klien asli (hop pertama)
    r = FakeRequest({"x-forwarded-for": "103.1.2.3, 172.18.0.5"})
    assert _rate_limit_key(r) == "103.1.2.3"

    # X-Real-Only fallback
    r2 = FakeRequest({"x-real-ip": "103.9.9.9"})
    assert _rate_limit_key(r2) == "103.9.9.9"

    # Tanpa header → IP socket
    r3 = FakeRequest({})
    assert _rate_limit_key(r3) == "10.0.0.1"

    # Dua user berbeda via tunnel → key berbeda (tidak saling blokir)
    a = FakeRequest({"x-forwarded-for": "1.1.1.1"})
    b = FakeRequest({"x-forwarded-for": "2.2.2.2"})
    assert _rate_limit_key(a) != _rate_limit_key(b)
