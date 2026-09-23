from fastapi.testclient import TestClient

from app.main import app


def _client():
    with TestClient(app) as c:
        yield c


def _login(c: TestClient):
    res = c.post(
        "/api/v1/auth/login/",
        json={"email": "admin@mauekspor.example", "password": "admin123"},
    )
    assert res.status_code == 200


def test_health():
    with TestClient(app) as c:
        res = c.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_products_list_and_detail():
    with TestClient(app) as c:
        listed = c.get("/api/v1/products/")
        assert listed.status_code == 200
        assert len(listed.json()["data"]) >= 1

        detail = c.get("/api/v1/products/PRD-COF-001/")
        assert detail.status_code == 200
        assert detail.json()["data"]["hs"] == "0901.21"


def test_create_product_and_enrich():
    with TestClient(app) as c:
        _login(c)
        created = c.post(
            "/api/v1/products/",
            json={"name": "Coconut Sugar", "category": "Food & Beverage", "origin": "Banyuwangi"},
        )
        assert created.status_code == 200
        product_id = created.json()["data"]["id"]
        assert product_id.startswith("PRD-")

        enriched = c.post(f"/api/v1/products/{product_id}/enrich/")
        assert enriched.status_code == 200
        assert enriched.json()["data"]["status"] == "Enriched"


def test_login_returns_session():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["role"] == "Admin"
        assert "access_token" in res.json()["meta"]


def test_create_trade_project():
    with TestClient(app) as c:
        _login(c)
        res = c.post(
            "/api/v1/trade-projects/",
            json={"name": "Coffee to JP", "country": "Japan", "product": "Gayo Arabica", "targetValue": 42000},
        )
        assert res.status_code == 200
        assert res.json()["data"]["stage"] == "Scoping"


def test_export_analysis_flow():
    with TestClient(app) as c:
        _login(c)
        created = c.post(
            "/api/v1/export-analysis/", json={"productId": "PRD-COF-001", "destination": "Japan"}
        )
        assert created.status_code == 200
        analysis_id = created.json()["data"]["id"]

        checked = c.post(f"/api/v1/export-analysis/{analysis_id}/regulation-recommendations/")
        assert checked.status_code == 200
        assert checked.json()["data"]["status"] == "Ready"
        assert len(checked.json()["data"]["recommendations"]) >= 1


def test_unknown_product_404():
    with TestClient(app) as c:
        assert c.get("/api/v1/products/NOPE/").status_code == 404


def test_signup_and_me():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/auth/register/",
            json={"email": "new@example.co", "password": "sekret123", "name": "New User", "role": "Exporter"},
        )
        assert res.status_code == 200
        user_id = res.json()["data"]["id"]
        me = c.get("/api/v1/auth/me/")
        assert me.status_code == 200
        assert me.json()["data"]["id"] == user_id


def test_mutating_request_requires_session():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/products/",
            json={"name": "Unauthed Product", "category": "Food", "origin": "Indonesia"},
        )
        assert res.status_code == 401
        assert res.json()["message"] == "Not authenticated"


def test_buyer_contract_lists():
    with TestClient(app) as c:
        for path in ["/buyers/", "/buyer-requests/", "/forwarders/", "/catalogs/", "/costing/", "/rfqs/"]:
            res = c.get(f"/api/v1{path}")
            assert res.status_code == 200, path


def test_mutating_requests_write_audit_events():
    with TestClient(app) as c:
        c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        created = c.post(
            "/api/v1/products/",
            json={"name": "Audit Coffee", "category": "Food & Beverage", "origin": "Aceh"},
        )
        assert created.status_code == 200

        audit = c.get("/api/v1/audit/")
        assert audit.status_code == 200
        events = audit.json()["data"]
        assert any(event["action"] == "POST /api/v1/products/" for event in events)
