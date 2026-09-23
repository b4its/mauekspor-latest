"""RBAC: hanya role tertentu yang boleh memodifikasi/membaca resource aria tertentu."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient, email: str, password: str, expected=200):
    res = c.post("/api/v1/auth/login/", json={"email": email, "password": password})
    assert res.status_code == expected, res.text
    return res


def test_buyer_cannot_create_product():
    with TestClient(app) as c:
        _login(c, "aya@hikari.example", "buyer123")
        res = c.post(
            "/api/v1/products/",
            json={"name": "Nope", "category": "Food", "origin": "ID"},
        )
        assert res.status_code == 403
        assert "cannot modify" in res.json()["message"]


def test_exporter_can_create_product_but_not_read_users():
    with TestClient(app) as c:
        _login(c, "rizal@kopigayo.example", "rizal123")
        res = c.post(
            "/api/v1/products/",
            json={"name": "Allowed", "category": "Food", "origin": "ID"},
        )
        assert res.status_code == 200, res.text
        blocked = c.get("/api/v1/users/")
        assert blocked.status_code == 403


def test_admin_can_read_users():
    with TestClient(app) as c:
        _login(c, "admin@mauekspor.example", "admin123")
        res = c.get("/api/v1/users/")
        assert res.status_code == 200, res.text


def test_buyer_can_create_buyer_request():
    with TestClient(app) as c:
        _login(c, "aya@hikari.example", "buyer123")
        res = c.post(
            "/api/v1/buyer-requests/",
            json={"subject": "Coffee", "destination": "JP", "quantity": "1kg"},
        )
        assert res.status_code == 200, res.text