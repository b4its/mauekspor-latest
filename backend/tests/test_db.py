"""Test logika murni lapisan data (app/db.py) tanpa menyentuh SQLite."""
import pytest

from app import db


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


def test_all_unknown_table_dibuat():
    assert db.all("tabel_baru") == []
    assert "tabel_baru" in db._STORE


def test_insert_tanpa_id_mengenerate():
    rec = db.insert("products", {"name": "Kopi"})
    assert rec["id"].startswith("PRODUCT-")
    assert rec["__table"] == "products"
    assert len(db.all("products")) == 1


def test_insert_dengan_id():
    rec = db.insert("products", {"id": "PRD-001", "name": "X"})
    assert db.get("products", "PRD-001")["name"] == "X"


def test_find_dan_get_by_filter():
    db.insert("buyers", {"id": "B-1", "country": "JP", "segment": "Retail"})
    db.insert("buyers", {"id": "B-2", "country": "DE", "segment": "Retail"})
    db.insert("buyers", {"id": "B-3", "country": "JP", "segment": "Wholesale"})
    assert len(db.find("buyers", country="JP")) == 2
    assert db.get_by("buyers", country="JP", segment="Wholesale")["id"] == "B-3"
    assert db.get_by("buyers", country="US") is None


def test_get_tidak_ditemukan_none():
    assert db.get("products", "TIDAK-ADA") is None


def test_update_record_ada_dan_tidak_ada():
    db.insert("products", {"id": "P-1", "name": "A"})
    updated = db.update("products", "P-1", {"name": "B", "nilai_none": None})
    assert updated["name"] == "B"
    # patch None diabaikan
    assert "nilai_none" not in updated
    assert db.update("products", "P-X", {"name": "B"}) is None


def test_replace_record_ada_dan_tidak_ada():
    db.insert("products", {"id": "P-1", "name": "A"})
    replaced = db.replace("products", "P-1", {"name": "C"})
    assert replaced["id"] == "P-1"
    assert replaced["name"] == "C"
    assert db.replace("products", "P-X", {"name": "C"}) is None


def test_delete_record_ada_dan_tidak_ada():
    db.insert("products", {"id": "P-1"})
    assert db.delete("products", "P-1") is True
    assert db.delete("products", "P-1") is False
    assert db.get("products", "P-1") is None


def test_save_dengan_dan_tanpa_table():
    rec = db.insert("products", {"id": "P-1"})
    saved = db.save(rec)
    assert saved["id"] == "P-1"
    # tanpa __table -> tidak persist, tidak error
    assert db.save({"id": "X"}) == {"id": "X"}


def test_gen_id_prefix_kustom():
    assert db.gen_id("products", "PRD").startswith("PRD-")
    assert db.gen_id("unknown_table").startswith("UNKNOWN_TABLE-")


def test_loaded_records():
    db.insert("products", {"id": "P-1"})
    db.insert("products", {"id": "P-2"})
    assert db.loaded_records("products") == 2
