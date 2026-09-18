"""Test seeder komoditas desa (app/seed_village_commodities.py)."""
from app import db
from app.seed_village_commodities import (
    VILLAGE_HS_CHAPTERS,
    filter_village_hs_codes,
    is_village_hs_code,
    seed_village_commodities,
    seed_village_hs_codes,
)


def test_is_village_hs_code():
    # Chapter 01-24: pertanian/peternakan/perikanan/perkebunan
    assert is_village_hs_code("090121")  # kopi
    assert is_village_hs_code("180100")  # kakao
    assert is_village_hs_code("040900")  # madu
    # Chapter 46: kerajinan anyaman rotan
    assert is_village_hs_code("460212")
    # Chapter 68-70: kriya
    assert is_village_hs_code("691110")
    assert is_village_hs_code("701399")
    # Di luar cakupan komoditas desa
    assert not is_village_hs_code("851712")  # smartphone
    assert not is_village_hs_code("940360")  # mebel kayu
    assert not is_village_hs_code("610910")  # tekstil
    assert not is_village_hs_code("")
    assert not is_village_hs_code(None)


def test_filter_village_hs_codes():
    codes = [
        {"hs_code": "090111", "description": "Coffee"},
        {"hs_code": "851712", "description": "Smartphones"},
        {"hs_code": "691110", "description": "Porcelain"},
    ]
    result = filter_village_hs_codes(codes)
    assert [c["hs_code"] for c in result] == ["090111", "691110"]


def test_seed_village_hs_codes_hanya_chapter_desa():
    assert seed_village_hs_codes() > 0
    total = db.loaded_records("hs_codes")
    # Jauh lebih kecil dari 6.941 kode penuh
    assert 0 < total < 3000
    # Semua kode termasuk chapter komoditas desa
    for record in db.all("hs_codes"):
        digits = "".join(ch for ch in str(record.get("hs_code", "")) if ch.isdigit())
        assert int(digits[:2]) in VILLAGE_HS_CHAPTERS


def test_seed_village_commodities_mengisi_komoditas_desa():
    seed_village_commodities()
    products = {p["id"]: p for p in db.all("products")}
    expected = [
        "PRD-DES-KOPI-001", "PRD-DES-KAKAO-003", "PRD-DES-VANILI-004", "PRD-DES-MANGGIS-005",
        "PRD-DES-ROTAN-006", "PRD-DES-HHNK-008",
    ]
    for pid in expected:
        assert pid in products

    profiles = {p["id"] for p in db.all("business_profiles")}
    assert "BIZ-DES-TORAJA" in profiles
    assert "BIZ-DES-GAYO" in profiles

    enrichments = {e["productId"] for e in db.all("product_enrichments")}
    for pid in expected:
        assert pid in enrichments


def test_seed_village_commodities_idempoten():
    seed_village_commodities()
    before = db.loaded_records("products")
    seed_village_commodities()
    assert db.loaded_records("products") == before
