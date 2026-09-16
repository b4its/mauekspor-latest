"""Test direktori regulasi seluruh dunia (app/data/world_countries.py, app/data/regulatory_intel.py)."""
from fastapi.testclient import TestClient

from app.data import regulatory_intel as ri
from app.data import world_countries as wc
from app.main import app


def test_world_countries_lengkap_terkini():
    assert len(wc.WORLD_COUNTRIES) >= 249
    codes = {c["country_code"] for c in wc.WORLD_COUNTRIES}
    for expect in ("ID", "JP", "US", "CN", "KR", "IN", "GB", "CA", "AU", "NZ", "SG", "MY", "TH", "VN", "AE", "SA", "DE", "FR", "NL", "BR", "ZA", "TR", "CH", "EG", "NG", "RU", "CO", "MX", "AR", "KE"):
        assert expect in codes, f"{expect} tidak ada di WORLD_COUNTRIES"
    for c in wc.WORLD_COUNTRIES:
        assert c["country_code"] and c["country_name"] and c["region"]
    # field lengkap untuk negara sampel
    idn = next(c for c in wc.WORLD_COUNTRIES if c["country_code"] == "ID")
    assert idn["capital"] and idn["currency"] and idn["languages"]
    assert idn["subregion"] == "South-Eastern Asia"


def test_customs_systems_terdefinisi():
    for code in ("ID", "DE", "FR", "NL", "BR", "AR", "MY", "TH", "VN", "RU"):
        assert code in ri.COUNTRY_CUSTOMS, f"{code} tidak dipetakan ke blok kepabeanan"


def test_profile_for_negara_env():
    jp = ri.profile_for("JP")
    assert jp["import_rules"] and jp["export_rules"]
    assert jp["authorities"]
    assert jp["tariff"] and jp["customs"]
    assert not jp.get("_is_template", False)
    # template tidak punya detail negara terdaftar
    assert ri.has_profile("JP")
    assert not ri.has_profile("TT")


def test_profile_for_tanpa_profil_pakai_template_region():
    # Negara dengan wilayah dikenal tapi tanpa profil -> template, bukan detail
    tt = ri.profile_for("TT", "Americas")
    assert tt.get("_is_template", False)
    assert tt["import_rules"] or tt["documents"]


def test_risk_level_for():
    assert ri.risk_level_for("RU") == "High"
    assert ri.risk_level_for("US") in ("Elevated", "Moderate", "Low")
    assert ri.risk_level_for("JP") == "Moderate"
    assert ri.risk_level_for("SA") == "Moderate"
    assert ri.risk_level_for("ZZ") == "Low"  # default rendah utk negara tak dikenal


def test_customs_system_of():
    info = ri.customs_system_of("DE")
    assert "nomenclature" in info
    assert "tariffs" in info
    assert info.get("label") == "European Union / TARIC"
    assert ri.customs_system_of("ID")["label"] == "ASEAN / AHTN"


def test_list_countries_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/countries/")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) >= 249
    assert next(c for c in data if c["country_code"] == "ID")["customs_system"] == "ASEAN"
    assert any("regions" in res.json()["meta"] for _ in [0])


def test_list_countries_filter():
    client = TestClient(app)
    r = client.get("/api/v1/countries/", params={"region": "Europe", "search": "er"})
    data = r.json()["data"]
    assert data
    assert all(c["region"] == "Europe" for c in data)
    assert all("er" in (c["country_name"] + c["country_code"]).lower() for c in data)


def test_get_country_detail_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/countries/ID/")
    assert res.status_code == 200
    d = res.json()["data"]
    assert d["country_code"] == "ID"
    assert d["customs_system"] == "ASEAN"
    assert d["import_rules"] and d["export_rules"]
    assert d["authorities"]
    assert d["tariff"] and d["customs"]
    assert d["customs_system_info"]["label"] == "ASEAN / AHTN"
    assert "regulations_by_category" in d  # field lama tetap dipertahankan


def test_get_country_detail_not_found():
    client = TestClient(app)
    assert client.get("/api/v1/countries/ZZ/").status_code == 404
