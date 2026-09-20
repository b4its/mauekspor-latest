"""Test fitur inti ExportReadyAI yang diadaptasi ke backend FastAPI:
- Enrichment produk (HS code + SKU)
- Market Intelligence & Pricing (AI per produk)
- Export Analysis (compliance check, snapshot, reanalyze, compare, regulation 10-bagian)
- Costing nyata (EXW/FOB/CIF + exchange rate + PDF)
- Katalog (CRUD, gambar, varian, AI, public)
- Buyer request matching
- Forwarder (profil, review, rekomendasi, statistik)
- Educational CRUD
- Chat sessions
"""
from fastapi.testclient import TestClient

import pytest

from app.main import app


def _login(c) -> None:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200, res.text


# ---------------------------------------------------------------------------
# Enrichment produk
# ---------------------------------------------------------------------------
def test_product_enrich_sets_hs_and_sku():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/products/PRD-COF-001/enrich/")
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["status"] == "Enriched"
        assert data["hs"] not in ("", "TBD")
        assert data["sku"]
        # Enrichment tersimpan terpisah
        enr = c.get("/api/v1/products/PRD-COF-001/").json()["data"]
        assert enr["hs"]


def test_product_crud_patch_delete():
    with TestClient(app) as c:
        _login(c)
        r = c.patch("/api/v1/products/PRD-SNK-006/", json={"name": "Cassava Chips Sea Salt"})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["name"] == "Cassava Chips Sea Salt"
        r = c.delete("/api/v1/products/PRD-SNK-006/")
        assert r.status_code == 200, r.text
        r = c.get("/api/v1/products/PRD-SNK-006/")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Market Intelligence & Pricing
# ---------------------------------------------------------------------------
def test_market_intelligence_generate_and_get():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/products/PRD-COF-001/ai/market-intelligence/")
        assert r.status_code == 200, r.text
        mi = r.json()["data"]
        assert "recommendedCountries" in mi
        r = c.get("/api/v1/products/PRD-COF-001/ai/market-intelligence/")
        assert r.status_code == 200
        assert r.json()["data"]["productId"] == "PRD-COF-001"


def test_product_pricing_generate():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/products/PRD-COF-001/ai/pricing/", json={
            "cogs_per_unit_idr": 28500, "target_margin_percent": 22, "target_country_code": "JP",
        })
        assert r.status_code == 200, r.text
        pr = r.json()["data"]
        assert pr["exwPrice"] > 0
        assert pr["fobPrice"] > pr["exwPrice"]
        assert pr["cifPrice"] > pr["fobPrice"]


def test_catalog_description_generate():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/products/PRD-COF-001/ai/catalog-description/", json={})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["export_description"]


# ---------------------------------------------------------------------------
# Export analysis: compliance + snapshot + reanalyze + compare + regulasi
# ---------------------------------------------------------------------------
def test_export_analysis_compliance_and_regulations():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/export-analysis/", json={"productId": "PRD-COF-001", "destination": "JP"})
        assert r.status_code in (200, 409), r.text  # 409 bila sudah ada
        if r.status_code == 409:
            analysis = c.get("/api/v1/export-analysis/").json()["data"][0]
        else:
            analysis = r.json()["data"]
        aid = analysis["id"]
        # Detail berisi snapshot & grade
        detail = c.get(f"/api/v1/export-analysis/{aid}/").json()["data"]
        assert "productSnapshot" in detail
        assert detail.get("statusGrade") in ("Ready", "Warning", "Critical")
        # Rekomendasi regulasi 10 bagian
        regs = c.get(f"/api/v1/export-analysis/{aid}/regulation-recommendations/?language=id").json()["data"]
        assert len(regs["sections"]) == 10
        # Reanalyze
        r = c.post(f"/api/v1/export-analysis/{aid}/reanalyze/")
        assert r.status_code == 200, r.text
        assert r.json()["data"]["productChanged"] is False
        # Compare
        r = c.post("/api/v1/export-analysis/compare/", json={
            "product_id": "PRD-COF-001", "country_codes": ["JP", "SG"],
        })
        assert r.status_code == 200, r.text
        assert len(r.json()["data"]["results"]) == 2
        # Delete
        r = c.delete(f"/api/v1/export-analysis/{aid}/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------
def test_countries_list_and_detail():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/countries/")
        assert r.status_code == 200
        assert len(r.json()["data"]) >= 10
        r = c.get("/api/v1/countries/JP/")
        assert r.status_code == 200
        assert "regulations_by_category" in r.json()["data"]
        assert "Labeling" in r.json()["data"]["regulations_by_category"]


# ---------------------------------------------------------------------------
# HS codes
# ---------------------------------------------------------------------------
def test_hs_codes_search_and_autocomplete():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/hs-codes/?search=coffee")
        assert r.status_code == 200
        assert len(r.json()["data"]) > 0
        r = c.get("/api/v1/hs-codes/autocomplete/?q=0901")
        assert r.status_code == 200
        assert any(x["hs_code"].startswith("0901") for x in r.json()["data"])


# ---------------------------------------------------------------------------
# Costing nyata
# ---------------------------------------------------------------------------
def test_costing_full_calculation_and_pdf():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/costing/", json={
            "title": "Test FOB", "destination": "Japan", "productId": "PRD-COF-001",
            "incoterm": "FOB", "margin": 22, "cogs_per_unit_idr": 28500,
        })
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["exwPrice"] > 0
        assert data["fobPrice"] > data["exwPrice"]
        assert data["cifPrice"] > data["fobPrice"]
        assert data["exchangeRate"] > 0
        assert data["container"]["capacity_20ft"] >= 0
        # Recalculate
        r = c.post(f"/api/v1/costing/{data['id']}/recalculate/")
        assert r.status_code == 200, r.text
        # Exchange rate
        r = c.get("/api/v1/costing/exchange-rate/")
        assert r.status_code == 200, r.text
        # PDF
        r = c.get(f"/api/v1/costing/{data['id']}/pdf/")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Katalog: CRUD + gambar + varian + AI + public
# ---------------------------------------------------------------------------
def test_catalog_images_variants_and_ai():
    with TestClient(app) as c:
        _login(c)
        # Varian
        r = c.get("/api/v1/catalogs/CAT-COF-JP-001/variant-types/")
        assert r.status_code == 200, r.text
        assert len(r.json()["meta"]["predefined_types"]) == 8
        r = c.post("/api/v1/catalogs/CAT-COF-JP-001/variant-types/", json={
            "type_code": "size", "type_name": "Ukuran", "options": ["250g", "1kg"],
        })
        assert r.status_code == 200, r.text
        vt_id = r.json()["data"]["id"]
        assert len(r.json()["data"]["options"]) == 2
        # Gambar
        r = c.post("/api/v1/catalogs/CAT-COF-JP-001/images/", json={
            "image_url": "https://example.com/coffee.jpg", "alt_text": "Kopi Gayo", "is_primary": True,
        })
        assert r.status_code == 200, r.text
        # AI description
        r = c.post("/api/v1/catalogs/CAT-COF-JP-001/ai/description/", json={"save_to_catalog": False})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["export_description"]
        # Public
        r = c.get("/api/v1/catalogs/public/")
        assert r.status_code == 200, r.text
        # Update + delete varian
        r = c.put(f"/api/v1/catalogs/CAT-COF-JP-001/variant-types/{vt_id}/", json={"type_code": "size", "type_name": "Kemasan"})
        assert r.status_code == 200, r.text
        r = c.delete(f"/api/v1/catalogs/CAT-COF-JP-001/variant-types/{vt_id}/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Buyer request matching
# ---------------------------------------------------------------------------
def test_buyer_request_matching():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/buyer-requests/", json={
            "subject": "Coffee beans for Japan", "destination": "JP", "quantity": "2000",
        })
        assert r.status_code == 200, r.text
        req = r.json()["data"]
        assert "matches" in req
        # matched-catalogs
        r = c.get(f"/api/v1/buyer-requests/{req['id']}/matched-catalogs/")
        assert r.status_code == 200, r.text
        # status patch
        r = c.patch(f"/api/v1/buyer-requests/{req['id']}/status/", json={"status": "Closed"})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["status"] == "Closed"


# ---------------------------------------------------------------------------
# Forwarder: profil, review, rekomendasi, statistik
# ---------------------------------------------------------------------------
def test_forwarder_reviews_recommendations_statistics():
    with TestClient(app) as c:
        _login(c)
        # Review
        r = c.post("/api/v1/forwarders/FWD-NGL/reviews/", json={"rating": 5, "review_text": "Bagus"})
        assert r.status_code == 200, r.text
        review = r.json()["data"]
        # Rating ter-update
        fwd = c.get("/api/v1/forwarders/FWD-NGL/").json()["data"]
        assert fwd["totalReviews"] >= 1
        # Update review
        r = c.put(f"/api/v1/forwarders/FWD-NGL/reviews/{review['id']}/", json={"rating": 4, "review_text": "OK"})
        assert r.status_code == 200, r.text
        # Statistik
        r = c.get("/api/v1/forwarders/FWD-NGL/statistics/")
        assert r.status_code == 200, r.text
        assert "ratingDistribution" in r.json()["data"]
        # Rekomendasi
        r = c.get("/api/v1/forwarders/recommendations/?destination_country=JP")
        assert r.status_code == 200, r.text
        # Profil
        r = c.post("/api/v1/forwarders/profile/", json={"company_name": "Test Logistics", "specialization_routes": ["ID-JP"]})
        assert r.status_code == 200, r.text
        r = c.get("/api/v1/forwarders/profile/me/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Buyer profile
# ---------------------------------------------------------------------------
def test_buyer_profile_crud():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/buyers/profile/", json={
            "company_name": "Test Importer", "preferred_product_categories": ["Coffee"],
        })
        assert r.status_code == 200, r.text
        r = c.get("/api/v1/buyers/profile/me/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Educational CRUD + upload
# ---------------------------------------------------------------------------
def test_educational_crud_and_upload():
    with TestClient(app) as c:
        _login(c)
        r = c.post("/api/v1/educational/modules/", json={"title": "Modul Test", "description": "desc", "order_index": 9})
        assert r.status_code == 200, r.text
        mid = r.json()["data"]["id"]
        r = c.post("/api/v1/educational/articles/", json={"module_id": mid, "title": "Artikel 1", "content": "# Hello"})
        assert r.status_code == 200, r.text
        art_id = r.json()["data"]["id"]
        # Detail module berisi artikel
        r = c.get(f"/api/v1/educational/modules/{mid}/")
        assert r.status_code == 200, r.text
        assert len(r.json()["data"]["articles"]) == 1
        # Upload file
        r = c.post(f"/api/v1/educational/articles/{art_id}/upload-file/", files={"file": ("guide.pdf", b"%PDF-1.4 test", "application/pdf")})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["fileUrl"]
        # Delete
        r = c.delete(f"/api/v1/educational/modules/{mid}/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Chat sessions
# ---------------------------------------------------------------------------
def test_chat_sessions_and_suggestions():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/chat/sessions/")
        assert r.status_code == 200, r.text
        r = c.post("/api/v1/chat/sessions/", json={"title": "Sesi baru"})
        assert r.status_code == 200, r.text
        sid = r.json()["data"]["id"]
        r = c.post(f"/api/v1/chat/sessions/{sid}/messages/", json={"text": "Halo"})
        assert r.status_code == 200, r.text
        assert len(r.json()["data"]["messages"]) >= 2  # user + AI
        r = c.get("/api/v1/chat/suggestions/")
        assert r.status_code == 200, r.text
        assert len(r.json()["data"]) > 0
        r = c.delete(f"/api/v1/chat/sessions/{sid}/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Dashboard summary & register admin & users delete
# ---------------------------------------------------------------------------
def test_dashboard_summary_and_admin_flow():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/business-profiles/dashboard/summary/")
        assert r.status_code == 200, r.text
        assert "counts" in r.json()["data"]
        r = c.post("/api/v1/auth/register-admin/", json={
            "email": "admin2@test.com", "password": "pass1234", "full_name": "Admin 2", "admin_code": "admin-bootstrap-2026",
        })
        assert r.status_code == 200, r.text
        admin_id = r.json()["data"]["id"]
        # Login ulang sebagai admin utama (register-admin menimpa session cookie)
        _login(c)
        r = c.delete(f"/api/v1/users/{admin_id}/")
        assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# Filtering / pagination pada list
# ---------------------------------------------------------------------------
def test_list_filtering_and_pagination():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/products/?search=coffee")
        assert r.status_code == 200
        assert len(r.json()["data"]) >= 1
        assert all("coffee" in p["name"].lower() for p in r.json()["data"])
        r = c.get("/api/v1/products/?limit=2&offset=0")
        assert r.status_code == 200
        assert len(r.json()["data"]) <= 2
        assert r.json()["meta"]["total"] >= 3
        r = c.get("/api/v1/forwarders/?min_rating=4")
        assert r.status_code == 200
        r = c.get("/api/v1/buyer-requests/?status=Open")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Notifikasi otomatis
# ---------------------------------------------------------------------------
def test_auto_notifications_on_actions():
    with TestClient(app) as c:
        _login(c)
        before = len(c.get("/api/v1/notifications/").json()["data"])
        c.post("/api/v1/tasks/TSK-COF-LABEL-01/complete/")
        c.post("/api/v1/shipments/SHP-JP-017/milestones/", json={"milestone": "Booking Confirmed"})
        after = len(c.get("/api/v1/notifications/").json()["data"])
        assert after >= before + 1, "aksi penting harus membuat notifikasi"


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
def test_analytics_overview_and_lanes():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/analytics/overview/")
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert len(data) >= 4
        assert any(m["label"] == "Pipeline value" for m in data)
        assert any(m["label"] == "Active projects" for m in data)
        # lane terurut berdasarkan nilai (terbesar dulu), berisi data nyata
        r = c.get("/api/v1/analytics/lanes/")
        assert r.status_code == 200, r.text
        lanes = r.json()["data"]
        assert lanes, "harus ada minimal 1 lane"
        values = [l["readiness"] for l in lanes]
        assert all(0 <= v <= 100 for v in values)
        assert all(l["href"].startswith("/trade-projects/") for l in lanes)
        assert lanes[0]["label"], "lane pertama punya nama proyek"
        r = c.post("/api/v1/analytics/refresh/")
        assert r.status_code == 200, r.text
        assert len(r.json()["data"]) >= 4


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def test_settings_get_and_update():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/settings/")
        assert r.status_code == 200, r.text
        assert r.json()["data"]["companyName"]
        r = c.put("/api/v1/settings/", json={"nib": "1234567890123", "taxId": "01.234.567.8"})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["nib"] == "1234567890123"


# ---------------------------------------------------------------------------
# Audit CSV export
# ---------------------------------------------------------------------------
def test_audit_csv_export():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/audit/export.csv")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/csv")
        assert b"time,actor,action" in r.content


def test_batch_enrich_and_batch_delete():
    with TestClient(app) as c:
        _login(c)
        # Siapkan 2 produk baru (belum enriched)
        p1 = c.post("/api/v1/products/", json={"name": "Kopi Batch A", "category": "Food", "origin": "Aceh"}).json()["data"]
        p2 = c.post("/api/v1/products/", json={"name": "Teh Batch B", "category": "Beverage", "origin": "Jawa"}).json()["data"]
        assert p1["status"] != "Enriched" and p2["status"] != "Enriched"

        # Batch enrich tanpa ids -> enrich semua produk non-Enriched
        r = c.post("/api/v1/products/batch/enrich/", json={"ids": []})
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["enrichedCount"] >= 2
        assert p1["id"] in data["enriched"] and p2["id"] in data["enriched"]

        # Setelah batch: semua enriched
        p1b = c.get(f"/api/v1/products/{p1['id']}/").json()["data"]
        assert p1b["status"] == "Enriched" and p1b["hs"] not in ("", "TBD")

        # Batch delete dengan ids
        r = c.post("/api/v1/products/batch/delete/", json={"ids": [p1["id"], p2["id"], "TIDAK-ADA"]})
        assert r.status_code == 200, r.text
        assert r.json()["data"]["deletedCount"] == 2
        assert c.get(f"/api/v1/products/{p1['id']}/").status_code == 404

        # Batch delete tanpa ids -> 422
        r = c.post("/api/v1/products/batch/delete/", json={"ids": []})
        assert r.status_code == 422


def test_costing_compare_and_xlsx_exports():
    with TestClient(app) as c:
        _login(c)
        costing_ids = [x["id"] for x in c.get("/api/v1/costing/").json()["data"]]
        assert costing_ids, "seed costing kosong"
        r = c.post("/api/v1/costing/compare/", json={"ids": costing_ids})
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["count"] == len(costing_ids)
        assert data["recommendation"] and data["recommendation"]["costingId"]
        # ids kosong -> 422 + pesan Inggris
        r = c.post("/api/v1/costing/compare/", json={"ids": []})
        assert r.status_code == 422
        assert "ids are required" in r.json()["message"]

        # Automations: run menaikkan runs + membuat notifikasi
        auto = next(a for a in c.get("/api/v1/automations/").json()["data"] if a["id"] == "AUT-LABEL-BLOCKER")
        before = auto["runs"]
        r = c.post("/api/v1/automations/AUT-LABEL-BLOCKER/run/")
        assert r.status_code == 200, r.text
        assert r.json()["data"]["runs"] == before + 1
        notif = c.get("/api/v1/notifications/").json()["data"]
        assert any(n.get("type") == "automation" and n.get("status") == "Unread" for n in notif)
        r = c.post("/api/v1/automations/AUT-LABEL-BLOCKER/activate/")
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "Active"

        # Compare analysis -> JSON & PDF (data nyata dari compliance service)
        products = c.get("/api/v1/products/").json()["data"]
        prod = products[0]
        r = c.post("/api/v1/export-analysis/compare/", json={"product_id": prod["id"], "country_codes": ["JP", "US", "DE"]})
        assert r.status_code == 200, r.text
        results = r.json()["data"]["results"]
        assert len(results) == 3
        scores = [x["score"] for x in results]
        assert scores == sorted(scores, reverse=True)
        r = c.post("/api/v1/export-analysis/compare/pdf/", json={"product_id": prod["id"], "country_codes": ["JP", "US", "DE"]})
        assert r.status_code == 200, r.text[:80]
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF")
        assert b"BEST OPTION" in r.content

        # SSE notifications: endpoint terdaftar; tanpa auth -> 401; generator
        # menghasilkan event 'unread' saat punya cookie valid.
        # (TestClient/httpx tidak bisa menahan stream tanpa hang, jadi uji
        # fungsinya langsung di Python.)
        import json as _json
        from types import SimpleNamespace

        from fastapi import HTTPException as _HTTPException
        from app.api.routes import stream_notifications

        async def _anext(agen):
            return await agen.__anext__()

        with pytest.raises(_HTTPException) as exc_info:
            stream_notifications(SimpleNamespace(cookies={}))
        assert exc_info.value.status_code == 401

        # Token diambil dari body respons login (bukan cookie jar httpx yang
        # bisa mengubah encoding nilai cookie secara nondeterministik)
        login_resp = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        token = login_resp.json()["meta"]["access_token"]
        assert token
        resp = stream_notifications(SimpleNamespace(cookies={"access_token": token}))
        import asyncio as _asyncio

        first = _asyncio.run(_anext(resp.body_iterator))
        assert first.startswith("event: unread")
        payload = _json.loads(first.split("data: ", 1)[1].strip())
        assert "unread_count" in payload

        # Export XLSX valid (zip XML) untuk semua modul
        for url in ("/api/v1/products/export.xlsx", "/api/v1/buyers/export.xlsx",
                    "/api/v1/export-analysis/export.xlsx", "/api/v1/costing/export.xlsx",
                    "/api/v1/audit/export.xlsx"):
            r = c.get(url)
            assert r.status_code == 200, (url, r.text[:80])
            assert "spreadsheetml.sheet" in r.headers["content-type"]
            assert r.content[:2] == b"PK"  # magic zip
            import io
            import zipfile
            names = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
            assert "xl/workbook.xml" in names and "xl/worksheets/sheet1.xml" in names


def test_dashboard_summary_menyertakan_rincian_role():
    with TestClient(app) as c:
        _login(c)
        r = c.get("/api/v1/business-profiles/dashboard/summary/")
        assert r.status_code == 200
        counts = r.json()["data"]["counts"]
        assert "products_without_catalog" in counts
        assert "catalogs_published" in counts
        assert "catalogs_draft" in counts
        assert "buyer_requests_pending" in counts
        assert "educational_modules" in counts
        assert "educational_articles" in counts


def test_buyer_request_matched_umkm_dan_pilih_katalog():
    """Alur Buyer: matching -> matched-umkm -> pilih katalog -> close request.

    Diadaptasi dari alur ExportReadyAI-fe buyer-requests/[id] (SelectCatalogModal).
    """
    from app import db as app_db
    with TestClient(app) as c:
        _login(c)
        # siapkan produk + katalog published + buyer request
        prod = c.post("/api/v1/products/", json={"name": "Kopi Gayo", "category": "Food & Beverage", "origin": "Aceh"}).json()["data"]
        cat = c.post("/api/v1/catalogs/", json={
            "title": "Katalog Kopi", "productId": prod["id"], "targetMarket": "JP", "moq": "100",
        }).json()["data"]
        c.post(f"/api/v1/catalogs/{cat['id']}/publish/")
        buyers = c.get("/api/v1/buyers/").json()["data"]
        req = c.post("/api/v1/buyer-requests/", json={
            "subject": "Permintaan kopi untuk Jepang",
            "buyerId": buyers[0]["id"], "productId": prod["id"],
            "destination": "Japan", "quantity": "1000", "deadline": "2026-12-31",
            "product_category": "Makanan Olahan",
        }).json()["data"]

        # matching
        matched = c.post(f"/api/v1/buyer-requests/{req['id']}/match/")
        assert matched.status_code == 200
        assert matched.json()["data"]["status"] == "Matched"

        # matched-umkm memperkaya data kontak
        umkm = c.get(f"/api/v1/buyer-requests/{req['id']}/matched-umkm/")
        assert umkm.status_code == 200
        assert umkm.json()["data"]  # setidaknya satu match

        # pilih katalog -> close request dengan selected_catalog + umkm
        match = umkm.json()["data"][0]
        closed = c.patch(f"/api/v1/buyer-requests/{req['id']}/status/", json={
            "status": "Closed",
            "selected_catalog_id": match.get("catalogId", cat["id"]),
            "umkm_id": match.get("umkm_id", ""),
        })
        assert closed.status_code == 200
        assert closed.json()["data"]["status"] == "Closed"
        assert closed.json()["data"]["selectedCatalog"] == match.get("catalogId", cat["id"])
