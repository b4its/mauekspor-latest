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
        assert pr["exwPriceUsd"] > 0
        assert pr["fobPriceUsd"] > pr["exwPriceUsd"]
        assert pr["cifPriceUsd"] > pr["fobPriceUsd"]


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
        r = c.get("/api/v1/buyers/my-profile/")
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
