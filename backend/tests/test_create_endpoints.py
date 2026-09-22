"""Test endpoint create (POST) yang baru ditambahkan untuk modul yang
sebelumnya tidak punya cara membuat record: suppliers, payments, shipments,
tasks, documents, compliance.

Sebelumnya halaman list memakai tombol "buat" yang menyasar record seed
hardcoded. File ini mengunci kontrak create nyata.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import db

EXPORTER = ("rizal@kopigayo.example", "rizal123")


def _login(c: TestClient, creds=EXPORTER) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


# (label, table, path, payload, expected_field, expected_value)
CASES = [
    ("suppliers", "suppliers", "/suppliers", {"name": "PT Uji", "location": "Bali", "category": "Processor"},
     "name", "PT Uji"),
    ("payments", "payments", "/payments", {"buyer": "Buyer X", "amount": 5000, "currency": "USD"},
     "amount", 5000),
    ("shipments", "shipments", "/shipments", {"forwarder": "NGL", "route": "Priok-Yokohama", "mode": "Ocean LCL"},
     "forwarder", "NGL"),
    ("tasks", "tasks", "/tasks", {"title": "Uji task", "module": "Compliance", "priority": "High"},
     "title", "Uji task"),
    ("documents", "documents", "/documents", {"type": "Packing List", "projectId": "EXP-1"},
     "type", "Packing List"),
]


@pytest.mark.parametrize("label,table,path,payload,field,value", CASES,
                         ids=[c[0] for c in CASES])
def test_create_record(label, table, path, payload, field, value):
    with TestClient(app) as c:
        t = _login(c)
        before = len(db.all(table))
        r = c.post(f"/api/v1{path}/", json=payload, headers=_auth(t))
        assert r.status_code == 200, f"{label}: {r.text}"
        data = r.json()["data"]
        assert data[field] == value, f"{label} field {field}={data.get(field)}"
        assert db.get(table, data["id"]) is not None
        assert len(db.all(table)) == before + 1


def test_create_compliance_requirement():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/compliance/requirements/",
                   json={"title": "Izin BPOM", "category": "Labeling", "severity": "High"},
                   headers=_auth(t))
        assert r.status_code == 200, r.text
        rid = r.json()["data"]["id"]
        assert r.json()["data"]["title"] == "Izin BPOM"
        assert db.get("compliance_requirements", rid) is not None


def test_create_requires_title_422():
    with TestClient(app) as c:
        t = _login(c)
        for path in ("/api/v1/tasks/", "/api/v1/suppliers/", "/api/v1/compliance/requirements/"):
            r = c.post(path, json={}, headers=_auth(t))
            assert r.status_code == 422, f"{path}: {r.text}"


def test_create_requires_auth():
    with TestClient(app) as c:
        r = c.post("/api/v1/tasks/", json={"title": "x"})
        assert r.status_code == 401
        assert db.get_by("tasks", title="x") is None
