"""Snapshot regulasi terkurasi harus faktual, tanggal jelas, dan tanpa data karangan.

Memastikan:
- timeline peristiwa 2026–2028 konsisten dan terurut;
- angka kunci HS 2028 sesuai sumber WCO;
- setiap pointer riset berasal dari sumber resmi https dan berstatus research_only;
- tidak ada lagi aturan demo sintetis ("Regulation for <CODE>.").
"""
from app.data import trade_reference as tr
from app.data.regulatory_intel import product_regulations_for


def test_snapshot_date_and_guide_present():
    assert tr.SNAPSHOT_DATE == "2026-09-29"
    assert tr.GUIDE.endswith("PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md")


def test_timeline_is_chronological_and_scoped():
    dates = [d for (d, _, _) in tr.REGULATORY_TIMELINE]
    assert dates == sorted(dates), "timeline harus terurut kronologis"
    # Peristiwa kunci dari guide harus ada.
    joined = " ".join(f"{d} {e} {s}" for (d, e, s) in tr.REGULATORY_TIMELINE)
    for key in ("IEEPA", "CBAM", "EUDR", "Section 301", "HS 2028", "DHE SDA", "Permendag 5/2026"):
        assert key in joined, f"timeline kehilangan peristiwa: {key}"


def test_hs_2028_facts_match_wco():
    f = tr.HS_2028_FACTS
    assert f["effective"] == "2028-01-01"
    assert f["edition"] == 8
    assert f["headings_total"] == 1229
    assert f["subheadings_total"] == 5852
    assert f["subheadings_new"] == 428
    assert f["subheadings_deleted"] == 172
    assert f["headings_new"] == 6
    assert f["headings_deleted"] == 5
    assert "39.15" in f["highlights"] or "30.07" in f["highlights"]


def test_all_research_pointers_are_traceable_and_not_clearance():
    for code in ("ID", "US", "CA", "GB", "MX", "JP", "CN", "IN", "DE", "FR", "NL"):
        for r in tr.rules_for(code):
            assert r["sourceUrl"].startswith("https://"), f"{code} url tidak https"
            assert r["snapshotDate"] == "2026-09-29"
            assert r["reviewStatus"] == "research_only"
            # Bukan tarif/clearance otomatis.
            assert "requiredSpecs" in r and r["requiredSpecs"] == []


def test_indonesia_pointer_covers_key_2026_regimes():
    joined = " ".join(r["descriptionRule"] for r in tr.rules_for("ID"))
    for key in ("Permendag 16/2025", "Permendag 5/2026", "Permendag 6/2026", "PP 21/2026", "PMK 4/2025"):
        assert key in joined, f"pointer ID kehilangan {key}"


def test_eu_pointer_covers_cbam_eudr_and_ecommerce():
    joined = " ".join(r["descriptionRule"] for r in tr.rules_for("DE"))
    for key in ("CBAM", "EUDR", "€3", "GPSR"):
        assert key in joined, f"pointer EU kehilangan {key}"
    assert "IEU-CEPA" in joined


def test_us_pointer_reflects_ieepa_reversal_and_301_forced_labor():
    joined = " ".join(r["descriptionRule"] for r in tr.rules_for("US"))
    assert "IEEPA" in joined and "dibatalkan" in joined
    assert "forced labor" in joined
    assert "de minimis" in joined.lower()


def test_eu_cbam_regulation_carries_dates_and_minimum_threshold():
    regs = product_regulations_for("7208", "DE")
    cbam = next(r for r in regs if r["id"] == "EU-CBAM")
    assert cbam["applicability"] == "candidate_check_annex_i"
    assert "50 ton" in cbam["requirement"]
    assert "30 Sep 2027" in cbam["deadline"] or "30 September 2027" in cbam["deadline"]


def test_cross_product_regulations_include_gpsr_and_forced_labour():
    regs = product_regulations_for("0901", "DE")
    ids = {r["id"] for r in regs}
    assert "EU-GPSR" in ids
    assert "EU-FORCED-LABOUR" in ids


def test_country_detail_exposes_reference_timeline_and_hs_2028():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        data = c.get("/api/v1/countries/US/").json()["data"]
    assert isinstance(data.get("reference_timeline"), list) and data["reference_timeline"]
    assert data["reference_timeline"][0]["date"] <= data["reference_timeline"][-1]["date"]
    facts = data.get("hs_2028_facts")
    assert facts and facts["headings_total"] == 1229
    assert data["reference_snapshot_date"] == "2026-09-29"
