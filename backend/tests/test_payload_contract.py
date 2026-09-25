"""Kontrak payload runtime: kirim body persis seperti frontend (src/lib/api/*.ts) dan pastikan diterima tanpa 422/500 serta data tersimpan benar."""
from fastapi.testclient import TestClient

from app.main import app
from app import db  # noqa: F401


def _login(c) -> None:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200, res.text


def test_costing_create_accepts_frontend_payload_with_title():
    with TestClient(app) as c:
        _login(c)
        payload = {
            "title": "Japan Coffee FOB Base Case",
            "projectId": "",
            "productId": "PRD-COF-001",
            "incoterm": "FOB",
            "margin": 22,
            "destination": "Japan",
        }
        res = c.post("/api/v1/costing/", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["title"] == payload["title"]
        assert data["margin"] == 22
        # Kalkulasi nyata (EXW/FOB/CIF) langsung menghasilkan status Ready + harga
        assert data["status"] == "Ready"
        assert data["exwPrice"] > 0
        assert data["fobPrice"] > 0
        assert data["cifPrice"] > 0
        assert data["exchangeRate"] > 0


def test_compliance_evidence_accepts_note_key():
    with TestClient(app) as c:
        _login(c)
        req_id = c.get("/api/v1/compliance/requirements/").json()["data"][0]["id"]
        res = c.post(
            f"/api/v1/compliance/requirements/{req_id}/evidence/",
            json={"requirementId": req_id, "note": "Lab report QR uploaded", "fileName": "lab.pdf"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["currentEvidence"] == "Lab report QR uploaded"
        assert data["evidenceFile"] == "lab.pdf"


def test_shipment_exception_resolve_persists_note_and_owner():
    with TestClient(app) as c:
        _login(c)
        shipment_id = c.get("/api/v1/shipments/").json()["data"][0]["id"]
        payload = {"shipmentId": shipment_id, "note": "Customs docs corrected", "owner": "Operations"}
        res = c.post(f"/api/v1/shipments/{shipment_id}/exceptions/resolve/", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["status"] == "In Transit"
        assert data["lastExceptionResolution"]["note"] == "Customs docs corrected"
        assert data["lastExceptionResolution"]["owner"] == "Operations"


def test_quotation_create_accepts_extra_frontend_keys():
    with TestClient(app) as c:
        _login(c)
        payload = {"rfqId": "RFQ-JP-001", "incoterm": "CIF", "value": 1000, "currency": "USD", "validUntil": "2026-09-01"}
        res = c.post("/api/v1/quotations/", json=payload)
        assert res.status_code == 200, res.text


def test_order_create_accepts_extra_frontend_keys():
    with TestClient(app) as c:
        _login(c)
        payload = {"quotationId": "Q-001", "paymentTerms": "30% deposit", "deliveryWindow": "4 weeks"}
        res = c.post("/api/v1/orders/", json=payload)
        assert res.status_code == 200, res.text


def test_shipment_milestone_accepts_frontend_payload():
    with TestClient(app) as c:
        _login(c)
        shipment_id = c.get("/api/v1/shipments/").json()["data"][0]["id"]
        res = c.post(f"/api/v1/shipments/{shipment_id}/milestones/", json={"milestone": "Booking Requested"})
        assert res.status_code == 200, res.text
        milestones = res.json()["data"]["milestones"]
        assert milestones[-1]["label"] == "Booking Requested"


def test_buyer_request_requirements_list_roundtrip():
    with TestClient(app) as c:
        _login(c)
        payload = {
            "subject": "Trial shipment for Gayo Arabica coffee",
            "buyerId": "BUY-HIKARI-JP",
            "productId": "PRD-COF-001",
            "destination": "Japan",
            "quantity": "2,000 bags",
            "deadline": "2026-08-12",
            "requirements": ["Japanese label", "Lab report", "FOB quote"],
        }
        res = c.post("/api/v1/buyer-requests/", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["requirements"] == payload["requirements"]
        assert data["subject"] == payload["subject"]


def test_mark_payment_received_accepts_empty_body():
    """Frontend memanggil POST mark-received tanpa body — harus 200, bukan 422."""
    with TestClient(app) as c:
        _login(c)
        payment_id = c.get("/api/v1/payments/").json()["data"][0]["id"]
        res = c.post(f"/api/v1/payments/{payment_id}/mark-received/")
        assert res.status_code == 200, res.text
        assert res.json()["data"]["status"] in {"Settled", "Deposit Paid"}


def test_mark_payment_received_accepts_amount_body():
    with TestClient(app) as c:
        _login(c)
        payment_id = c.get("/api/v1/payments/").json()["data"][0]["id"]
        res = c.post(f"/api/v1/payments/{payment_id}/mark-received/", json={"amount": 1000})
        assert res.status_code == 200, res.text
        assert res.json()["data"]["paid"] == 1000


def test_update_market_persists_country_and_product():
    """Editor market mengirim {country, productId, ...} — field ini harus tersimpan."""
    with TestClient(app) as c:
        _login(c)
        market_id = c.get("/api/v1/markets/").json()["data"][0]["id"]
        res = c.patch(
            f"/api/v1/markets/{market_id}/",
            json={"country": "Germany", "productId": "PRD-COF-001", "status": "Watchlist"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["country"] == "Germany"
        assert data["productId"] == "PRD-COF-001"
        assert data["status"] == "Watchlist"


def test_update_variant_type_preserves_type_code_when_omitted():
    with TestClient(app) as c:
        _login(c)
        catalog_id = c.get("/api/v1/catalogs/").json()["data"][0]["id"]
        created = c.post(
            f"/api/v1/catalogs/{catalog_id}/variant-types/",
            json={"type_code": "color", "type_name": "Warna", "sort_order": 0},
        ).json()["data"]
        assert created["typeCode"] == "color"
        # Update hanya nama — typeCode TIDAK boleh berubah menjadi 'custom'.
        updated = c.put(
            f"/api/v1/catalogs/{catalog_id}/variant-types/{created['id']}/",
            json={"type_name": "Warna Baru"},
        ).json()["data"]
        assert updated["typeName"] == "Warna Baru"
        assert updated["typeCode"] == "color"


def test_export_analysis_dedup_detects_seeded_destination():
    """Analisis seed hanya punya `destination` (nama negara) — dedup harus tetap mendeteksinya."""
    with TestClient(app) as c:
        _login(c)
        # Seed ANL-COF-001 adalah PRD-COF-001 / Japan tanpa countryCode.
        res = c.post(
            "/api/v1/export-analysis/",
            json={"productId": "PRD-COF-001", "destination": "Japan"},
        )
        assert res.status_code == 409, res.text


def test_educational_file_upload_produces_downloadable_url():
    with TestClient(app) as c:
        _login(c)
        article_id = c.get("/api/v1/educational/articles/").json()["data"][0]["id"]
        res = c.post(
            f"/api/v1/educational/articles/{article_id}/upload-file/",
            files={"file": ("catatan.txt", b"hello world", "text/plain")},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["fileUrl"].startswith("/files/")
        assert data["fileUrl"].endswith("/download/")
        dl = c.get(f"/api/v1{data['fileUrl']}")
        assert dl.status_code == 200, dl.text
        assert dl.content == b"hello world"
