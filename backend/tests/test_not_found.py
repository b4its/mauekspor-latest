"""Test branch 404 untuk resource kunci + endpoint global search."""
from fastapi.testclient import TestClient

from app.main import app


def test_product_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/products/PRD-TIDAK-ADA/")
        assert res.status_code == 404
        assert "not found" in res.json()["message"].lower()


def test_project_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/trade-projects/TP-TIDAK-ADA/")
        assert res.status_code == 404


def test_buyer_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/buyers/BUY-TIDAK-ADA/")
        assert res.status_code == 404


def test_supplier_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/suppliers/SUP-TIDAK-ADA/")
        assert res.status_code == 404


def test_forwarder_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/forwarders/FWD-TIDAK-ADA/")
        assert res.status_code == 404


def test_costing_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/costing/CST-TIDAK-ADA/")
        assert res.status_code == 404


def test_export_analysis_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/export-analysis/EA-TIDAK-ADA/")
        assert res.status_code == 404


def test_catalog_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/catalogs/CAT-TIDAK-ADA/")
        assert res.status_code == 404


def test_market_tidak_ditemukan_404():
    with TestClient(app) as c:
        res = c.get("/api/v1/markets/MKT-TIDAK-ADA/")
        assert res.status_code == 404


def test_global_search_mengembalikan_hasil():
    with TestClient(app) as c:
        res = c.get("/api/v1/search/?q=kopi")
        assert res.status_code == 200
        # bentuk data array (list hasil)
        assert isinstance(res.json().get("data"), list)


def test_global_search_query_kosong():
    with TestClient(app) as c:
        res = c.get("/api/v1/search/?q=")
        assert res.status_code == 200
