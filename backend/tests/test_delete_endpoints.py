"""Test endpoint DELETE: cascade, 404, dan pembatasan role.

Sebelumnya DELETE routes nyaris tidak diuji secara langsung (hanya lewat
contract test). File ini memverifikasi perilaku nyata: record benar-benar
terhapus, relasi ikut terhapus (cascade), 404 untuk id tak ada, dan guard
RBAC/role untuk endpoint yang sensitif.
"""
from fastapi.testclient import TestClient

from app.main import app
from app import db

ADMIN = ("admin@mauekspor.example", "admin123")
BUYER = ("aya@hikari.example", "buyer123")
EXPORTER = ("rizal@kopigayo.example", "rizal123")


def _login(c: TestClient, creds=ADMIN) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_delete_product_cascade_menghapus_relasi():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        # Product + data turunan (enrichment, MI, pricing).
        db.insert("products", {"id": "P-DEL", "name": "Hapus Aku", "category": "Coffee"})
        db.insert("product_enrichments", {"id": "PE-DEL", "productId": "P-DEL"})
        db.insert("market_intelligence", {"id": "MI-DEL", "productId": "P-DEL"})
        db.insert("pricing_results", {"id": "PR-DEL", "productId": "P-DEL"})

        r = c.delete("/api/v1/products/P-DEL/", headers=_auth(token))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["status"] == "deleted"

        assert db.get("products", "P-DEL") is None
        assert db.find("product_enrichments", productId="P-DEL") == []
        assert db.find("market_intelligence", productId="P-DEL") == []
        assert db.find("pricing_results", productId="P-DEL") == []


def test_delete_product_tidak_ada_404():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        r = c.delete("/api/v1/products/P-TIDAK-ADA/", headers=_auth(token))
        assert r.status_code == 404, r.text


def test_delete_catalog_cascade_images_dan_variants():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        db.insert("catalogs", {"id": "C-DEL", "title": "Katalog Hapus"})
        db.insert("catalog_images", {"id": "IMG1", "catalogId": "C-DEL", "url": "a.png"})
        db.insert("catalog_images", {"id": "IMG2", "catalogId": "C-DEL", "url": "b.png"})
        db.insert("catalog_variant_types", {"id": "VT1", "catalogId": "C-DEL", "typeName": "Ukuran"})
        db.insert("catalog_variant_options", {"id": "OPT1", "variantTypeId": "VT1", "value": "250g"})

        r = c.delete("/api/v1/catalogs/C-DEL/", headers=_auth(token))
        assert r.status_code == 200, r.text
        # Delay: cascade options dijalankan di dalam handler.
        assert db.get("catalogs", "C-DEL") is None
        assert db.find("catalog_images", catalogId="C-DEL") == []
        assert db.find("catalog_variant_types", catalogId="C-DEL") == []
        assert db.find("catalog_variant_options", variantTypeId="VT1") == []


def test_delete_catalog_tidak_ada_404():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        r = c.delete("/api/v1/catalogs/C-TIDAK-ADA/", headers=_auth(token))
        assert r.status_code == 404, r.text


def test_delete_costing_dan_404():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        db.insert("costing", {"id": "CO-DEL", "productName": "X"})
        assert c.delete("/api/v1/costing/CO-DEL/", headers=_auth(token)).status_code == 200
        assert db.get("costing", "CO-DEL") is None
        assert c.delete("/api/v1/costing/CO-TIDAK-ADA/", headers=_auth(token)).status_code == 404


def test_delete_buyer_request_dan_404():
    with TestClient(app) as c:
        token = _login(c, BUYER)
        db.insert("buyer_requests", {"id": "BR-DEL", "subject": "Test"})
        assert c.delete("/api/v1/buyer-requests/BR-DEL/", headers=_auth(token)).status_code == 200
        assert db.get("buyer_requests", "BR-DEL") is None
        assert c.delete("/api/v1/buyer-requests/BR-TIDAK-ADA/", headers=_auth(token)).status_code == 404


def test_delete_user_hanya_admin():
    with TestClient(app) as c:
        # Non-admin ditolak (403).
        buyer_token = _login(c, BUYER)
        db.insert("users", {"id": "U-DEL", "email": "x@y.example", "role": "Exporter"})
        r = c.delete("/api/v1/users/U-DEL/", headers=_auth(buyer_token))
        assert r.status_code == 403, r.text
        # Record tetap ada.
        assert db.get("users", "U-DEL") is not None

        # Admin boleh.
        admin_token = _login(c, ADMIN)
        r2 = c.delete("/api/v1/users/U-DEL/", headers=_auth(admin_token))
        assert r2.status_code == 200, r2.text
        assert db.get("users", "U-DEL") is None


def test_delete_user_tidak_bisa_hapus_diri_sendiri():
    with TestClient(app) as c:
        token = _login(c, ADMIN)
        me = db.get_by("users", email=ADMIN[0])
        r = c.delete(f"/api/v1/users/{me['id']}/", headers=_auth(token))
        assert r.status_code == 400, r.text
        assert db.get("users", me["id"]) is not None


def test_delete_user_tidak_ada_404():
    with TestClient(app) as c:
        token = _login(c, ADMIN)
        r = c.delete("/api/v1/users/U-TIDAK-ADA/", headers=_auth(token))
        assert r.status_code == 404, r.text


def test_delete_chat_session():
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        res = c.post("/api/v1/chat/sessions/", json={"title": "hapus aku"}, headers=_auth(token))
        assert res.status_code in (200, 201), res.text
        sid = res.json()["data"]["id"]
        r = c.delete(f"/api/v1/chat/sessions/{sid}/", headers=_auth(token))
        assert r.status_code == 200, r.text
        assert db.get("chat_sessions", sid) is None
