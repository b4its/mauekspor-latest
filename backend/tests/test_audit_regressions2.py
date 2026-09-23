"""Regresi audit lanjutan: read-gating anonim, fail-fast secret production,
konkurensi id store, delete id int, dan GET read-only."""
import json
import os
import threading

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import db

ADMIN = ("admin@mauekspor.example", "admin123")


def _login(c: TestClient, creds=ADMIN) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- Read gating: komersial butuh login, publik tetap terbuka ----------
@pytest.mark.parametrize("module", ["payments", "messages", "orders", "products", "buyers", "costing"])
def test_anon_read_komersial_ditolak(module):
    with TestClient(app) as c:
        assert c.get(f"/api/v1/{module}/").status_code == 401


@pytest.mark.parametrize("module", ["payments", "messages", "orders", "products"])
def test_authed_read_komersial_ok(module):
    with TestClient(app) as c:
        token = _login(c)
        assert c.get(f"/api/v1/{module}/", headers=_auth(token)).status_code == 200


@pytest.mark.parametrize("path", ["countries", "hs-codes", "catalogs/public", "search"])
def test_anon_read_publik_tetap_terbuka(path):
    with TestClient(app) as c:
        assert c.get(f"/api/v1/{path}/").status_code == 200


# ---------- Fail-fast secret di production ----------
def _build_settings(**env):
    from app.core.config import Settings
    prev = {k: os.environ.get(k) for k in env}
    os.environ.update({k: str(v) for k, v in env.items()})
    try:
        return Settings()
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_production_menolak_secret_default():
    with pytest.raises(Exception):
        _build_settings(MAUEKSPOR_ENVIRONMENT="production", MAUEKSPOR_SECRET_KEY="change-me-in-production")


def test_production_menolak_seed_password_default():
    with pytest.raises(Exception):
        _build_settings(
            MAUEKSPOR_ENVIRONMENT="production",
            MAUEKSPOR_SECRET_KEY="a-strong-random-secret-value-123456",
            MAUEKSPOR_SEED_ADMIN_PASSWORD="admin123",
        )


def test_production_dengan_secret_kuat_ok():
    s = _build_settings(
        MAUEKSPOR_ENVIRONMENT="production",
        MAUEKSPOR_SECRET_KEY="a-strong-random-secret-value-123456",
        MAUEKSPOR_SEED_ADMIN_PASSWORD="S3cure-Adm1n-Pass",
    )
    assert s.environment == "production"


def test_allow_insecure_defaults_escape_hatch():
    s = _build_settings(
        MAUEKSPOR_ENVIRONMENT="production",
        MAUEKSPOR_ALLOW_INSECURE_DEFAULTS="1",
    )
    assert s is not None


def test_development_secret_default_tidak_blokir():
    assert _build_settings(MAUEKSPOR_ENVIRONMENT="development") is not None


# ---------- Konkurensi: gen_id/insert tidak boleh duplikat ----------
def test_gen_id_unik_saat_konkuren():
    with TestClient(app) as c:
        c.get("/api/v1/health")
        db.reset_store()
        results = []
        barrier = threading.Barrier(16)

        def worker():
            barrier.wait()
            results.append(db.insert("tasks", {"title": "t"})["id"])

        threads = [threading.Thread(target=worker) for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 16
        assert len(set(results)) == 16, f"id duplikat: {results}"
        assert len(db.all("tasks")) == 16


# ---------- delete: id int (admin-made) tetap terhapus ----------
def test_delete_record_id_int_konsisten():
    with TestClient(app) as c:
        c.get("/api/v1/health")
        db.reset_store()
        db.insert("tasks", {"id": 5, "title": "int-id"})
        assert db.get("tasks", 5) is not None
        assert db.get("tasks", "5") is not None  # lookup toleran tipe
        assert db.delete("tasks", 5) is True
        assert db.get("tasks", 5) is None
        assert db.all("tasks") == []


# ---------- GET tidak boleh menulis / fetch ----------
def test_get_exchange_rate_tidak_memicu_fetch(monkeypatch):
    from app.services import pricing
    called = {"n": 0}

    def boom():
        called["n"] += 1
        return 16000.0

    monkeypatch.setattr(pricing, "fetch_live_exchange_rate", boom)
    with TestClient(app) as c:
        token = _login(c)  # login dulu (seed user ada)
        db.insert("exchange_rates", {"id": "FX-1", "rate": 15800.0, "source": "manual",
                                     "updatedAt": "2000-01-01T00:00:00+00:00"})
        before = len(db.all("exchange_rates"))
        res = c.get("/api/v1/costing/exchange-rate/", headers=_auth(token))
        assert res.status_code == 200
        assert called["n"] == 0, "GET tidak boleh memicu outbound fetch"
        assert len(db.all("exchange_rates")) == before, "GET tidak boleh menambah record"


# ---------- Pagination clamp ----------
def test_filtered_query_clamp_offset_dan_limit():
    from app.api.routes import _filtered_query
    assert _filtered_query("products", limit=10_000_000)["meta"]["limit"] <= 500
    assert _filtered_query("products", limit=-5)["meta"]["limit"] == 0
    assert _filtered_query("products", offset=-10)["meta"]["offset"] == 0
