"""Test CRUD lengkap untuk modul workspace: automations, integrations,
templates, knowledge, team, calendar, files, support.

Sebelumnya modul-modul ini hanya punya list + satu aksi (activate/connect/
publish) tanpa create/update/delete, sehingga UI tidak bisa mengelola data
sepenuhnya. File ini mengunci kontrak CRUD yang baru.
"""
from fastapi.testclient import TestClient

from app.main import app
from app import db

ADMIN = ("admin@mauekspor.example", "admin123")
EXPORTER = ("rizal@kopigayo.example", "rizal123")
BUYER = ("aya@hikari.example", "buyer123")


def _login(c: TestClient, creds=EXPORTER) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- AUTOMATIONS ----------
def test_automation_crud_lengkap():
    with TestClient(app) as c:
        t = _login(c)
        # create
        r = c.post("/api/v1/automations/", json={
            "name": "Kirim reminder saat dokumen telat",
            "trigger": "Status Change", "action": "Send Notification",
            "module": "Documents", "description": "test",
        }, headers=_auth(t))
        assert r.status_code == 200, r.text
        aid = r.json()["data"]["id"]
        assert r.json()["data"]["status"] == "Paused"
        assert db.get("automations", aid) is not None

        # get
        assert c.get(f"/api/v1/automations/{aid}/", headers=_auth(t)).status_code == 200

        # update
        r = c.patch(f"/api/v1/automations/{aid}/", json={"name": "Nama baru", "status": "Active"},
                    headers=_auth(t))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["name"] == "Nama baru"

        # pause / activate
        assert c.post(f"/api/v1/automations/{aid}/pause/", headers=_auth(t)).json()["data"]["status"] == "Paused"
        assert c.post(f"/api/v1/automations/{aid}/activate/", headers=_auth(t)).json()["data"]["status"] == "Active"

        # run
        r = c.post(f"/api/v1/automations/{aid}/run/", headers=_auth(t))
        assert r.json()["data"]["runs"] == 1

        # delete
        assert c.delete(f"/api/v1/automations/{aid}/", headers=_auth(t)).status_code == 200
        assert db.get("automations", aid) is None


def test_automation_create_tanpa_nama_422():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/automations/", json={"trigger": "x"}, headers=_auth(t))
        assert r.status_code == 422, r.text


def test_automation_update_delete_404():
    with TestClient(app) as c:
        t = _login(c)
        assert c.patch("/api/v1/automations/AUT-NOPE/", json={"name": "x"}, headers=_auth(t)).status_code == 404
        assert c.delete("/api/v1/automations/AUT-NOPE/", headers=_auth(t)).status_code == 404


# ---------- INTEGRATIONS ----------
def test_integration_crud_lengkap():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/integrations/", json={
            "name": "Shopify Sync", "category": "E-commerce Platform",
            "description": "sync orders", "scopes": ["read_orders"],
        }, headers=_auth(t))
        assert r.status_code == 200, r.text
        iid = r.json()["data"]["id"]
        assert r.json()["data"]["status"] == "Disconnected"

        assert c.get(f"/api/v1/integrations/{iid}/", headers=_auth(t)).status_code == 200

        r = c.patch(f"/api/v1/integrations/{iid}/", json={"name": "Shopify Sync v2"}, headers=_auth(t))
        assert r.json()["data"]["name"] == "Shopify Sync v2"

        assert c.post(f"/api/v1/integrations/{iid}/connect/", headers=_auth(t)).json()["data"]["status"] == "Connected"
        assert c.post(f"/api/v1/integrations/{iid}/disconnect/", headers=_auth(t)).json()["data"]["status"] == "Disconnected"
        assert c.post(f"/api/v1/integrations/{iid}/sync/", headers=_auth(t)).json()["data"]["lastSync"] == "now"

        assert c.delete(f"/api/v1/integrations/{iid}/", headers=_auth(t)).status_code == 200
        assert db.get("integrations", iid) is None


def test_integration_create_tanpa_nama_422():
    with TestClient(app) as c:
        t = _login(c)
        assert c.post("/api/v1/integrations/", json={}, headers=_auth(t)).status_code == 422


# ---------- TEMPLATES ----------
def test_template_crud_lengkap():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/templates/", json={"title": "Invoice V2", "category": "Document",
                                               "description": "desc"}, headers=_auth(t))
        assert r.status_code == 200, r.text
        tid = r.json()["data"]["id"]
        assert r.json()["data"]["usedCount"] == 0

        assert c.get(f"/api/v1/templates/{tid}/", headers=_auth(t)).status_code == 200

        r = c.patch(f"/api/v1/templates/{tid}/", json={"title": "Invoice V3", "status": "Ready"},
                    headers=_auth(t))
        assert r.json()["data"]["title"] == "Invoice V3"

        r = c.post(f"/api/v1/templates/{tid}/use/", headers=_auth(t))
        assert r.json()["data"]["usedCount"] == 1

        assert c.delete(f"/api/v1/templates/{tid}/", headers=_auth(t)).status_code == 200
        assert db.get("templates", tid) is None


def test_template_update_delete_404():
    with TestClient(app) as c:
        t = _login(c)
        assert c.patch("/api/v1/templates/TPL-NOPE/", json={"title": "x"}, headers=_auth(t)).status_code == 404
        assert c.delete("/api/v1/templates/TPL-NOPE/", headers=_auth(t)).status_code == 404


# ---------- KNOWLEDGE ----------
def test_knowledge_crud_lengkap():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/knowledge/", json={
            "title": "Panduan Pajak Ekspor", "category": "Regulation",
            "summary": "ringkasan", "steps": ["Langkah 1"], "readTime": "7 min",
        }, headers=_auth(t))
        assert r.status_code == 200, r.text
        kid = r.json()["data"]["id"]
        assert r.json()["data"]["status"] == "Draft"

        assert c.get(f"/api/v1/knowledge/{kid}/", headers=_auth(t)).status_code == 200

        r = c.patch(f"/api/v1/knowledge/{kid}/", json={"title": "Panduan Pajak Ekspor 2026"},
                    headers=_auth(t))
        assert r.json()["data"]["title"] == "Panduan Pajak Ekspor 2026"

        r = c.post(f"/api/v1/knowledge/{kid}/publish/", headers=_auth(t))
        assert r.json()["data"]["status"] == "Published"

        assert c.delete(f"/api/v1/knowledge/{kid}/", headers=_auth(t)).status_code == 200
        assert db.get("knowledge_articles", kid) is None


def test_knowledge_create_tanpa_judul_422():
    with TestClient(app) as c:
        t = _login(c)
        assert c.post("/api/v1/knowledge/", json={"summary": "x"}, headers=_auth(t)).status_code == 422


# ---------- TEAM ----------
def test_team_member_update_dan_remove():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/team/invite/", json={"email": "baru@kopigayo.example", "role": "Operations"},
                   headers=_auth(t))
        assert r.status_code == 200, r.text
        mid = r.json()["data"]["id"]
        assert db.get("team_members", mid) is not None

        r = c.patch(f"/api/v1/team/{mid}/", json={"name": "Nama Baru", "role": "Finance"},
                    headers=_auth(t))
        assert r.status_code == 200, r.text
        assert r.json()["data"]["name"] == "Nama Baru"
        assert r.json()["data"]["role"] == "Finance"

        assert c.delete(f"/api/v1/team/{mid}/", headers=_auth(t)).status_code == 200
        assert db.get("team_members", mid) is None
        assert c.delete(f"/api/v1/team/{mid}/", headers=_auth(t)).status_code == 404


# ---------- CALENDAR ----------
def test_calendar_event_update_dan_delete():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/calendar/", json={
            "title": "Deadline Dokumen", "date": "2026-09-01", "time": "10:00",
            "type": "Deadline", "module": "Documents", "notes": "test",
        }, headers=_auth(t))
        assert r.status_code == 200, r.text
        eid = r.json()["data"]["id"]

        r = c.patch(f"/api/v1/calendar/{eid}/", json={"title": "Deadline Baru"}, headers=_auth(t))
        assert r.json()["data"]["title"] == "Deadline Baru"

        assert c.post(f"/api/v1/calendar/{eid}/done/", headers=_auth(t)).json()["data"]["status"] == "Done"
        assert c.delete(f"/api/v1/calendar/{eid}/", headers=_auth(t)).status_code == 200
        assert db.get("calendar_events", eid) is None


# ---------- FILES ----------
def test_file_delete_menghapus_record_dan_berkas_fisik(tmp_path, monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(routes, "UPLOAD_DIR", str(tmp_path))
    with TestClient(app) as c:
        t = _login(c)
        # Buat berkas fisik + record.
        stored = "unit-test-file.pdf"
        (tmp_path / stored).write_bytes(b"%PDF-1.4 test")
        fid = "FIL-DEL-1"
        db.insert("files", {"id": fid, "name": "unit.pdf", "storageName": stored})

        r = c.delete(f"/api/v1/files/{fid}/", headers=_auth(t))
        assert r.status_code == 200, r.text
        assert db.get("files", fid) is None
        assert not (tmp_path / stored).exists(), "berkas fisik harus terhapus"


def test_file_update_dan_delete_404():
    with TestClient(app) as c:
        t = _login(c)
        db.insert("files", {"id": "FIL-UPD", "name": "a.pdf"})
        r = c.patch("/api/v1/files/FIL-UPD/", json={"name": "b.pdf", "status": "Verified"},
                    headers=_auth(t))
        assert r.json()["data"]["name"] == "b.pdf"
        assert c.delete("/api/v1/files/FIL-NOPE/", headers=_auth(t)).status_code == 404


# ---------- SUPPORT ----------
def test_support_update_resolve_delete():
    with TestClient(app) as c:
        t = _login(c)
        r = c.post("/api/v1/support/", json={"subject": "Bug upload", "description": "gagal"},
                   headers=_auth(t))
        assert r.status_code == 200, r.text
        sid = r.json()["data"]["id"]

        r = c.patch(f"/api/v1/support/{sid}/", json={"priority": "High", "owner": "Nadia"},
                    headers=_auth(t))
        assert r.json()["data"]["priority"] == "High"

        assert c.post(f"/api/v1/support/{sid}/resolve/", headers=_auth(t)).json()["data"]["status"] == "Resolved"
        assert c.delete(f"/api/v1/support/{sid}/", headers=_auth(t)).status_code == 200
        assert db.get("support_tickets", sid) is None


# ---------- RBAC ----------
def test_buyer_tidak_boleh_mutasi_automations():
    with TestClient(app) as c:
        bt = _login(c, BUYER)
        r = c.post("/api/v1/automations/", json={"name": "x"}, headers=_auth(bt))
        assert r.status_code == 403, r.text


def test_delete_requires_auth():
    with TestClient(app) as c:
        db.insert("automations", {"id": "AUT-ANON", "name": "x"})
        assert c.delete("/api/v1/automations/AUT-ANON/").status_code == 401
        assert db.get("automations", "AUT-ANON") is not None
