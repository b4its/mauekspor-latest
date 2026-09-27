"""Test API aksi kunci lintas modul (publish, qualify, quote, generate, dll)."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["meta"]["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_katalog_publish_unpublish():
    with TestClient(app) as c:
        token = _login(c)
        # buat katalog lalu publish
        created = c.post("/api/v1/catalogs/", json={
            "title": "Katalog Test", "productId": "PRD-COF-001",
            "targetMarket": "JP", "moq": "100",
        }, headers=_headers(token))
        assert created.status_code == 200
        cid = created.json()["data"]["id"]
        pub = c.post(f"/api/v1/catalogs/{cid}/publish/", headers=_headers(token))
        assert pub.status_code == 200
        assert pub.json()["data"]["status"] == "Published"
        unpub = c.post(f"/api/v1/catalogs/{cid}/unpublish/", headers=_headers(token))
        assert unpub.status_code == 200


def test_buyer_qualify_dan_log_contact():
    with TestClient(app) as c:
        token = _login(c)
        buyers = c.get("/api/v1/buyers/", headers=_headers(token)).json()["data"]
        bid = buyers[0]["id"]
        q = c.post(f"/api/v1/buyers/{bid}/qualify/", headers=_headers(token))
        assert q.status_code == 200
        contact = c.post(f"/api/v1/buyers/{bid}/contacts/", json={"note": "Follow-up"}, headers=_headers(token))
        assert contact.status_code == 200


def test_forwarder_request_quote_dan_statistik():
    with TestClient(app) as c:
        token = _login(c)
        fwds = c.get("/api/v1/forwarders/", headers=_headers(token)).json()["data"]
        fid = fwds[0]["id"]
        req = c.post(
            f"/api/v1/forwarders/{fid}/request-quote/",
            json={"lane": "Belawan → Tokyo", "incoterm": "FOB", "cargo": "Kopi Arabika 20ft"},
            headers=_headers(token),
        )
        assert req.status_code == 200
        # Alur utuh: kuotasi benar-benar dibuat, bukan hanya status.
        quote = req.json()["data"]["quote"]
        assert quote["status"] == "Requested"
        assert quote["forwarderId"] == fid
        assert quote["lane"] == "Belawan → Tokyo"
        listed = c.get(f"/api/v1/forwarders/{fid}/quotes/", headers=_headers(token)).json()["data"]
        assert any(q["id"] == quote["id"] for q in listed)
        # Forwarder mencatat hitungan permintaan.
        refreshed = c.get(f"/api/v1/forwarders/{fid}/", headers=_headers(token)).json()["data"]
        assert refreshed["quoteRequestCount"] >= 1
        stats = c.get(f"/api/v1/forwarders/{fid}/statistics/", headers=_headers(token))
        assert stats.status_code == 200
        assert "ratingDistribution" in stats.json()["data"]


def test_forwarder_quote_dan_notifikasi_antar_modul():
    """Permintaan kuotasi harus memunculkan notifikasi & thread pesan terkait."""
    with TestClient(app) as c:
        token = _login(c)
        fid = c.get("/api/v1/forwarders/", headers=_headers(token)).json()["data"][0]["id"]
        before_notif = len(c.get("/api/v1/notifications/", headers=_headers(token)).json()["data"])
        c.post(f"/api/v1/forwarders/{fid}/request-quote/", json={"lane": "Tanjung Priok → Hamburg"}, headers=_headers(token))
        notifs = c.get("/api/v1/notifications/", headers=_headers(token)).json()["data"]
        assert len(notifs) > before_notif
        threads = c.get("/api/v1/messages/", headers=_headers(token)).json()["data"]
        assert any(t.get("relatedModule") == "forwarders" and t.get("relatedId") == fid for t in threads)


def test_payment_send_reminder_tercatat():
    with TestClient(app) as c:
        token = _login(c)
        payments = c.get("/api/v1/payments/", headers=_headers(token)).json()["data"]
        pid = payments[0]["id"]
        res = c.post(f"/api/v1/payments/{pid}/send-reminder/", headers=_headers(token))
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["remindersSent"] >= 1
        assert data.get("lastReminderAt")


def test_dokumen_generate_dan_approve():
    with TestClient(app) as c:
        token = _login(c)
        projects = c.get("/api/v1/trade-projects/", headers=_headers(token)).json()["data"]
        pid = projects[0]["id"]
        gen = c.post("/api/v1/documents/generate/", json={"projectId": pid, "type": "Commercial Invoice"}, headers=_headers(token))
        assert gen.status_code == 200
        doc = gen.json()["data"]
        # approve (jika skor validasi >= threshold; jika gagal, pastikan status bukan 500)
        appr = c.post(f"/api/v1/documents/{doc['id']}/approve/", headers=_headers(token))
        assert appr.status_code in (200, 422)


def test_automation_run_dan_activate():
    with TestClient(app) as c:
        token = _login(c)
        rules = c.get("/api/v1/automations/", headers=_headers(token)).json()["data"]
        rule = rules[0]
        run = c.post(f"/api/v1/automations/{rule['id']}/run/", headers=_headers(token))
        assert run.status_code == 200
        act = c.post(f"/api/v1/automations/{rule['id']}/activate/", headers=_headers(token))
        assert act.status_code == 200


def test_market_refresh():
    with TestClient(app) as c:
        token = _login(c)
        markets = c.get("/api/v1/markets/", headers=_headers(token)).json()["data"]
        if markets:
            mid = markets[0]["id"]
            ref = c.post(f"/api/v1/markets/{mid}/refresh/", headers=_headers(token))
            assert ref.status_code == 200
