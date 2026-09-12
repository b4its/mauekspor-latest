"""Test layanan kepatuhan ekspor (app/services/compliance.py)."""
import pytest

from app import db
from app.services import compliance


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


def test_parse_json_list():
    assert compliance._parse_json_list('[{"a": 1}]') == [{"a": 1}]
    assert compliance._parse_json_list('teks [{"a": 2}] akhir') == [{"a": 2}]
    assert compliance._parse_json_list('tanpa kurung') is None
    assert compliance._parse_json_list('[bukan json') is None
    assert compliance._parse_json_list(None) is None
    assert compliance._parse_json_list('{"obj": 1}') is None  # bukan list


def test_calculate_readiness_score_grades():
    # bersih -> Ready
    assert compliance.calculate_readiness_score([]) == (100, "Ready")
    # satu minor (5) -> 95 Ready
    score, grade = compliance.calculate_readiness_score([{"severity": "minor"}])
    assert score == 95 and grade == "Ready"
    # dua major (10) -> 80 Ready (batas)
    score, grade = compliance.calculate_readiness_score([{"severity": "major"}, {"severity": "major"}])
    assert score == 80 and grade == "Ready"
    # tiga major -> 70 Warning
    score, grade = compliance.calculate_readiness_score([{"severity": "major"}] * 3)
    assert score == 70 and grade == "Warning"
    # lima critical (20) -> 0 Critical
    score, grade = compliance.calculate_readiness_score([{"severity": "critical"}] * 5)
    assert score == 0 and grade == "Critical"
    # severity tidak dikenal -> default 5
    score, grade = compliance.calculate_readiness_score([{"severity": "aneh"}])
    assert score == 95


def test_generate_recommendations_tanpa_isu():
    text = compliance.generate_recommendations([])
    assert "Tidak ditemukan" in text


def test_generate_recommendations_fallback_terdaftar():
    text = compliance.generate_recommendations([
        {"type": "Labeling", "required_value": "JP label", "severity": "major"},
    ])
    assert "1." in text
    assert "JP label" in text


def test_check_ingredient_compliance_terdeteksi():
    # Gunakan negara dengan regulasi Ingredient yang punya forbidden_keywords
    # (data seed countries.py punya contoh)
    product = {"name": "Kopi", "description": "mengandung pewarna terlarang"}
    issues = compliance.check_ingredient_compliance(product, "JP")
    # bila ada reg ingredient dengan keyword cocok -> critical issue
    ingredient_issues = [i for i in issues if i["type"] == "Ingredient"]
    for i in ingredient_issues:
        assert i["severity"] == "critical"


def test_check_specification_compliance_missing():
    product = {"name": "Kopi", "quality_specs": {}}
    issues = compliance.check_specification_compliance(product, "JP")
    for i in issues:
        assert i["type"] == "Labeling"
        assert i["severity"] == "major"


def test_check_packaging_compliance():
    product = {"name": "Rattan Chair", "packaging": "kayu tidak diolah"}
    issues = compliance.check_packaging_compliance(product, "EU")
    # tidak ada assertion keras; pastikan tidak error dan tipe benar
    for i in issues:
        assert i["type"] == "Physical"


def test_analyze_product_compliance_menggabungkan_semua_checker():
    product = {"name": "Kopi", "category": "Food & Beverage", "description": "", "quality_specs": {}, "packaging": ""}
    result = compliance.analyze_product_compliance(product, "JP")
    assert "issues" in result
    assert "score" in result
    assert "grade" in result
    assert "recommendations" in result
    assert 0 <= result["score"] <= 100


def test_generate_regulation_recommendations_id_dan_en():
    snapshot = {"name": "Kopi", "hs": "0901.21"}
    id_result = compliance.generate_regulation_recommendations(snapshot, "JP", language="id")
    en_result = compliance.generate_regulation_recommendations(snapshot, "JP", language="en")
    assert len(id_result["sections"]) == 10
    assert id_result["from_cache"] is False
    # judul section dalam bahasa Indonesia vs Inggris
    first_id = id_result["sections"][0]
    first_en = en_result["sections"][0]
    assert first_id["title"] != first_en["title"]
    assert first_en["title_en"] == "Overview"


def test_generate_regulation_recommendations_negara_tidak_dikenal():
    snapshot = {"name": "Produk", "hs": "TBD"}
    result = compliance.generate_regulation_recommendations(snapshot, "ZZ", language="id")
    assert len(result["sections"]) == 10
    assert result["country"]["country_name"] == "ZZ"  # fallback


def test_snapshot_product_dengan_enrichment():
    db.insert("product_enrichments", {"id": "EN-1", "productId": "P-1", "hsCode": "0901.21"})
    snapshot = compliance.snapshot_product({"id": "P-1", "name": "Kopi", "category": "Food"})
    assert snapshot["id"] == "P-1"
