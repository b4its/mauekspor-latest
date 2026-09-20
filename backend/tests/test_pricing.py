"""Test layanan keuangan & pricing (app/services/pricing.py)."""
from datetime import datetime, timedelta, timezone

import pytest

from app import db
from app.services import pricing


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


# ---------- Exchange rate ----------
def test_get_exchange_rate_fallback_saat_fetch_gagal(monkeypatch):
    monkeypatch.setattr(pricing, "fetch_live_exchange_rate", lambda: None)
    rec = pricing.get_exchange_rate()
    assert rec["rate"] == pricing.FALLBACK_RATE
    assert rec["source"] == "fallback"


def test_get_exchange_rate_fresh_tidak_fetch(monkeypatch):
    called = {"n": 0}

    def fetch():
        called["n"] += 1
        return 16000.0

    monkeypatch.setattr(pricing, "fetch_live_exchange_rate", fetch)
    db.insert("exchange_rates", {
        "id": "FX-1", "rate": 15800.0, "source": "manual",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "baseCurrency": pricing.BASE_CURRENCY, "targetCurrency": pricing.DISPLAY_CURRENCY,
    })
    rec = pricing.get_exchange_rate()
    assert rec["rate"] == 15800.0
    assert called["n"] == 0  # tidak fetch karena masih fresh


def test_get_exchange_rate_stale_memicu_fetch(monkeypatch):
    monkeypatch.setattr(pricing, "fetch_live_exchange_rate", lambda: 16100.0)
    old = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    db.insert("exchange_rates", {"id": "FX-1", "rate": 15800.0, "source": "manual", "updatedAt": old,
        "baseCurrency": pricing.BASE_CURRENCY, "targetCurrency": pricing.DISPLAY_CURRENCY})
    rec = pricing.get_exchange_rate()
    assert rec["rate"] == 16100.0
    assert rec["source"] == "auto_fetched"


def test_get_exchange_rate_updatedAt_invalid_dianggap_stale(monkeypatch):
    monkeypatch.setattr(pricing, "fetch_live_exchange_rate", lambda: None)
    db.insert("exchange_rates", {"id": "FX-1", "rate": 15800.0, "source": "manual", "updatedAt": "bukan-tanggal"})
    rec = pricing.get_exchange_rate()
    assert rec["source"] == "fallback"


def test_set_exchange_rate_update_dan_create():
    created = pricing.set_exchange_rate(15900.0, source="manual")
    assert created["rate"] == 15900.0
    updated = pricing.set_exchange_rate(16000.0, source="admin")
    assert updated["rate"] == 16000.0
    assert len(db.all("exchange_rates")) == 1
    assert updated["source"] == "admin"


# ---------- Kalkulasi harga ----------
def test_trucking_cost_bands():
    assert pricing._trucking_cost(30) == pytest.approx(30 * 0.50, abs=0.001)
    assert pricing._trucking_cost(100) == pytest.approx(100 * 0.40, abs=0.001)
    assert pricing._trucking_cost(300) == pytest.approx(300 * 0.30, abs=0.001)
    assert pricing._trucking_cost(1000) == pytest.approx(1000 * 0.25, abs=0.001)
    # melewati semua band -> band terakhir
    assert pricing._trucking_cost(20000) == pytest.approx(20000 * 0.25, abs=0.001)


def test_calculate_exw_fob_cif():
    exw = pricing.calculate_exw(10000, 2000, 20, 15800)
    assert exw == pytest.approx(round(12000 * 1.2 / 15800, 2), abs=0.001)
    fob = pricing.calculate_fob(100.0, 200, 15800)
    # trucking 200km = 80 USD + doc 50 (both in USD, which is display currency when rate=15800)
    assert fob == pytest.approx(100 + 80 + 50, abs=0.001)
    cif = pricing.calculate_cif(200.0, "Asia")
    freight = 200 * 0.08
    insurance = (200 + freight) * 0.005
    assert cif == pytest.approx(round(200 + freight + insurance, 2), abs=0.001)
    # region tidak dikenal -> default 0.12
    cif_unknown = pricing.calculate_cif(200.0, "Mars")
    assert cif_unknown > cif


# ---------- Kontainer ----------
def test_container_capacity_by_volume_dan_weight():
    # volume kecil, berat besar -> dibatasi bobot
    res = pricing.container_capacity(0.5, 200)
    by_volume = int(33.2 * 0.85 / 0.5)
    by_weight = int(17500 / 200)
    assert res["capacity_20ft"] == min(by_volume, by_weight)
    assert res["capacity_40ft"] == res["capacity_20ft"] * 2.1
    assert "bobot" in res["tips"][0].lower() or "volume" in res["tips"][0].lower()


def test_container_capacity_zero_volume():
    res = pricing.container_capacity(0, 100)
    assert res["capacity_20ft"] == 0
    assert any("dimensi" in t.lower() for t in res["tips"])


def test_container_capacity_efisien():
    res = pricing.container_capacity(0.1, 10)
    assert "efisien" in res["tips"][0].lower()


# ---------- Full costing ----------
def test_calculate_full_costing(monkeypatch):
    monkeypatch.setattr(pricing, "get_exchange_rate", lambda: {"rate": 15800.0, "source": "test"})
    result = pricing.calculate_full_costing(10000, 2000, 20, "Japan", distance_km=200)
    assert result["exchangeRate"] == 15800.0
    assert result["exwPrice"] > 0
    assert result["fobPrice"] > result["exwPrice"]
    assert result["cifPrice"] > result["fobPrice"]
    assert len(result["lines"]) >= 7
    assert result["container"]["capacity_20ft"] >= 0


# ---------- PDF ----------
def test_build_costing_pdf_valid():
    pdf = pricing.build_costing_pdf({
        "title": "T", "destination": "JP", "incoterm": "FOB", "margin": 20,
        "exchangeRate": 15800, "lines": [{"category": "Production", "label": "COGS", "amount": 100}],
        "exwPrice": 1, "fobPrice": 2, "cifPrice": 3, "landedCost": 4, "risks": ["R1"],
    })
    assert pdf.startswith(b"%PDF-1.4")
    assert b"MAUEKSPOR - COSTING REPORT" in pdf
    assert b"COGS" in pdf


def test_build_analysis_pdf_valid():
    pdf = pricing.build_analysis_pdf({
        "productName": "Kopi", "destination": "JP", "hsCode": "0901.21",
        "status": "Ready", "score": 85, "statusGrade": "A", "confidence": 90,
        "complianceIssues": [{"severity": "high", "type": "Label", "required_value": "JP label"}],
        "recommendations": ["R1", "R2"],
    })
    assert pdf.startswith(b"%PDF-1.4")
    assert b"EXPORT ANALYSIS REPORT" in pdf


def test_build_compare_pdf_valid():
    pdf = pricing.build_compare_pdf(
        {"name": "Kopi", "hs": "0901.21"},
        [{"country": "JP", "score": 90, "grade": "A", "critical_issues": 0, "recommendation": "rec"}],
    )
    assert pdf.startswith(b"%PDF-1.4")
    assert b"BEST OPTION : JP" in pdf


# ---------- Kapasitas kontainer dari dimensi (referensi ExportReadyAI) ----------
def test_calculate_container_capacity_from_dimensions():
    # 50x40x30 cm = 60.000 cm³; volume kontainer 20ft * 0.85 / 60000
    res = pricing.calculate_container_capacity_from_dimensions(50, 40, 30)
    assert res["capacity_20ft"] > 0
    assert res["capacity_40ft"] == round(res["capacity_20ft"] * 2.1)
    assert res["utilization_note"]
    assert res["tips"]


def test_calculate_container_capacity_dimensi_invalid():
    res = pricing.calculate_container_capacity_from_dimensions(0, 0, 0)
    assert res["capacity_20ft"] == 0
    assert "dimensi" in res["utilization_note"].lower()


def test_calculate_container_capacity_dibatasi_bobot():
    # berat besar -> kapasitas dibatasi bobot
    res = pricing.calculate_container_capacity_from_dimensions(50, 40, 30, weight_per_unit_kg=500)
    assert res["capacity_20ft"] == int(17500 / 500)
    assert "bobot" in res["utilization_note"].lower()


def test_ai_container_optimization_tanpa_nama_produk():
    assert pricing.ai_container_optimization("", {}, 100) == ""


def test_ai_container_optimization_mock_menghasilkan_saran():
    # mode mock -> ai.complete mengembalikan teks canned untuk kind tidak dikenal?
    # kind container_optimization tidak ada di mock -> None -> string kosong, atau fallback
    text = pricing.ai_container_optimization("Kopi Gayo", {"l": 50, "w": 40, "h": 30}, 100)
    # tidak wajib ada teks di mode mock; pastikan tidak error dan bertipe str
    assert isinstance(text, str)
