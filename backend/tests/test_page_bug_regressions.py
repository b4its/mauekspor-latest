"""Regresi bug halaman yang ditemukan saat audit UI.

Setiap test menutup satu kelas bug yang membuat halaman menampilkan nilai kosong,
NaN, atau error 500:
1. Compare analisis 500 saat `recommendations` berupa list (hasil regulation check).
2. Order hasil konversi quotation tidak punya `readiness` → UI menampilkan NaN%.
3. Market baru tidak punya field yang dibaca kartu UI → blank & "%".
4. HS code detail memutasi record cache bersama (mencemari indeks in-memory).
5. List endpoint mem-bypass clamp `limit` (anti-DoS).
6. Shortlist RFQ tidak mengisi `catalog`/`matchScore`.
"""
from fastapi.testclient import TestClient

from app.main import app
from app import db

ADMIN = ("admin@mauekspor.example", "admin123")


def _auth(c: TestClient) -> dict:
    res = c.post("/api/v1/auth/login/", json={"email": ADMIN[0], "password": ADMIN[1]})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['meta']['access_token']}"}


def test_export_analysis_compare_handles_list_recommendations():
    """run_regulation_check menyimpan `recommendations` sebagai list; compare harus tahan."""
    with TestClient(app) as c:
        h = _auth(c)
        aid = c.get("/api/v1/export-analysis/", headers=h).json()["data"][0]["id"]
        # Jadikan recommendations sebuah list (seperti hasil regulation check).
        rec = db.get("export_analyses", aid)
        rec["recommendations"] = [{"type": "Certificate", "title": "COO", "status": "Required"}]
        db.save(rec)
        pid = rec.get("productId") or c.get("/api/v1/products/", headers=h).json()["data"][0]["id"]
        res = c.post(
            "/api/v1/export-analysis/compare/",
            json={"product_id": pid, "country_codes": ["JP", "SG"]},
            headers=h,
        )
        assert res.status_code == 200, res.text


def test_quotation_to_order_sets_readiness_shape():
    with TestClient(app) as c:
        h = _auth(c)
        q = c.get("/api/v1/quotations/", headers=h).json()["data"][0]
        db.get("quotations", q["id"])
        # Pastikan status bisa dikonversi.
        quote = db.get("quotations", q["id"])
        quote["status"] = "Accepted"
        quote.pop("orderId", None)
        db.save(quote)
        res = c.post(f"/api/v1/quotations/{q['id']}/to-order/", headers=h)
        assert res.status_code == 200, res.text
        order = res.json()["data"]
        assert order.get("readiness") == 0
        assert isinstance(order.get("lines"), list)
        assert isinstance(order.get("checklist"), list)


def test_new_market_has_fields_read_by_ui_cards():
    with TestClient(app) as c:
        h = _auth(c)
        res = c.post("/api/v1/markets/", json={"country": "JP", "entryStrategy": "Direct"}, headers=h)
        assert res.status_code == 200, res.text
        m = res.json()["data"]
        for field in ("complianceComplexity", "logisticsFeasibility", "estimatedMargin", "growth"):
            assert field in m, f"market tidak punya {field}"
            assert m[field] is not None


def test_hs_code_detail_does_not_pollute_cache():
    with TestClient(app) as c:
        h = _auth(c)
        from app.data.hs_loader import get_hs_loader
        loader = get_hs_loader()
        code = loader.codes[0]["hs_code"]
        before = dict(loader.get_hs_code(code) or {})
        c.get(f"/api/v1/hs-codes/{code}/", headers=h)
        after = loader.get_hs_code(code) or {}
        assert "section_name" not in before
        assert "section_name" not in after, "cache HS tercemar field turunan"


def test_list_endpoints_clamp_limit():
    with TestClient(app) as c:
        h = _auth(c)
        res = c.get("/api/v1/products/?limit=100000000", headers=h)
        assert res.status_code == 200
        meta = res.json()["meta"]
        assert meta["limit"] <= 500, f"limit tidak di-clamp: {meta['limit']}"
        res2 = c.get("/api/v1/forwarders/?limit=100000000", headers=h)
        assert res2.json()["meta"]["limit"] <= 500


def test_rfq_shortlist_sets_catalog_and_match_score():
    with TestClient(app) as c:
        h = _auth(c)
        created = c.post(
            "/api/v1/rfqs/",
            json={"buyerName": "Buyer Uji", "destination": "JP", "quantity": "1"},
            headers=h,
        )
        rfq = created.json()["data"]
        res = c.post(
            f"/api/v1/rfqs/{rfq['id']}/shortlist/",
            json={"supplier": "PT Uji", "catalog": "Katalog Uji", "score": 77},
            headers=h,
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["matchScore"] == 77
        assert data["matches"][-1]["catalog"] == "Katalog Uji"
