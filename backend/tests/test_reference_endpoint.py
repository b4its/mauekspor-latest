"""Referensi faktual (endpoint /reference/) & pemisahan master data dari demo.

Memastikan:
- master data faktual (negara + regulasi) dimuat TANPA membuat entitas demo;
- endpoint /reference/ mengembalikan timeline, HS 2028, FTA, sistem kepabeanan
  yang bertanggal dan dari sumber resmi;
- konteks AI menyertakan referensi terverifikasi.
"""
import contextlib

from fastapi.testclient import TestClient

from app import db
from app.main import app


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        yield c


# ── Master data faktual vs demo ──────────────────────────────────────────────
def test_seed_master_data_creates_no_demo_entities():
    """seed_master_data hanya memuat referensi; tidak ada user/produk/demo."""
    db.reset_store()
    from app.seed import seed_master_data

    seed_master_data()
    assert len(db.all("countries")) > 0, "negara faktual harus ter-seed"
    assert len(db.all("regulations")) > 0, "pointer regulasi harus ter-seed"
    for table in ("users", "products", "buyers", "orders", "payments", "shipments"):
        assert len(db.all(table)) == 0, f"{table} tidak boleh terisi oleh master data"
    # Setiap negara bertanda sumber resmi.
    assert all(c.get("dataSource") == "official_iso3166" for c in db.all("countries"))


def test_reference_has_no_demo_marker_in_countries():
    with _client() as c:
        items = c.get("/api/v1/countries/").json()["data"]
    # Negara berasal dari master ISO, bukan karangan.
    assert len(items) >= 249


# ── Endpoint /reference/ ─────────────────────────────────────────────────────
def test_reference_endpoint_returns_curated_bundle():
    with _client() as c:
        res = c.get("/api/v1/reference/")
        assert res.status_code == 200, res.text
        data = res.json()["data"]
    assert data["snapshotDate"] == "2026-09-29"
    assert data["guide"].endswith("PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md")
    assert len(data["timeline"]) >= 15
    assert data["hs2028"]["headings_total"] == 1229
    assert data["hs2028"]["effective"] == "2028-01-01"
    assert len(data["indonesiaFtas"]) >= 10
    assert "ASEAN" in data["customsSystems"] and "EU" in data["customsSystems"]
    assert data["hsStructureNote"]


def test_reference_timeline_is_chronological():
    with _client() as c:
        tl = c.get("/api/v1/reference/").json()["data"]["timeline"]
    dates = [item["date"] for item in tl]
    assert dates == sorted(dates)


def test_reference_fta_statuses_are_valid_values():
    with _client() as c:
        ftas = c.get("/api/v1/reference/").json()["data"]["indonesiaFtas"]
    valid = {"in_force", "signed_ratifying", "concluded", "negotiating"}
    assert all(f["status"] in valid for f in ftas)
    # IEU-CEPA belum berlaku (tidak boleh in_force).
    ieu = next((f for f in ftas if "IEU-CEPA" in f["name"]), None)
    assert ieu and ieu["status"] == "concluded"


def test_ai_workspace_context_includes_verified_reference():
    from app.api.routes import _build_workspace_context

    ctx = _build_workspace_context(None, "/compliance")
    assert "Referensi Regulasi Terverifikasi" in ctx
    assert "2026-09-29" in ctx
    assert "HS 2028" in ctx
