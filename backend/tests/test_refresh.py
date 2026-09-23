"""Refresh token: rotasi, revoke di logout, dan reuse deteksi."""
from fastapi.testclient import TestClient

from app.main import app


def test_refresh_rotation_flow():
    with TestClient(app) as c:
        login = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert login.status_code == 200
        old_refresh = login.json()["meta"]["refresh_token"]

        first = c.post("/api/v1/auth/refresh/")
        assert first.status_code == 200, first.text
        new_refresh = first.json()["meta"]["refresh_token"]
        assert new_refresh != old_refresh

        second = c.post("/api/v1/auth/refresh/")
        assert second.status_code == 200, second.text

        c.cookies.clear()
        reused = c.post("/api/v1/auth/refresh/", headers={"X-Refresh-Token": old_refresh})
        assert reused.status_code == 401


def test_logout_revokes_refresh():
    with TestClient(app) as c:
        login = c.post("/api/v1/auth/login/", json={"email": "rizal@kopigayo.example", "password": "rizal123"})
        refresh = login.json()["meta"]["refresh_token"]
        assert c.post("/api/v1/auth/logout/").status_code == 200

        refreshed = c.post("/api/v1/auth/refresh/", headers={"X-Refresh-Token": refresh})
        assert refreshed.status_code == 401
        assert c.get("/api/v1/auth/me/").status_code == 401


def test_refresh_returns_fresh_access_token():
    with TestClient(app) as c:
        login = c.post("/api/v1/auth/login/", json={"email": "aya@hikari.example", "password": "buyer123"})
        access = login.json()["meta"]["access_token"]
        refreshed = c.get("/api/v1/auth/me/", headers={"Authorization": f"Bearer {access}"})
        assert refreshed.status_code == 200
        assert refreshed.json()["data"]["email"] == "aya@hikari.example"