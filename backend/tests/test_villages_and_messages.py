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
    """Kesiapan desa dihitung dari profil pengelola, bukan input manual."""
    with TestClient(app) as c:
        t = _login(c)
        # Profil pengelola lengkap → skor tinggi (>=80) tanpa mengirim readiness.
        db.insert("business_profiles", {
            "id": "BIZ-REJE-GAYO", "companyName": "BUMDes Reje Gayo",
            "address": "Desa Kopi Reje Gayo, Aceh Tengah", "productionCapacity": "10 ton / bulan",
            "yearEstablished": 2018, "certifications": ["Halal", "Origin declaration"],
            "status": "Complete", "owner": "Reje",
        })
        # 1. Create village (tanpa field readiness manual)
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
                "businessProfileId": "BIZ-REJE-GAYO",
            },
            headers=_auth(t)
        )
        assert create_res.status_code == 200
        body = create_res.json()["data"]
        v_id = body["id"]
        assert v_id.startswith("DES")
        # Skor dihitung dari profil → lengkap → Siap Ekspor.
        assert body["readiness"] >= 80
        assert body["status"] == "Siap Ekspor"
        assert body["readinessSource"] == "profile"

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

        # 4. Update village: readiness dari klien diabaikan, tetap hasil hitung.
        update_res = c.put(
            f"/api/v1/villages/{v_id}/",
            json={"production": "15 ton / bulan", "readiness": 1},
            headers=_auth(t)
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["production"] == "15 ton / bulan"
        assert update_res.json()["data"]["readiness"] >= 80

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


def test_villages_readiness_filter_matches_computed_score():
    """?readiness=<angka> menyaring skor yang dihitung dari profil pengelola."""
    with TestClient(app) as c:
        t = _login(c)
        # Profil lengkap → skor tinggi; profil kosong → skor rendah.
        db.insert("business_profiles", {
            "id": "BIZ-R-HIGH", "companyName": "Koperasi Tinggi", "address": "Desa A",
            "productionCapacity": "1 ton", "yearEstablished": 2015,
            "certifications": ["Halal", "SVLK", "Organic"], "status": "Complete", "owner": "X",
        })
        db.insert("business_profiles", {
            "id": "BIZ-R-LOW", "companyName": "Koperasi Rendah", "address": "Desa B",
            "productionCapacity": "", "yearEstablished": None,
            "certifications": [], "status": "Draft", "owner": "",
        })
        high_score = compliance_ready_score("BIZ-R-HIGH")
        db.insert("villages", {"id": "DES-R-HIGH", "name": "Ready",
                               "businessProfileId": "BIZ-R-HIGH"})
        db.insert("villages", {"id": "DES-R-LOW", "name": "Assist",
                               "businessProfileId": "BIZ-R-LOW"})
        res = c.get(f"/api/v1/villages/?readiness={high_score}", headers=_auth(t))
        assert res.status_code == 200
        ids = {v["id"] for v in res.json()["data"]}
        assert "DES-R-HIGH" in ids and "DES-R-LOW" not in ids
        # Fallback label status tetap didukung.
        res2 = c.get("/api/v1/villages/?readiness=Butuh%20Pendampingan", headers=_auth(t))
        ids2 = {v["id"] for v in res2.json()["data"]}
        assert "DES-R-LOW" in ids2


def compliance_ready_score(profile_id: str) -> int:
    from app.services import readiness as readiness_svc
    return readiness_svc.profile_readiness(db.get("business_profiles", profile_id))


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
