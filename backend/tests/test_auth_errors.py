"""Test branch error & edge case pada alur auth (keamanan)."""
from fastapi.testclient import TestClient

from app.main import app


def _register(c: TestClient, email: str, name: str = "Test User"):
    return c.post(
        "/api/v1/auth/register/",
        json={
            "name": name,
            "organization": "PT Test",
            "role": "Exporter",
            "email": email,
            "password": "password123",
        },
    )


def test_login_password_salah_401():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "wrong-password"},
        )
        assert res.status_code == 401
        assert "Incorrect email or password" in res.json()["message"]


def test_login_email_tidak_terdaftar_401():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/login/",
            json={"email": "tidak-ada@example.com", "password": "password123"},
        )
        assert res.status_code == 401


def test_register_email_duplikat_409():
    with TestClient(app) as c:
        first = _register(c, "dup@mauekspor.example")
        assert first.status_code == 200
        second = _register(c, "dup@mauekspor.example")
        assert second.status_code == 409
        assert "already registered" in second.json()["message"]


def test_register_email_duplikat_admin_409():
    # email admin yang sudah ada di seed
    with TestClient(app) as c:
        res = _register(c, "admin@mauekspor.example")
        assert res.status_code == 409


def test_register_payload_tidak_lengkap_422():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/register/",
            json={"name": "X", "email": "x@y.z"},  # tanpa password
        )
        assert res.status_code == 422


def test_register_admin_code_salah_403():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/register-admin/",
            json={
                "name": "Admin Baru",
                "organization": "PT X",
                "role": "Admin",
                "email": "admin-baru@mauekspor.example",
                "password": "password123",
                "admin_code": "kode-salah",
            },
        )
        assert res.status_code == 403
        assert "admin" in res.json()["message"].lower()


def test_register_admin_fail_closed_tanpa_env(monkeypatch):
    """Tanpa MAUEKSPOR_ADMIN_CODE, tidak ada kode yang valid (fail-closed)."""
    monkeypatch.delenv("MAUEKSPOR_ADMIN_CODE", raising=False)
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/register-admin/",
            json={
                "email": "admin-x@mauekspor.example",
                "password": "password123",
                "full_name": "Admin X",
                "admin_code": "admin-bootstrap-2026",
            },
        )
        assert res.status_code == 403


def test_refresh_token_tidak_valid_401():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/refresh/",
            headers={"X-Refresh-Token": "bukan-token-valid"},
        )
        assert res.status_code == 401


def test_me_tanpa_sesi_401():
    with TestClient(app) as c:
        res = c.get("/api/v1/auth/me/")
        assert res.status_code == 401
