"""Test lapisan persistensi SQLite (db.py) dengan database file temporer.

Fungsi-fungsi ini (persist/load/delete/clear) hanya berjalan saat
persistensi aktif (MAUEKSPOR_DISABLE_PERSISTENCE tidak disetel).
"""
import json
import sqlite3

import pytest

from app import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_mauekspor.db"
    monkeypatch.setenv("MAUEKSPOR_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.delenv("MAUEKSPOR_DISABLE_PERSISTENCE", raising=False)
    # reset flag agar load berikutnya membaca dari file baru
    db._LOADED = False
    yield db_path
    db._LOADED = False
    db.reset_store()


def _read_rows(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT table_name, id, payload FROM records ORDER BY rowid").fetchall()
    finally:
        conn.close()


def test_persist_record_menulis_ke_sqlite(temp_db):
    rec = {"id": "P-1", "name": "Kopi", "__table": "products", "__private": "jangan disimpan"}
    db._persist_record("products", rec)

    rows = _read_rows(temp_db)
    assert len(rows) == 1
    table, rid, payload = rows[0]
    assert table == "products"
    assert rid == "P-1"
    data = json.loads(payload)
    assert data["name"] == "Kopi"
    # field __private tidak ikut tersimpan
    assert "__private" not in data


def test_persist_update_menimpa_baris_sama(temp_db):
    db._persist_record("products", {"id": "P-1", "name": "A"})
    db._persist_record("products", {"id": "P-1", "name": "B"})
    rows = _read_rows(temp_db)
    assert len(rows) == 1
    assert json.loads(rows[0][2])["name"] == "B"


def test_load_from_disk_memuat_kembali(temp_db):
    db._persist_record("products", {"id": "P-1", "name": "Kopi"})
    # simulasikan proses baru: kosongkan store in-memory (tanpa clear disk),
    # set _LOADED=False lalu init_store() membaca ulang dari sqlite
    db._STORE.clear()
    for name in db._TABLES:
        db._STORE[name] = []
    db._LOADED = False
    db.init_store()
    rec = db.get("products", "P-1")
    assert rec is not None
    assert rec["name"] == "Kopi"


def test_delete_record_menghapus_sqlite(temp_db):
    db._persist_record("products", {"id": "P-1"})
    db._delete_record("products", "P-1")
    assert _read_rows(temp_db) == []


def test_clear_disk_menghapus_semua(temp_db):
    db._persist_record("products", {"id": "P-1"})
    db._persist_record("buyers", {"id": "B-1"})
    db._clear_disk()
    assert _read_rows(temp_db) == []


def test_persistence_dinonaktifkan_tidak_menulis(tmp_path, monkeypatch):
    db_path = tmp_path / "off.db"
    monkeypatch.setenv("MAUEKSPOR_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("MAUEKSPOR_DISABLE_PERSISTENCE", "1")
    db._persist_record("products", {"id": "P-1"})
    # tanpa persistence, tidak ada file sqlite dibuat
    assert not db_path.exists()
