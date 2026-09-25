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


def test_buyer_cannot_read_commercial_modules():
    """Buyer hanya boleh baca modul yang relevan; sisanya 403 (bukan 200)."""
    with TestClient(app) as c:
        _login(c, "aya@hikari.example", "buyer123")
        # Boleh: buyer-requests, quotations, orders, portal buyer
        for path in ("/api/v1/buyer-requests/", "/api/v1/quotations/", "/api/v1/orders/",
                     "/api/v1/buyers/portal/"):
            assert c.get(path).status_code == 200, f"{path} should be readable by Buyer"
        # Tidak boleh: suppliers, team, costing, payments, buyers (CRM penuh), forwarders
        for path in ("/api/v1/suppliers/", "/api/v1/team/", "/api/v1/costing/",
                     "/api/v1/payments/", "/api/v1/buyers/", "/api/v1/forwarders/"):
            assert c.get(path).status_code == 403, f"{path} must be forbidden for Buyer"


def test_forwarder_cannot_read_buyer_or_cost_data():
    with TestClient(app) as c:
        # Daftarkan user forwarder lalu login.
        c.post(
            "/api/v1/auth/register/",
            json={"email": "fwd-rbac@example.com", "password": "fwd12345",
                  "name": "Fwd RBAC", "role": "Forwarder", "organization": "QA"},
        )
        _login(c, "fwd-rbac@example.com", "fwd12345")
        # Boleh: shipments, documents
        for path in ("/api/v1/shipments/", "/api/v1/documents/"):
            assert c.get(path).status_code == 200, f"{path} should be readable by Forwarder"
        # Tidak boleh: buyers, suppliers, costing, payments, team
        for path in ("/api/v1/buyers/", "/api/v1/suppliers/", "/api/v1/costing/",
                     "/api/v1/payments/", "/api/v1/team/"):
            assert c.get(path).status_code == 403, f"{path} must be forbidden for Forwarder"


def test_shared_modules_readable_by_any_role():
    """Modul kolaborasi (notifikasi/pesan/dukungan/analitik) boleh dibaca semua peran."""
    with TestClient(app) as c:
        _login(c, "aya@hikari.example", "buyer123")
        for path in ("/api/v1/notifications/", "/api/v1/messages/", "/api/v1/support/",
                     "/api/v1/analytics/overview/", "/api/v1/reports/"):
            assert c.get(path).status_code == 200, f"{path} should be shared-readable"