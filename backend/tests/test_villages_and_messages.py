"""Test first-class endpoints untuk modul villages dan messages."""
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


def test_messages_create_and_send_and_resolve():
    with TestClient(app) as c:
        t = _login(c)
        # Create message thread
        create_res = c.post(
            "/api/v1/messages/",
            json={
                "subject": "Penawaran Biji Kopi Gayo",
                "party": "Hikari Foods Co.",
                "channel": "Email",
                "lastMessage": "Halo, kami berminat dengan kopi Anda.",
                "participants": ["rizal@kopigayo.example", "aya@hikari.example"]
            },
            headers=_auth(t)
        )
        assert create_res.status_code == 200
        msg_id = create_res.json()["data"]["id"]
        assert msg_id.startswith("MSG")
        assert create_res.json()["data"]["status"] == "Open"

        # Send follow up message
        send_res = c.post(
            f"/api/v1/messages/{msg_id}/send/",
            json={"body": "Kami kirimkan sampel 1kg besok."},
            headers=_auth(t)
        )
        assert send_res.status_code == 200
        assert send_res.json()["data"]["lastMessage"] == "Kami kirimkan sampel 1kg besok."

        # Resolve message thread
        resolve_res = c.post(
            f"/api/v1/messages/{msg_id}/resolve/",
            headers=_auth(t)
        )
        assert resolve_res.status_code == 200
        assert resolve_res.json()["data"]["status"] == "Resolved"


def test_villages_crud():
    with TestClient(app) as c:
        t = _login(c)
        # 1. Create village
        create_res = c.post(
            "/api/v1/villages/",
            json={
                "name": "Desa Kopi Reje Gayo",
                "region": "Lut Tawar, Aceh Tengah",
                "province": "Aceh",
                "flagshipCommodity": "Kopi Arabika Gayo Specialty",
                "commodityGroup": "pertanian",
                "production": "10 ton / bulan",
                "organization": "BUMDes Reje Gayo",
                "readiness": 88
            },
            headers=_auth(t)
        )
        assert create_res.status_code == 200
        v_id = create_res.json()["data"]["id"]
        assert v_id.startswith("DES")
        assert create_res.json()["data"]["status"] == "Siap Ekspor"

        # 2. List villages with search & filter
        list_res = c.get(f"/api/v1/villages/?search=Reje&province=Aceh", headers=_auth(t))
        assert list_res.status_code == 200
        items = list_res.json()["data"]
        assert any(v["id"] == v_id for v in items)

        # 3. Get village detail
        get_res = c.get(f"/api/v1/villages/{v_id}/", headers=_auth(t))
        assert get_res.status_code == 200
        assert get_res.json()["data"]["name"] == "Desa Kopi Reje Gayo"
        assert "products" in get_res.json()["data"]

        # 4. Update village
        update_res = c.put(
            f"/api/v1/villages/{v_id}/",
            json={"production": "15 ton / bulan", "readiness": 92},
            headers=_auth(t)
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["production"] == "15 ton / bulan"

        # 5. Delete village
        del_res = c.delete(f"/api/v1/villages/{v_id}/", headers=_auth(t))
        assert del_res.status_code == 200
        assert db.get("villages", v_id) is None
