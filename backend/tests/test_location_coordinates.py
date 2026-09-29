"""Test penyimpanan koordinat lokasi (lat/lng) & alamat pada profil bisnis dan desa.

Fitur peta pemilih lokasi: titik yang dipilih di peta mengisi latitude/longitude
otomatis dan alamat hasil reverse-geocoding. Endpoint harus menyimpan & membaca
kembali nilai tersebut.
"""
import contextlib

from fastapi.testclient import TestClient

from app.main import app


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        yield c


# ── Business profile ──────────────────────────────────────────────────────────
def test_create_business_profile_persists_coordinates():
    with _client() as c:
        res = c.post(
            "/api/v1/business-profiles/",
            json={
                "companyName": "PT Uji Lokasi",
                "address": "Bebesen, Aceh Tengah, Aceh, Indonesia",
                "latitude": 4.6306,
                "longitude": 96.8474,
                "productionCapacity": "1 ton/bulan",
                "yearEstablished": 2019,
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        pid = data["id"]
        assert data["latitude"] == 4.6306
        assert data["longitude"] == 96.8474

        # Terbaca kembali lewat GET.
        got = c.get(f"/api/v1/business-profiles/{pid}/").json()["data"]
        assert got["latitude"] == 4.6306
        assert got["longitude"] == 96.8474
        assert "Bebesen" in got["address"]


def test_patch_business_profile_updates_coordinates():
    with _client() as c:
        pid = c.post(
            "/api/v1/business-profiles/",
            json={"companyName": "PT Patch Lokasi", "address": "Medan"},
        ).json()["data"]["id"]
        res = c.patch(
            f"/api/v1/business-profiles/{pid}/",
            json={"latitude": -6.2, "longitude": 106.8166, "address": "Jakarta, Indonesia"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["latitude"] == -6.2
        assert data["longitude"] == 106.8166
        assert data["address"] == "Jakarta, Indonesia"


def test_business_profile_coordinates_optional():
    with _client() as c:
        res = c.post(
            "/api/v1/business-profiles/",
            json={"companyName": "PT Tanpa Koordinat", "address": "Bandung"},
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        # Tidak wajib: absen/kosong tetap boleh.
        assert data.get("latitude") in (None, 0, 0.0) or "latitude" not in data


# ── Villages ──────────────────────────────────────────────────────────────────
def test_create_village_persists_coordinates_and_address():
    with _client() as c:
        res = c.post(
            "/api/v1/villages/",
            json={
                "name": "Desa Uji Peta",
                "region": "Aceh Tengah",
                "province": "Aceh",
                "flagshipCommodity": "Kopi",
                "organization": "BUMDes Uji",
                "lat": 4.6306,
                "lng": 96.8474,
                "address": "Bebesen, Aceh Tengah, Aceh, Indonesia",
            },
        )
        assert res.status_code == 200, res.text
        vid = res.json()["data"]["id"]
        got = c.get(f"/api/v1/villages/{vid}/").json()["data"]
        assert got["lat"] == 4.6306
        assert got["lng"] == 96.8474
        assert got["address"] == "Bebesen, Aceh Tengah, Aceh, Indonesia"


def test_update_village_rejects_out_of_range_coordinates():
    with _client() as c:
        vid = c.post(
            "/api/v1/villages/",
            json={"name": "Desa Rentang", "flagshipCommodity": "Kopi", "organization": "BUMDes"},
        ).json()["data"]["id"]
        bad = c.put(f"/api/v1/villages/{vid}/", json={"lat": 120, "lng": 200})
        assert bad.status_code == 422


def test_village_appears_in_map_points_after_coordinates_set():
    with _client() as c:
        c.post(
            "/api/v1/villages/",
            json={
                "name": "Desa Titik Peta",
                "region": "Bali",
                "province": "Bali",
                "flagshipCommodity": "Vanili",
                "organization": "BUMDes Bali",
                "lat": -8.5955,
                "lng": 115.1121,
            },
        )
        points = c.get("/api/v1/villages/map/").json()["data"]
        assert any(p["name"] == "Desa Titik Peta" for p in points)
