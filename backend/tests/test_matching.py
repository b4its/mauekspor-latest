"""Test layanan matching buyer request -> katalog (app/services/matching.py)."""
import pytest

from app import db
from app.services import matching


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


def test_category_id_mapping():
    assert matching._category_id("Makanan Olahan") == 1
    assert matching._category_id("FURNITURE & CRAFT") == 2
    assert matching._category_id("Textile") == 3
    assert matching._category_id("tidak dikenal") == 0
    assert matching._category_id("") == 0


def test_extract_keywords_menghapus_stopword_dan_membatasi():
    words = matching._extract_keywords("the red and green coffee for dengan yang dari")
    assert "the" not in words
    assert "dan" not in words
    assert "coffee" in words
    # max 20 kata
    many = matching._extract_keywords(" ".join([f"kata{i}" for i in range(50)]), max_words=20)
    assert len(many) == 20


def test_category_match():
    catalog = {"category": "Food & Beverage"}
    product = None
    # kategori cocok
    assert matching._category_match(1, catalog, product) == 100
    # kategori beda
    assert matching._category_match(2, catalog, product) == 25
    # req tanpa kategori -> 50
    assert matching._category_match(0, catalog, product) == 50


def test_hs_match():
    catalog = {"hs": "0901.21"}
    product = None
    assert matching._hs_match("0901.21", product, catalog) == 100
    assert matching._hs_match("0901.2101", product, catalog) == 75  # 6-digit
    assert matching._hs_match("0901.22", product, catalog) == 25  # beda digit ke-6
    assert matching._hs_match("9999", product, catalog) == 25
    assert matching._hs_match("", product, catalog) == 50


def test_spec_match():
    catalog = {"title": "Gayo Arabica Coffee", "description": "single origin arabica"}
    product = {"name": "Kopi", "description": "fully washed"}
    # semua keyword cocok
    assert matching._spec_match(["arabica", "coffee", "origin"], catalog, product) == 100
    # sebagian -> 70
    assert matching._spec_match(["arabica", "x1", "x2"], catalog, product) == 70
    # tanpa keyword -> 50
    assert matching._spec_match([], catalog, product) == 50


def test_capability_match():
    catalog = {}
    product = {"certificates": ["Halal", "HACCP"], "readiness": 90, "status": "Enriched", "id": "P-1"}
    # 20 (certs) + 30 (readiness) + 20 (enriched) = 70 (tanpa analyses)
    assert matching._capability_match(catalog, product, {}) == 70
    # dengan analysis -> +20 = 90
    db.insert("export_analyses", {"id": "EA-1", "productId": "P-1"})
    assert matching._capability_match(catalog, product, {}) == 90


def test_volume_match():
    catalog = {"availableStock": 100}
    product = None
    assert matching._volume_match(0, catalog, product) == 50  # tanpa target
    assert matching._volume_match(50, catalog, product) == 100  # stock cukup
    assert matching._volume_match(80, catalog, product) == 100  # stock cukup
    assert matching._volume_match(150, catalog, product) == 60  # > 50%
    assert matching._volume_match(500, catalog, product) == 30  # < 50%
    assert matching._volume_match(10, {"availableStock": 0}, None) == 40  # stock kosong


def _seed_catalog_and_request():
    db.insert("catalogs", {
        "id": "CAT-1", "title": "Gayo Arabica Coffee", "status": "Published",
        "category": "Food & Beverage", "hs": "0901.21", "productId": "P-1", "owner": "PT Kopi",
        "tags": ["coffee"], "description": "single origin"
    })
    db.insert("products", {
        "id": "P-1", "name": "Gayo Arabica", "category": "Food & Beverage",
        "hs": "0901.21", "certificates": ["Halal"], "readiness": 85, "status": "Enriched"
    })
    request = {
        "product_category": "Makanan Olahan",
        "subject": "Coffee untuk Jepang",
        "requirements": ["Single origin"],
        "spec_requirements": "arabica",
        "hs_code_target": "0901.21",
        "quantity": "1000",
    }
    return request


def test_match_buyer_request_skor_dan_alasan():
    request = _seed_catalog_and_request()
    matches = matching.match_buyer_request(request)
    assert len(matches) == 1
    m = matches[0]
    assert m["catalogId"] == "CAT-1"
    assert m["match_score"] > 0
    # HS cocok -> alasan ada
    assert any("HS code" in r for r in m["match_reasons"])


def test_match_buyer_request_tanpa_published_fallback():
    request = _seed_catalog_and_request()
    db.all("catalogs")[0]["status"] = "Draft"
    matches = matching.match_buyer_request(request)
    assert len(matches) == 1  # fallback ke semua katalog


def test_match_buyer_request_urutan_skor_turun():
    # dua katalog, satu cocok lebih baik
    request = _seed_catalog_and_request()
    db.insert("catalogs", {
        "id": "CAT-2", "title": "Rattan Chair", "status": "Published",
        "category": "Furniture & Craft", "hs": "9401.52", "productId": None, "owner": "Lain"
    })
    matches = matching.match_buyer_request(request)
    assert len(matches) == 2
    assert matches[0]["catalogId"] == "CAT-1"  # skor lebih tinggi di depan
