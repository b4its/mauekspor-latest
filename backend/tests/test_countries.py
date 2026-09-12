"""Test master data negara & regulasi (app/data/countries.py)."""
from app.data import countries


def test_get_countries_berisi_negara_utama():
    data = countries.get_countries()
    codes = [c["country_code"] for c in data]
    assert "JP" in codes and "DE" in codes and "US" in codes
    # mengembalikan salinan (tidak memutasi data asli)
    data[0]["country_code"] = "XX"
    assert countries.COUNTRIES[0]["country_code"] != "XX"


def test_get_regulations_per_negara():
    jp = countries.get_regulations("JP")
    assert jp
    assert all(r["country_code"] == "JP" for r in jp)
    # ada kategori Ingredient, Labeling, Physical
    cats = {r["rule_category"] for r in jp}
    assert "Ingredient" in cats and "Labeling" in cats and "Physical" in cats
    # negara tanpa regulasi -> kosong
    assert countries.get_regulations("ZZ") == []


def test_get_country_ada_dan_tidak():
    jp = countries.get_country("JP")
    assert jp["country_name"] == "Japan"
    assert jp["region"] == "Asia"
    assert countries.get_country("jp") is not None  # case-insensitive
    assert countries.get_country("ZZ") is None


def test_resolve_country_kode():
    assert countries.resolve_country("JP") == "JP"
    assert countries.resolve_country("DE") == "DE"
    assert countries.resolve_country("") == "JP"


def test_resolve_country_nama():
    assert countries.resolve_country("Japan") == "JP"
    assert countries.resolve_country("GERMANY") == "DE"
    assert countries.resolve_country("singapore") == "SG"


def test_resolve_country_nama_sebagian():
    # nama sebagian cocok (substring)
    assert countries.resolve_country("United") == "US"


def test_resolve_country_tidak_dikenal_fallback_2huruf():
    # "XY" tidak dikenal -> fallback "XY"
    assert countries.resolve_country("XY") == "XY"


def test_region_of():
    assert countries.region_of("JP") == "Asia"
    assert countries.region_of("DE") == "Europe"
    assert countries.region_of("US") == "North America"
    assert countries.region_of("AU") == "Oceania"
    assert countries.region_of("AE") == "Middle East"
    assert countries.region_of("ZZ") == "Asia"  # default
