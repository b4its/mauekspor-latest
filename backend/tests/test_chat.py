"""Test API chat sessions (list/create/get/delete/send/suggestions)."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["meta"]["access_token"]


def test_chat_sessions_flow():
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}

        # list awal (mungkin ada seed)
        listed = c.get("/api/v1/chat/sessions/", headers=headers)
        assert listed.status_code == 200

        # buat sesi baru
        created = c.post("/api/v1/chat/sessions/", json={"title": "Sesi Test"}, headers=headers)
        assert created.status_code == 200
        session = created.json()["data"]
        sid = session["id"]

        # get by id
        got = c.get(f"/api/v1/chat/sessions/{sid}/", headers=headers)
        assert got.status_code == 200
        assert got.json()["data"]["id"] == sid

        # kirim pesan
        sent = c.post(
            f"/api/v1/chat/sessions/{sid}/messages/",
            json={"text": "Ringkas risiko ekspor kopi ke Jepang"},
            headers=headers,
        )
        assert sent.status_code == 200
        messages = sent.json()["data"].get("messages") or []
        assert any("Ringkas" in (m.get("text") or "") for m in messages)

        # hapus sesi
        deleted = c.delete(f"/api/v1/chat/sessions/{sid}/", headers=headers)
        assert deleted.status_code == 200
        # get setelah hapus -> 404
        assert c.get(f"/api/v1/chat/sessions/{sid}/", headers=headers).status_code == 404


def test_chat_suggestions():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/chat/suggestions/", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert isinstance(res.json()["data"], list)


def test_chat_session_tidak_ada_404():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/chat/sessions/CHAT-TIDAK-ADA/", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404


def test_chat_session_tanpa_auth_tetap_dapat_diakses():
    # Chat read tidak memerlukan auth (module chat readable) — pastikan tidak error
    with TestClient(app) as c:
        res = c.get("/api/v1/chat/sessions/")
        assert res.status_code == 200
