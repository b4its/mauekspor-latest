"""Data riil dari panduan 2026 ter-seed sebagai regulations + knowledge_articles.

Memastikan:
- seeder menghasilkan baris faktual ID/US/EU/dll. yang traceable;
- TIDAK ada baris demo legacy ("Regulation for <CODE>.");
- knowledge_articles berisi artikel panduan yang benar-benar ada;
- bundle /reference/ lengkap dan konsisten dengan angka panduan.
"""
import contextlib

from fastapi.testclient import TestClient

from app import db
from app.data import regulatory_guide as g
from app.data.trade_reference import (
    _guide_regulations,
    _guide_knowledge_articles,
    full_reference_bundle,
    seed_regulatory_guide,
)
from app.main import app


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        yield c


# ── Struktur data panduan ────────────────────────────────────────────────────
def test_guide_module_has_core_sections():
    assert g.SNAPSHOT_DATE == "2026-09-29"
    assert len(g.INCOTERMS_2020) == 11
    assert len(g.KUMHS_RULES) == 9
    assert g.HS_2028["headings_total"] == 1229
    assert len(g.US_SECTION_301_FORCED_LABOR["standard_10pct"]) >= 15
    assert "Indonesia" in g.US_SECTION_301_FORCED_LABOR["standard_10pct"]
    assert len(g.ID_FTAS) >= 12
    assert len(g.KEY_TIMELINE) >= 15


def test_guide_timeline_is_chronological():
    dates = [d for d, _ in g.KEY_TIMELINE]
    assert dates == sorted(dates)


# ── Regulasi ter-seed ────────────────────────────────────────────────────────
def test_guide_regulations_are_factual_and_traceable():
    rows = _guide_regulations()
    assert len(rows) >= 40
    codes = {r["countryCode"] for r in rows}
    for expected in ("ID", "US", "EU", "CN", "GB", "JP", "IN", "CA", "MX"):
        assert expected in codes, f"regulasi {expected} tidak ter-seed"
    for r in rows:
        assert r["sourceUrl"].startswith("https://")
        assert r["snapshotDate"] == "2026-09-29"
        assert r["reviewStatus"] == "research_only"
        assert r["descriptionRule"].strip()
        # Setiap baris harus menyebut sumber/peraturan konkret di kolom source.
        assert r["source"].strip() and r["source"] != "..."


def test_regulations_seed_retires_legacy_demo_rows():
    class Store:
        def __init__(self):
            self.rows = {
                "REG-201": {"id": "REG-201", "countryCode": "US", "descriptionRule": "Regulation for US."},
                "EG-ADMIN": {"id": "EG-ADMIN", "countryCode": "ID", "descriptionRule": "Keep me"},
            }

        def all(self, table):
            return list(self.rows.values())

        def get(self, table, key):
            return self.rows.get(key)

        def insert(self, table, record):
            self.rows[record["id"]] = record

        def delete(self, table, key):
            del self.rows[key]

    store = Store()
    seed_regulatory_guide(store)
    assert "REG-201" not in store.rows, "baris demo legacy harus dipensiunkan"
    assert "EG-ADMIN" in store.rows, "record non-demo harus dipertahankan"
    assert any(k.startswith("REG-GUIDE-ID") for k in store.rows)


def test_seed_master_data_populates_guide_data_without_demo_entities():
    db.reset_store()
    from app.seed import seed_master_data

    seed_master_data()
    regs = db.all("regulations")
    assert any(str(r["id"]).startswith("REG-GUIDE") for r in regs)
    assert not any(str(r.get("descriptionRule", "")).startswith("Regulation for ") for r in regs)
    assert len(db.all("knowledge_articles")) >= 12
    # Tidak membuat entitas demo.
    for table in ("users", "products", "buyers", "orders", "payments"):
        assert len(db.all(table)) == 0, f"{table} tidak boleh terisi oleh master data"


# ── Knowledge articles ───────────────────────────────────────────────────────
def test_guide_knowledge_articles_cover_all_sections():
    arts = _guide_knowledge_articles()
    assert len(arts) >= 12
    cats = {a["category"] for a in arts}
    for expected in ("HS Code", "Incoterms", "Indonesia", "Amerika Serikat", "Uni Eropa", "FTA", "Compliance"):
        assert expected in cats, f"artikel kategori {expected} hilang"
    for a in arts:
        assert a["status"] == "Published"
        assert a["summary"].strip()
        assert len(a["steps"]) >= 3


# ── Endpoint /reference/ ─────────────────────────────────────────────────────
def test_reference_endpoint_serves_full_guide():
    with _client() as c:
        data = c.get("/api/v1/reference/").json()["data"]
    assert data["snapshotDate"] == "2026-09-29"
    assert len(data["incoterms"]) == 11
    assert len(data["kumhs"]) == 9
    assert data["hs2028"]["headings_total"] == 1229
    assert data["hs2022"]["chapters"] == 97
    assert data["indonesia"]["btki"]["lines"] == 11414
    assert data["indonesia"]["dhe"]["repatriation"] == "100%"
    assert len(data["unitedStates"]["timeline"]) >= 10
    assert len(data["europeanUnion"]["cbam"]["sectors"]) == 6
    assert len(data["complianceChecklist"]) == 4
    assert data["paymentMethods"]
    assert data["primarySources"]


def test_full_bundle_indonesia_import_example_matches_guide():
    b = full_reference_bundle()
    ex = b["indonesia"]["importExample"]
    assert ex["nilai_pabean_idr"] == 160_000_000
    assert ex["total_pungutan_idr"] == 39_760_000
