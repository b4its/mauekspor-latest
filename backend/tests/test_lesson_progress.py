"""Progres belajar per-user pada modul edukasi."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient, email: str = "admin@mauekspor.example", password: str = "admin123") -> str:
    res = c.post("/api/v1/auth/login/", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _first_module_id(c: TestClient, token: str) -> str:
    res = c.get("/api/v1/educational/modules/", headers=_auth(token))
    assert res.status_code == 200, res.text
    data = res.json()["data"]
    assert data, "perlu minimal 1 modul seed"
    return data[0]["id"]


def test_lesson_progress_starts_empty():
    with TestClient(app) as c:
        token = _login(c)
        module_id = _first_module_id(c, token)
        res = c.get(f"/api/v1/educational/modules/{module_id}/progress/", headers=_auth(token))
        assert res.status_code == 200, res.text
        assert res.json()["data"]["completedLessonIds"] == []


def test_lesson_progress_roundtrip():
    with TestClient(app) as c:
        token = _login(c)
        module_id = _first_module_id(c, token)
        lesson_id = "lesson-abc-1"

        done = c.post(
            f"/api/v1/educational/modules/{module_id}/lessons/{lesson_id}/complete/",
            json={"completed": True},
            headers=_auth(token),
        )
        assert done.status_code == 200, done.text
        assert done.json()["data"]["completed"] is True

        listed = c.get(f"/api/v1/educational/modules/{module_id}/progress/", headers=_auth(token))
        assert lesson_id in listed.json()["data"]["completedLessonIds"]

        # Tandai belum selesai -> hilang dari daftar.
        undone = c.post(
            f"/api/v1/educational/modules/{module_id}/lessons/{lesson_id}/complete/",
            json={"completed": False},
            headers=_auth(token),
        )
        assert undone.status_code == 200, undone.text
        listed2 = c.get(f"/api/v1/educational/modules/{module_id}/progress/", headers=_auth(token))
        assert lesson_id not in listed2.json()["data"]["completedLessonIds"]


def test_lesson_progress_requires_auth():
    # Klien baru tanpa sesi → endpoint butuh auth.
    with TestClient(app) as c:
        token = _login(c)
        module_id = _first_module_id(c, token)
        token_cookie = c.cookies
    with TestClient(app) as anon:
        res = anon.get(f"/api/v1/educational/modules/{module_id}/progress/")
        assert res.status_code in (401, 403), res.text
        assert token_cookie is not None


def test_complete_lesson_unknown_module_404():
    with TestClient(app) as c:
        token = _login(c)
        res = c.post(
            "/api/v1/educational/modules/NOPE/lessons/x/complete/",
            json={"completed": True},
            headers=_auth(token),
        )
        assert res.status_code == 404, res.text
