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
        assert res.json()["data"]["currentEvidence"] == "Lab report QR uploaded"


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
