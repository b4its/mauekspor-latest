"""Smoke test menyeluruh: pastikan semua koleksi bisa di-list dan aksi utama tidak 500."""
from fastapi.testclient import TestClient

from app.main import app
from app import db  # noqa: F401  (pastikan modul db termuat sebelum TestClient)


def test_all_collections_listable():
    with TestClient(app) as c:
        lr = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert lr.status_code == 200, lr.text
        for path in [
            "/users/", "/products/", "/trade-projects/", "/business-profiles/",
            "/buyers/", "/buyer-requests/", "/forwarders/", "/catalogs/",
            "/costing/", "/markets/", "/rfqs/", "/quotations/", "/orders/",
            "/compliance/requirements/", "/documents/", "/shipments/", "/payments/",
            "/tasks/", "/suppliers/", "/analytics/overview/", "/notifications/",
            "/audit/", "/team/", "/templates/", "/automations/", "/integrations/",
            "/knowledge/", "/educational/", "/educational/articles/", "/calendar/",
            "/files/", "/messages/", "/reports/", "/billing/", "/support/",
            "/api-keys/", "/export-analysis/",
        ]:
            res = c.get(f"/api/v1{path}")
            assert res.status_code == 200, f"{path} -> {res.status_code} {res.text[:120]}"


def test_posts_do_not_crash():
    with TestClient(app) as c:
        lr = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert lr.status_code == 200
        cases = [
            ("/api/v1/products/", {"name": "Coconut Sugar", "category": "Food", "origin": "ID"}),
            ("/api/v1/trade-projects/", {"name": "Proj", "country": "JP", "targetValue": 100}),
            ("/api/v1/buyers/", {"name": "BuyCo", "country": "JP", "segment": "Retail", "interestedProducts": []}),
            ("/api/v1/buyer-requests/", {"subject": "Coffee", "destination": "JP", "quantity": "1kg"}),
            ("/api/v1/forwarders/", {"name": "FWD", "coverage": "Asia", "mode": "Air"}),
            ("/api/v1/catalogs/", {"title": "Cat", "targetMarket": "JP", "moq": "1"}),
            ("/api/v1/costing/", {"title": "Cost", "destination": "JP", "incoterm": "FOB", "margin": 20}),
            ("/api/v1/markets/", {"country": "JP", "entryStrategy": "Direct"}),
            ("/api/v1/rfqs/", {"buyerName": "BuyCo", "destination": "JP", "quantity": "1"}),
            ("/api/v1/quotations/", {"projectId": "P1", "buyerName": "BuyCo", "incoterm": "FOB"}),
            ("/api/v1/orders/", {"projectId": "P1", "buyerName": "BuyCo", "value": 100}),
            ("/api/v1/documents/generate/", {"type": "Invoice", "projectId": "P1", "data": {}}),
            ("/api/v1/calendar/", {"title": "Event", "date": "2026-08-10", "type": "Task"}),
            ("/api/v1/team/invite/", {"email": "x@y.co", "role": "Ops"}),
            ("/api/v1/templates/", {"title": "Tpl", "category": "Doc"}),
            ("/api/v1/files/", {"name": "f.pdf", "type": "Document"}),
            ("/api/v1/support/", {"subject": "Help", "category": "Question", "description": "..."}),
            ("/api/v1/api-keys/", {"name": "Key", "scopes": ["read"]}),
        ]
        for path, payload in cases:
            res = c.post(path, json=payload)
            assert res.status_code == 200, f"{path} -> {res.status_code} {res.text[:150]}"


def test_action_endpoints():
    with TestClient(app) as c:
        c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        asserts = [
            ("/api/v1/products/PRD-COF-001/enrich/", None),
            ("/api/v1/buyers/BUY-HIKARI-JP/qualify/", None),
            ("/api/v1/catalogs/CAT-COF-JP-001/publish/", None),
            ("/api/v1/catalogs/CAT-COF-JP-001/generate-description/", None),
            ("/api/v1/costing/CST-JP-017/recalculate/", None),
            ("/api/v1/quotations/Q-2408-017-A/accept/", None),
            ("/api/v1/tasks/TSK-COF-LABEL-01/complete/", None),
            ("/api/v1/tasks/TSK-COF-LABEL-01/assign/", {"owner": "Ops"}),
            ("/api/v1/documents/DOC-JP-INV-001/approve/", None),
            ("/api/v1/orders/SO-2408-026/confirm/", None),
            ("/api/v1/shipments/SHP-JP-017/milestones/", {"milestone": "Loaded"}),
            ("/api/v1/notifications/NTF-001/read/", None),
            ("/api/v1/messages/MSG-HIKARI-LABEL/resolve/", None),
            ("/api/v1/support/SUPPORT-1041/resolve/", None),
            ("/api/v1/files/FIL-CI-JP/verify/", None),
            ("/api/v1/api-keys/KEY-LOG-001/revoke/", None),
            ("/api/v1/export-analysis/ANL-COF-001/regulation-recommendations/", None),
        ]
        for path, payload in asserts:
            res = c.post(path, json=payload or {})
            assert res.status_code == 200, f"{path} -> {res.status_code} {res.text[:150]}"


def test_me_and_logout_flow():
    with TestClient(app) as c:
        res = c.post("/api/v1/auth/login/", json={"email": "rizal@kopigayo.example", "password": "rizal123"})
        assert res.status_code == 200
        me = c.get("/api/v1/auth/me/")
        assert me.status_code == 200
        assert me.json()["data"]["role"] == "Exporter"
        out = c.post("/api/v1/auth/logout/")
        assert out.status_code == 200
        assert c.get("/api/v1/auth/me/").status_code == 401