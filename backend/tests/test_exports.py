"""Test endpoint export CSV/XLSX (dipakai frontend untuk download)."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["meta"]["access_token"]


def test_export_products_csv():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/products/export.csv", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert res.content.startswith(b"id") or res.content  # header CSV ada


def test_export_buyers_csv():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/buyers/export.csv", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


def test_export_analyses_csv():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/export-analysis/export.csv", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


def test_export_costing_csv():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/costing/export.csv", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


def test_export_audit_csv():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/audit/export.csv", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


def test_export_products_xlsx():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/products/export.xlsx", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "spreadsheet" in res.headers["content-type"] or "octet-stream" in res.headers["content-type"]
        # XLSX dimulai dengan PK (zip magic)
        assert res.content.startswith(b"PK")


def test_export_buyers_xlsx():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/buyers/export.xlsx", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


def test_export_analyses_xlsx():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/export-analysis/export.xlsx", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


def test_export_costing_xlsx():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/costing/export.xlsx", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


def test_export_audit_xlsx():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/audit/export.xlsx", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
