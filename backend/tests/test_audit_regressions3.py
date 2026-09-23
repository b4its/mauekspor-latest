"""Regresi audit ronde-3: logger, IDOR review/chat, region_of nama negara,
seed tidak saling menimpa, dan validasi numerik input."""
from fastapi.testclient import TestClient

from app.main import app
from app import db

ADMIN = ("admin@mauekspor.example", "admin123")
BUYER = ("aya@hikari.example", "buyer123")
EXPORTER = ("rizal@kopigayo.example", "rizal123")


def _login(c: TestClient, creds=ADMIN) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_logger_terdefinisi_di_routes():
    """`logger` dipakai di routes.py; sebelumnya NameError -> 500 saat AI down."""
    from app.api import routes
    assert getattr(routes, "logger", None) is not None


def test_region_of_menerima_nama_negara():
    """Destinasi free-text ('Japan') sebelumnya selalu dianggap Asia."""
    from app.data.countries import region_of
    assert region_of("Japan") == "Asia"
    assert region_of("Germany") == "Europe"
    assert region_of("DE") == "Europe"
    assert region_of("United States") in {"Americas", "North America"}


def test_forwarder_review_update_idor_ditolak():
    with TestClient(app) as c:
        exporter_token = _login(c, EXPORTER)  # U-002
        # review milik user lain
        db.insert("forwarder_reviews", {
            "id": "REV-IDOR", "forwarderId": "FWD-NGL", "rating": 5,
            "reviewText": "punya orang lain", "umkmId": "U-999",
        })
        r = c.put("/api/v1/forwarders/FWD-NGL/reviews/REV-IDOR/",
                  json={"rating": 1, "review_text": "dibajak"}, headers=_auth(exporter_token))
        assert r.status_code == 403, r.text
        r2 = c.delete("/api/v1/forwarders/FWD-NGL/reviews/REV-IDOR/delete/", headers=_auth(exporter_token))
        assert r2.status_code == 403, r2.text


def test_forwarder_review_update_oleh_pemilik_dan_admin():
    with TestClient(app) as c:
        exporter_token = _login(c, EXPORTER)
        db.insert("forwarder_reviews", {
            "id": "REV-OWN", "forwarderId": "FWD-NGL", "rating": 5,
            "reviewText": "milik U-002", "umkmId": "U-002",
        })
        r = c.put("/api/v1/forwarders/FWD-NGL/reviews/REV-OWN/",
                  json={"rating": 4, "review_text": "diperbarui"}, headers=_auth(exporter_token))
        assert r.status_code == 200, r.text
        admin_token = _login(c, ADMIN)
        db.insert("forwarder_reviews", {
            "id": "REV-OTHER", "forwarderId": "FWD-NGL", "rating": 3,
            "reviewText": "milik U-999", "umkmId": "U-999",
        })
        r2 = c.put("/api/v1/forwarders/FWD-NGL/reviews/REV-OTHER/",
                   json={"rating": 2, "review_text": "admin"}, headers=_auth(admin_token))
        assert r2.status_code == 200, r2.text


def test_chat_session_tidak_bocor_antar_user():
    with TestClient(app) as c:
        buyer_token = _login(c, BUYER)  # U-003
        # sesi milik user lain
        db.insert("chat_sessions", {"id": "CHS-OTHER", "title": "rahasia",
                                    "messages": [{"role": "user", "text": "x"}], "userId": "U-999"})
        listed = c.get("/api/v1/chat/sessions/", headers=_auth(buyer_token)).json()["data"]
        assert all(s["id"] != "CHS-OTHER" for s in listed), "sesi user lain bocor"
        assert c.get("/api/v1/chat/sessions/CHS-OTHER/", headers=_auth(buyer_token)).status_code == 404
        assert c.delete("/api/v1/chat/sessions/CHS-OTHER/", headers=_auth(buyer_token)).status_code == 404


def test_chat_session_create_menyimpan_userId():
    with TestClient(app) as c:
        token = _login(c, BUYER)
        created = c.post("/api/v1/chat/sessions/", json={"title": "baru"}, headers=_auth(token)).json()["data"]
        assert created.get("userId") == "U-003"


def test_seed_tidak_saling_menimpa():
    """seed_large harus memakai rentang id berbeda dari seed kurasi (001)."""
    with TestClient(app) as c:
        c.get("/api/v1/health")
        # Profil buyer kurasi U-003 harus tetap ada setelah seed_large berjalan
        profile = db.get("buyer_profiles", "BYP-001")
        assert profile is not None, "BYP-001 (kurasi) hilang/tertimpa"
        assert profile.get("userId") == "U-003"
        # review kurasi FWD-NGL tetap ada
        assert db.get("forwarder_reviews", "REV-001") is not None


def test_payment_amount_numerik_garbage_422():
    with TestClient(app) as c:
        token = _login(c)
        payments = c.get("/api/v1/payments/", headers=_auth(token)).json()["data"]
        pid = payments[0]["id"]
        r = c.post(f"/api/v1/payments/{pid}/mark-received/", json={"amount": "abc"}, headers=_auth(token))
        assert r.status_code == 422, r.text
        # format ribuan "42,800" harus diterima
        r2 = c.post(f"/api/v1/payments/{pid}/mark-received/", json={"amount": "42,800"}, headers=_auth(token))
        assert r2.status_code == 200, r2.text


def test_product_pricing_cogs_non_numerik_422():
    with TestClient(app) as c:
        token = _login(c)
        r = c.post("/api/v1/products/PRD-COF-001/ai/pricing/",
                   json={"cogs_per_unit_idr": "bukan-angka"}, headers=_auth(token))
        assert r.status_code == 422, r.text
