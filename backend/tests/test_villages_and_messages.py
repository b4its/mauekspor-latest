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


def test_village_map_points_hanya_desa_berkoordinat():
    """Peta desa mengambil titik dari tabel; desa tanpa koordinat tidak dikirim."""
    with TestClient(app) as c:
        t = _login(c)
        db.insert("villages", {
            "id": "DES-MAP-1", "name": "Desa Berkordinat", "region": "Aceh",
            "province": "Aceh", "flagshipCommodity": "Kopi", "production": "1 ton",
            "readiness": 85, "status": "Siap Ekspor", "lat": 4.5, "lng": 96.8,
        })
        db.insert("villages", {
            "id": "DES-MAP-2", "name": "Desa Tanpa Koordinat", "region": "Bali",
            "province": "Bali", "flagshipCommodity": "Vanili", "production": "1 kg",
            "readiness": 70, "status": "Butuh Pendampingan",
        })
        res = c.get("/api/v1/villages/map/", headers=_auth(t))
        assert res.status_code == 200, res.text
        points = res.json()["data"]
        ids = {p["id"] for p in points}
        assert "DES-MAP-1" in ids
        assert "DES-MAP-2" not in ids
        point = next(p for p in points if p["id"] == "DES-MAP-1")
        assert point["lat"] == 4.5 and point["lng"] == 96.8
        assert point["commodity"] == "Kopi"


def test_villages_list_with_coords_filter():
    with TestClient(app) as c:
        t = _login(c)
        db.insert("villages", {"id": "DES-C1", "name": "A", "lat": 1.0, "lng": 100.0, "readiness": 80})
        db.insert("villages", {"id": "DES-C2", "name": "B", "readiness": 80})
        res = c.get("/api/v1/villages/?with_coords=1", headers=_auth(t))
        assert res.status_code == 200
        ids = {v["id"] for v in res.json()["data"]}
        assert "DES-C1" in ids and "DES-C2" not in ids


def test_villages_readiness_filter_matches_numeric_score():
    """?readiness=<angka> harus menyaring skor kesiapan numerik, bukan label status."""
    with TestClient(app) as c:
        t = _login(c)
        # Nilai readiness unik agar tidak bentrok dengan data seed demo.
        db.insert("villages", {"id": "DES-R93", "name": "Ready", "readiness": 93,
                               "status": "Siap Ekspor"})
        db.insert("villages", {"id": "DES-R61", "name": "Assist", "readiness": 61,
                               "status": "Butuh Pendampingan"})
        res = c.get("/api/v1/villages/?readiness=93", headers=_auth(t))
        assert res.status_code == 200
        ids = {v["id"] for v in res.json()["data"]}
        assert ids == {"DES-R93"}
        # Fallback label status tetap didukung.
        res2 = c.get("/api/v1/villages/?readiness=Butuh%20Pendampingan", headers=_auth(t))
        ids2 = {v["id"] for v in res2.json()["data"]}
        assert "DES-R61" in ids2


def test_village_coordinate_validation_422():
    with TestClient(app) as c:
        t = _login(c)
        bad = c.post("/api/v1/villages/", json={"name": "X", "lat": "bukan-angka"}, headers=_auth(t))
        assert bad.status_code == 422
        out_of_range = c.post("/api/v1/villages/", json={"name": "Y", "lat": 999}, headers=_auth(t))
        assert out_of_range.status_code == 422
        ok = c.post("/api/v1/villages/", json={"name": "Z", "lat": -6.2, "lng": 106.8}, headers=_auth(t))
        assert ok.status_code == 200
        assert ok.json()["data"]["lat"] == -6.2
