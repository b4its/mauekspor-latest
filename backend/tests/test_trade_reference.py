"""Research snapshot must not become an invented legal clearance or tariff."""

from app.data.regulatory_intel import product_regulations_for, profile_for
from app.data.trade_reference import rules_for, seed_trade_reference


def test_reference_is_dated_traceable_and_fta_is_not_automatically_effective():
    assert all(r["sourceUrl"].startswith("https://") and r["snapshotDate"] == "2026-09-29"
               and r["reviewStatus"] == "research_only" for r in rules_for("US") + rules_for("DE"))
    assert "belum otomatis" in profile_for("ID")["fta"]
    assert "IEU-CEPA" in " ".join(r["descriptionRule"] for r in rules_for("DE"))


def test_annex_i_cannot_be_inferred_from_hs_chapter_alone():
    assert not any(r["id"] == "EUDR" for r in product_regulations_for("0902", "DE"))
    assert not any(r["id"] == "EUDR" for r in product_regulations_for("40", "DE"))
    regs = product_regulations_for("090111", "DE")
    assert any(r["id"] == "EUDR" and r["applicability"] == "candidate_check_annex_i" for r in regs)
    assert not any(r["id"] == "EUDR" for r in product_regulations_for("090111", "JP"))
    assert any(r["id"] == "EU-CBAM" and r["applicability"] == "candidate_check_annex_i"
               for r in product_regulations_for("7208", "DE"))
    assert not any(r["id"] == "EU-CBAM" for r in product_regulations_for("7208", "US"))


def test_seed_retires_only_legacy_fake_rules_and_preserves_admin_records():
    class Store:
        def __init__(self):
            self.records = {
                "REG-201": {"id": "REG-201", "countryCode": "US", "descriptionRule": "Regulation for US."},
                "ADMIN-1": {"id": "ADMIN-1", "countryCode": "US", "descriptionRule": "Regulation for US."},
            }

        def all(self, table):
            return list(self.records.values())

        def get(self, table, key):
            return self.records.get(key)

        def insert(self, table, record):
            self.records[record["id"]] = record

        def delete(self, table, key):
            del self.records[key]

    store = Store()
    seed_trade_reference(store)
    seed_trade_reference(store)
    assert "REG-201" not in store.records
    assert "ADMIN-1" in store.records
    assert any(r["id"].startswith("REF-20260929-US") for r in store.records.values())
