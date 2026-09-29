"""Curated research pointers from guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md.

This snapshot is not a tariff schedule. Do not infer a duty or legal clearance
from a chapter-level HS match: consult the linked authority for national HS,
origin, product attributes, transaction date and any applicable exceptions.
"""

SNAPSHOT_DATE = "2026-09-29"
GUIDE = "guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md"

# Keep these records actionable and traceable. No invented prohibitions or
# rates: these are verification tasks, never automatic eligibility findings.
TRADE_RULES = (
    ("ID", "Documentation", "BTKI 2022 / PMK 26/PMK.010/2022: klasifikasi sampai 8 digit dan cek tarif/lartas di INSW sebelum PIB/PEB.", "https://www.insw.go.id/", "PMK 26/PMK.010/2022"),
    ("ID", "Documentation", "Impor: cek Permendag 16/2025 beserta regulasi sektoral; izin PI/LS sesuai barang di OSS/SINSW.", "https://jdih.kemendag.go.id/", "Permendag 16/2025"),
    ("ID", "Documentation", "Ekspor: cek lartas setelah perubahan Permendag 5/2026 dan larangan ekspor setelah Permendag 6/2026; jangan anggap seluruh produk memerlukan PE.", "https://jdih.kemendag.go.id/", "Permendag 5/2026; Permendag 6/2026"),
    ("ID", "Documentation", "DHE SDA: cek PP 36/2023 beserta perubahan terakhir dan ketentuan sektor sebelum menetapkan kewajiban penempatan.", "https://peraturan.bpk.go.id/", "PP 36/2023; PP 21/2026"),
    ("US", "Documentation", "Cek HTSUS termasuk Chapter 99, Section 301/232 dan AD/CVD untuk HS, asal dan tanggal impor; tarif IEEPA historis tidak boleh dipakai sebagai tarif kini.", "https://hts.usitc.gov/", "HTSUS / Chapter 99"),
    ("US", "Documentation", "Pantau CSMS CBP dan Federal Register untuk de minimis, pengecualian dan perubahan tarif. Status Section 301 'forced labor' dalam dokumen riset perlu verifikasi tersendiri.", "https://www.cbp.gov/trade/automated/csms", "CBP CSMS"),
    ("CA", "Documentation", "ICA-CEPA: penandatanganan/ratifikasi bukan otomatis tarif preferensi; verifikasi tanggal berlaku dan aturan asal barang.", "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/", "ICA-CEPA"),
    ("GB", "Documentation", "Cek kode tarif impor nasional 10 digit dan status UK CBAM per produk/tanggal transaksi.", "https://www.trade-tariff.service.gov.uk/", "UK Global Tariff"),
    ("MX", "Documentation", "Cek kode tarif nasional dan bea tambahan produk dari negara non-FTA sebelum menghitung landed cost.", "https://www.sat.gob.mx/", "Mexico customs tariff"),
    ("JP", "Documentation", "Cek Japan Customs, IJEPA/RCEP beserta rules of origin dan ketentuan MAFF/MHLW untuk pangan.", "https://www.customs.go.jp/english/", "Japan Customs / IJEPA"),
)

EU_RULES = (
    ("Documentation", "Cek TARIC 10 digit, preferensi GSP yang berlaku dan tindakan perdagangan untuk HS/tanggal impor; IEU-CEPA yang belum berlaku tidak boleh memberi tarif preferensi.", "https://trade.ec.europa.eu/access-to-markets/en/home", "TARIC / Access2Markets"),
    ("Documentation", "CBAM: cek cakupan kode CN besi/baja, aluminium, semen, pupuk, hidrogen, listrik dan kewajiban data emisi tertanam serta status importir.", "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en", "Regulation (EU) 2023/956"),
    ("Documentation", "EUDR: cocokkan Annex I/kode CN, geolokasi, legalitas, DDS dan tanggal penerapan menurut ukuran operator; tidak semua barang satu bab HS tercakup.", "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en", "Regulation (EU) 2023/1115"),
)


def rules_for(country_code: str) -> list[dict]:
    """Return research pointers for a country; EU entries apply to EU members."""
    from app.data.regulatory_intel import COUNTRY_CUSTOMS

    code = (country_code or "").upper()
    rows = [row for row in TRADE_RULES if row[0] == code]
    if COUNTRY_CUSTOMS.get(code) == "EU":
        rows.extend((code, *row) for row in EU_RULES)
    return [
        {"id": f"REF-20260929-{code}-{i:02d}", "countryCode": code,
         "ruleCategory": category, "descriptionRule": description,
         "source": reference, "sourceUrl": url, "snapshotDate": SNAPSHOT_DATE,
         "reviewStatus": "research_only", "guide": GUIDE,
         "requiredSpecs": [], "forbiddenKeywords": []}
        for i, (_, category, description, url, reference) in enumerate(rows, 1)
    ]


def seed_trade_reference(db) -> None:
    """Install curated records without overwriting admin edits; retire old fake demo rows."""
    for record in db.all("regulations"):
        if (str(record.get("id", "")).startswith("REG-")
                and str(record.get("descriptionRule", "")) == f"Regulation for {record.get('countryCode')}."):
            db.delete("regulations", record["id"])
    from app.data.regulatory_intel import COUNTRY_CUSTOMS
    codes = ("ID", "US", "CA", "GB", "MX", "JP") + tuple(
        code for code, bloc in COUNTRY_CUSTOMS.items() if bloc == "EU"
    )
    for code in codes:
        for record in rules_for(code):
            if not db.get("regulations", record["id"]):
                db.insert("regulations", record)
