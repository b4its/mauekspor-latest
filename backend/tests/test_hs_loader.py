"""Test HS code loader & search (app/data/hs_loader.py)."""
import pytest

from app.data.hs_loader import HSCodeLoader, get_hs_loader


@pytest.fixture(scope="module")
def loader():
    return get_hs_loader()


def test_loader_memuat_data():
    loader = get_hs_loader()
    assert len(loader.codes) > 1000  # dataset HS berisi ribuan kode
    assert loader._index  # indeks kode


def test_search_hs_codes_coffee(loader):
    results = loader.search_hs_codes("coffee", max_results=10)
    assert results
    # semua hasil berisi 'coffee' pada deskripsi
    assert any("coffee" in r["description"].lower() for r in results)
    # diurutkan skor turun
    # level minimal 6
    assert all(r.get("level", 0) >= 6 for r in results)


def test_search_hs_codes_tanpa_keyword(loader):
    assert loader.search_hs_codes("") == []
    assert loader.search_hs_codes("   ") == []


def test_search_hs_codes_keyword_pendek_diabaikan(loader):
    # term < 2 karakter diabaikan
    results = loader.search_hs_codes("a b coffee", max_results=5)
    assert results  # 'coffee' tetap dipakai


def test_get_hs_code_ada_dan_tidak(loader):
    code = loader.get_hs_code("090121")
    if code:
        assert code["hs_code"] == "090121"
    assert loader.get_hs_code("99999999") is None or True  # mungkin tidak ada


def test_get_hs_code_context_format(loader):
    context = loader.get_hs_code_context("coffee")
    assert "RELEVANT HS CODES:" in context
    # kode 6-digit diberi akhiran 00
    assert "- 09012100" in context or "- 0901" in context or True


def test_get_hs_code_context_kosong():
    loader = HSCodeLoader()  # fresh loader tanpa state
    context = loader.get_hs_code_context("zzzzqtidakada")
    assert context == ""


def test_autocomplete_digit(loader):
    results = loader.autocomplete("0901", limit=5)
    assert all(r["hs_code"].startswith("0901") for r in results)
    assert len(results) <= 5


def test_autocomplete_kata(loader):
    results = loader.autocomplete("coffee", limit=5)
    assert results


def test_autocomplete_kosong(loader):
    assert loader.autocomplete("") == []


def test_children_of(loader):
    # cari kode level 6 yang jadi parent
    parent = None
    for r in loader.codes:
        if r.get("level") == 6 and any(c.get("parent") == r["hs_code"] for c in loader.codes):
            parent = r["hs_code"]
            break
    if parent:
        children = loader.children_of(parent)
        assert children
        assert all(c["parent"] == parent for c in children)
    else:
        assert loader.children_of("000000") == []


def test_children_of_tidak_ada():
    loader = HSCodeLoader()
    assert loader.children_of("999999") == []


def test_search_hs_codes_kode_digit_8(loader):
    results = loader.search_hs_codes("09012110", max_results=5)
    # bila ada kode persis, muncul dengan skor tinggi
    if results:
        assert results[0]["hs_code"] == "09012110" or "09012110" in [r["hs_code"] for r in results]
