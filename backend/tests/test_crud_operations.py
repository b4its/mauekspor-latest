"""Test CRUD lengkap (update + delete) untuk modul operasional inti.

Modul-modul ini sebelumnya hanya punya list + detail + satu aksi (confirm/
approve/complete/verify), sehingga record tidak bisa diedit atau dihapus sama
sekali. File ini mengunci kontrak PATCH + DELETE yang baru untuk:
orders, payments, quotations, rfqs, shipments, tasks, documents, compliance,
suppliers, markets, reports, trade-projects, buyers, messages, notifications,
business-profiles.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import db

EXPORTER = ("rizal@kopigayo.example", "rizal123")
BUYER = ("aya@hikari.example", "buyer123")


def _login(c: TestClient, creds=EXPORTER) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


# (label, table, base_path, seed_record, patch_payload, patch_field, patch_value)
CASES = [
    ("orders", "orders", "/orders", {"id": "ORD-T1", "buyer": "A", "value": 10},
     {"buyer": "B", "status": "Confirmed"}, "buyer", "B"),
    ("payments", "payments", "/payments", {"id": "PAY-T1", "buyer": "A", "amount": 100},
     {"method": "TT", "status": "Settled"}, "method", "TT"),
    ("quotations", "quotations", "/quotations", {"id": "Q-T1", "buyer": "A", "value": 5},
     {"incoterm": "CIF", "status": "Sent"}, "incoterm", "CIF"),
    ("rfqs", "rfqs", "/rfqs", {"id": "RFQ-T1", "buyer": "A"},
     {"incoterm": "FOB", "quantity": "100"}, "quantity", "100"),
    ("shipments", "shipments", "/shipments", {"id": "SHP-T1", "progress": 0},
     {"status": "In Transit", "container": "MSKU1"}, "container", "MSKU1"),
    ("tasks", "tasks", "/tasks", {"id": "TSK-T1", "title": "T", "status": "Open"},
     {"status": "In Progress", "priority": "High"}, "priority", "High"),
    ("documents", "documents", "/documents", {"id": "DOC-T1", "status": "Draft"},
     {"status": "Approved", "version": "v2"}, "version", "v2"),
    ("suppliers", "suppliers", "/suppliers", {"id": "SUP-T1", "name": "S"},
     {"status": "Verified", "complianceScore": 95}, "complianceScore", 95),
    ("markets", "markets", "/markets", {"id": "MKT-T1", "destination": "JP"},
     {"status": "Researched", "marketScore": 70}, "marketScore", 70),
    ("reports", "reports", "/reports", {"id": "RPT-T1", "title": "R"},
     {"status": "Ready", "period": "Q3"}, "period", "Q3"),
    ("trade-projects", "projects", "/trade-projects", {"id": "EXP-T1", "name": "P"},
     {"stage": "Negotiation", "readiness": 60}, "readiness", 60),
    ("buyers", "buyers", "/buyers", {"id": "BUY-T1", "name": "B"},
     {"status": "Qualified", "segment": "Retail"}, "segment", "Retail"),
    ("messages", "messages", "/messages", {"id": "MSG-T1", "subject": "Hi"},
     {"status": "Resolved", "lastMessage": "ok"}, "lastMessage", "ok"),
]


@pytest.mark.parametrize("label,table,path,seed,patch,field,value", CASES,
                         ids=[c[0] for c in CASES])
def test_update_then_delete(label, table, path, seed, patch, field, value):
    with TestClient(app) as c:
        t = _login(c)
        db.insert(table, dict(seed))
        rid = seed["id"]
        # update
        r = c.patch(f"/api/v1{path}/{rid}/", json=patch, headers=_auth(t))
        assert r.status_code == 200, f"{label} patch: {r.text}"
        assert r.json()["data"][field] == value, f"{label} field {field}"
        # delete
        r = c.delete(f"/api/v1{path}/{rid}/", headers=_auth(t))
        assert r.status_code == 200, f"{label} delete: {r.text}"
        assert db.get(table, rid) is None, f"{label} still present"
        # idempotent 404
        assert c.delete(f"/api/v1{path}/{rid}/", headers=_auth(t)).status_code == 404


@pytest.mark.parametrize("label,table,path,seed,patch,field,value", CASES,
                         ids=[c[0] for c in CASES])
def test_update_delete_missing_404(label, table, path, seed, patch, field, value):
    with TestClient(app) as c:
        t = _login(c)
        assert c.patch(f"/api/v1{path}/{label}-NOPE/", json=patch, headers=_auth(t)).status_code == 404
        assert c.delete(f"/api/v1{path}/{label}-NOPE/", headers=_auth(t)).status_code == 404


def test_compliance_update_delete():
    with TestClient(app) as c:
        t = _login(c)
        db.insert("compliance_requirements", {"id": "REQ-T1", "title": "Izin", "status": "Open"})
        r = c.patch("/api/v1/compliance/requirements/REQ-T1/",
                    json={"status": "Compliant", "severity": "High"}, headers=_auth(t))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["severity"] == "High"
        assert c.delete("/api/v1/compliance/requirements/REQ-T1/", headers=_auth(t)).status_code == 200
        assert db.get("compliance_requirements", "REQ-T1") is None
        assert c.delete("/api/v1/compliance/requirements/REQ-NOPE/", headers=_auth(t)).status_code == 404


def test_notifications_delete():
    with TestClient(app) as c:
        t = _login(c)
        db.insert("notifications", {"id": "NTF-T1", "title": "x", "status": "Unread"})
        assert c.delete("/api/v1/notifications/NTF-T1/", headers=_auth(t)).status_code == 200
        assert db.get("notifications", "NTF-T1") is None
        assert c.delete("/api/v1/notifications/NTF-NOPE/", headers=_auth(t)).status_code == 404


def test_reports_create_update_delete():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/reports/", json={"title": "Laporan Q3", "type": "Summary"}, headers=_auth(t))
        assert r.status_code == 200, r.text
        rid = r.json()["data"]["id"]
        r = c.patch(f"/api/v1/reports/{rid}/", json={"status": "Ready"}, headers=_auth(t))
        assert r.json()["data"]["status"] == "Ready"
        assert c.delete(f"/api/v1/reports/{rid}/", headers=_auth(t)).status_code == 200
        assert db.get("reports", rid) is None


def test_reports_create_tanpa_judul_422():
    with TestClient(app) as c:
        t = _login(c)
        assert c.post("/api/v1/reports/", json={"type": "Summary"}, headers=_auth(t)).status_code == 422


def test_business_profile_delete():
    with TestClient(app) as c:
        t = _login(c)
        db.insert("business_profiles", {"id": "BIZ-T1", "companyName": "X"})
        r = c.delete("/api/v1/business-profiles/BIZ-T1/", headers=_auth(t))
        assert r.status_code == 200, r.text
        assert db.get("business_profiles", "BIZ-T1") is None
        assert c.delete("/api/v1/business-profiles/BIZ-T1/", headers=_auth(t)).status_code == 404


def test_delete_requires_auth():
    with TestClient(app) as c:
        db.insert("orders", {"id": "ORD-ANON", "buyer": "A"})
        assert c.delete("/api/v1/orders/ORD-ANON/").status_code == 401
        assert db.get("orders", "ORD-ANON") is not None


def test_buyer_tidak_boleh_hapus_compliance():
    with TestClient(app) as c:
        bt = _login(c, BUYER)
        db.insert("compliance_requirements", {"id": "REQ-RBAC", "title": "A"})
        # Buyer tidak punya modul 'compliance' di MUTATE_MODULES.
        assert c.delete("/api/v1/compliance/requirements/REQ-RBAC/", headers=_auth(bt)).status_code == 403
        assert db.get("compliance_requirements", "REQ-RBAC") is not None
