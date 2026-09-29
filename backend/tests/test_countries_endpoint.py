"""Test endpoint /countries/ sebagai sumber tunggal daftar negara dunia.

Memastikan daftar negara yang dipakai semua input select (frontend) konsisten:
kode ISO unik, nama kanonik terisi, dan mencakup seluruh negara dunia.
"""
import contextlib

from fastapi.testclient import TestClient

from app.data.world_countries import WORLD_COUNTRIES
from app.main import app


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        yield c


def test_countries_endpoint_returns_world_list():
    with _client() as c:
        res = c.get("/api/v1/countries/")
        assert res.status_code == 200
        items = res.json()["data"]
        # Seluruh negara dunia ada (minimal jumlah WORLD_COUNTRIES).
        assert len(items) >= len(WORLD_COUNTRIES)
        codes = {i["country_code"] for i in items}
        assert {"ID", "JP", "US", "DE", "SG"}.issubset(codes)


def test_countries_have_consistent_code_and_name():
    with _client() as c:
        items = c.get("/api/v1/countries/").json()["data"]
    seen = set()
    for item in items:
        code = item.get("country_code")
        name = item.get("country_name")
        assert code and isinstance(code, str) and len(code) == 2
        assert name and isinstance(name, str) and name.strip()
        # Tidak ada kode duplikat (satu entri per negara).
        assert code not in seen, f"kode duplikat: {code}"
        seen.add(code)


def test_country_names_match_master_data():
    """Nama kanonik di endpoint == nama di master WORLD_COUNTRIES (tanpa drift)."""
    master = {c["country_code"]: c["country_name"] for c in WORLD_COUNTRIES}
    with _client() as c:
        items = c.get("/api/v1/countries/").json()["data"]
    for item in items:
        code = item["country_code"]
        if code in master:
            assert item["country_name"] == master[code], f"nama tidak sinkron untuk {code}"


def test_countries_search_filter():
    with _client() as c:
        items = c.get("/api/v1/countries/", params={"search": "japan"}).json()["data"]
    assert any(i["country_code"] == "JP" for i in items)
    # Semua hasil memuat kata kunci di nama/kode.
    for i in items:
        assert "japan" in (i["country_name"] + i["country_code"]).lower()
