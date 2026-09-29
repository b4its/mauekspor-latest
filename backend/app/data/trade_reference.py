"""Curated research pointers from guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md.

This snapshot is not a tariff schedule. Do not infer a duty or legal clearance
from a chapter-level HS match: consult the linked authority for national HS,
origin, product attributes, transaction date and any applicable exceptions.

Every record here is a *verification task* traceable to an official source,
never an automatic eligibility finding. Anything that could not be confirmed
against a primary source is deliberately omitted rather than guessed.
"""

from __future__ import annotations

SNAPSHOT_DATE = "2026-09-29"
GUIDE = "guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md"

# Keep these records actionable and traceable. No invented prohibitions or
# rates: these are verification tasks, never automatic eligibility findings.
TRADE_RULES = (
    # ── Indonesia ──────────────────────────────────────────────────────────
    ("ID", "Documentation", "BTKI 2022 / PMK 26/PMK.010/2022: klasifikasi sampai 8 digit dan cek tarif/lartas di INSW sebelum PIB/PEB.", "https://www.insw.go.id/", "PMK 26/PMK.010/2022"),
    ("ID", "Documentation", "Impor: cek Permendag 16/2025 beserta regulasi sektoral (17/2025 tekstil, 18/2025 pertanian/peternakan, 19/2025 garam/perikanan); izin PI/LS sesuai barang di OSS/SINSW.", "https://jdih.kemendag.go.id/", "Permendag 16/2025"),
    ("ID", "Documentation", "Ekspor: cek lartas setelah perubahan Permendag 5/2026 dan larangan ekspor setelah Permendag 6/2026 (berlaku 1 April 2026); jangan anggap seluruh produk memerlukan PE.", "https://jdih.kemendag.go.id/", "Permendag 5/2026; Permendag 6/2026"),
    ("ID", "Documentation", "DHE SDA: PP 21/2026 (perubahan terbaru atas PP 36/2023) berlaku 1 Juni 2026 — repatriasi 100%, penempatan nonmigas 100% minimal 12 bulan, migas 30% minimal 3 bulan; verifikasi sebelum menetapkan kewajiban penempatan.", "https://peraturan.bpk.go.id/", "PP 36/2023; PP 21/2026"),
    ("ID", "Documentation", "Bea keluar komoditas (sawit/CPO, mineral olahan, kayu, kakao, dll.) mengacu PMK per komoditas; batu bara/emas: jangan asumsikan tarif tanpa PMK final yang berlaku.", "https://jdih.kemenkeu.go.id/", "PMK 68/2025 (dan PMK terkait)"),
    ("ID", "Documentation", "Barang kiriman (e-commerce/kurir): PMK 96/2023 jo. PMK 4/2025 — bebas BM ≤ USD 3, tarif flat umumnya 7,5% untuk USD 3–1.500, dan ketentuan impor umum di atasnya.", "https://jdih.kemenkeu.go.id/", "PMK 96/2023; PMK 4/2025"),
    ("ID", "Documentation", "Hilirisasi: larangan ekspor bijih nikel (2020), bauksit (2023), dan konsentrat tembaga; cek ketentuan terbaru Kementerian ESDM/Kemendag.", "https://jdih.esdm.go.id/", "Kebijakan hilirisasi minerba"),
    # ── United States ──────────────────────────────────────────────────────
    ("US", "Documentation", "Cek HTSUS termasuk Chapter 99, Section 301/232 dan AD/CVD untuk HS, asal dan tanggal impor; tarif IEEPA historis tidak boleh dipakai sebagai tarif kini (dibatalkan Mahkamah Agung AS, 20 Feb 2026).", "https://hts.usitc.gov/", "HTSUS / Chapter 99"),
    ("US", "Documentation", "Section 301 'forced labor' (berlaku 24 Jul 2026) menambah tarif di atas MFN (Indonesia 10%); cek daftar HTS per negara ART dan pengecualian. Status dalam sengketa di CIT (sidang 30 Sep 2026) — verifikasi sebelum menghitung landed cost.", "https://www.cbp.gov/trade/automated/csms", "CBP CSMS / Federal Register"),
    ("US", "Documentation", "De minimis USD 800 ditangguhkan untuk semua negara (29 Agu 2025; ditetapkan tanpa batas waktu via Interim Final Rules 24 Jun 2026); cek CSMS sebelum mengirim barang kiriman.", "https://www.cbp.gov/trade/automated/csms", "CBP CSMS"),
    ("US", "Documentation", "Section 232: baja/aluminium 50% atas nilai penuh (sejak 6 Apr 2026); cek Annex I-A/I-B dan tarif produk turunan terkini di HTSUS Chapter 99.", "https://hts.usitc.gov/", "Section 232 / HTSUS Ch.99"),
    ("US", "Documentation", "Agreement on Reciprocal Trade (ART) AS–Indonesia ditandatangani 19 Feb 2026 (tarif resiprokal 19%, produk tertentu 0% per Schedule 2B); cek HTS khusus per negara.", "https://ustr.gov/", "ART AS–Indonesia"),
    # ── Canada ─────────────────────────────────────────────────────────────
    ("CA", "Documentation", "ICA-CEPA: penandatanganan/ratifikasi bukan otomatis tarif preferensi; verifikasi tanggal berlaku setelah pertukaran nota diplomatik dan aturan asal barang.", "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/", "ICA-CEPA (SI/2026-30)"),
    # ── United Kingdom ─────────────────────────────────────────────────────
    ("GB", "Documentation", "Cek kode tarif impor nasional 10 digit dan status UK CBAM (sektor aluminium, semen, pupuk, hidrogen, besi & baja; mulai 1 Jan 2027) per produk/tanggal transaksi.", "https://www.trade-tariff.service.gov.uk/", "UK Global Tariff / UK CBAM"),
    # ── Mexico ─────────────────────────────────────────────────────────────
    ("MX", "Documentation", "Tarif 5–50% atas 1.463 pos tarif dari negara non-FTA (termasuk Indonesia) sejak 1 Jan 2026; cek kode tarif nasional dan bea tambahan sebelum menghitung landed cost.", "https://www.sat.gob.mx/", "Mexico customs tariff"),
    # ── Japan ──────────────────────────────────────────────────────────────
    ("JP", "Documentation", "Cek Japan Customs, IJEPA/RCEP beserta rules of origin dan ketentuan MAFF/MHLW untuk pangan (label bahasa Jepang, deklarasi alergen).", "https://www.customs.go.jp/english/", "Japan Customs / IJEPA"),
    # ── China ──────────────────────────────────────────────────────────────
    ("CN", "Documentation", "Registrasi produsen pangan luar negeri (GACC Decree 248 dan revisinya); kontrol ekspor tanah jarang Tiongkok (paket Apr 2025 tetap berlaku, paket Okt 2025 ditangguhkan hingga 10 Nov 2026).", "https://english.customs.gov.cn/", "GACC / MOFCOM Export Control Law"),
    # ── India ──────────────────────────────────────────────────────────────
    ("IN", "Documentation", "Wajib IEC; ICEGATE; BIS Quality Control Orders (QCO); cek ITC(HS) status free/restricted/prohibited dan SCOMET untuk dual-use.", "https://www.dgft.gov.in/", "DGFT / ITC(HS)"),
)

EU_RULES = (
    ("Documentation", "Cek TARIC 10 digit, preferensi GSP yang berlaku dan tindakan perdagangan untuk HS/tanggal impor; IEU-CEPA (target penandatanganan Okt 2026) yang belum berlaku tidak boleh memberi tarif preferensi.", "https://trade.ec.europa.eu/access-to-markets/en/home", "TARIC / Access2Markets"),
    ("Documentation", "CBAM: periode definitif mulai 1 Jan 2026 (besi & baja, aluminium, semen, pupuk, hidrogen, listrik); ambang de minimis 50 ton/importir/tahun; penjualan sertifikat mulai 1 Feb 2027, deklarasi pertama 30 Sep 2027. Cek Annex I/kode CN, status Authorised CBAM Declarant, dan data emisi tertanam.", "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en", "Regulation (EU) 2023/956"),
    ("Documentation", "EUDR: berlaku 30 Des 2026 (operator besar/menengah) dan 30 Jun 2027 (mikro/kecil); cocokkan Annex I/kode CN, geolokasi lahan, legalitas, dan DDS. Delegated Act 13 Jul 2026 mengubah cakupan — verifikasi daftar terkini, tidak semua barang satu bab HS tercakup.", "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en", "Regulation (EU) 2023/1115"),
    ("Documentation", "Aturan e-commerce: mulai 1 Jul 2026 bea masuk tetap €3 per jenis barang (per kode tarif) untuk kiriman ≤ €150, sementara hingga 1 Jul 2028; pembebasan bea €150 berakhir.", "https://taxation-customs.ec.europa.eu/", "EU customs reform (temporary €3)"),
    ("Documentation", "GPSR (keamanan produk umum), REACH (kimia), CE marking, EU Batteries Regulation, PPWR (kemasan), dan Forced Labour Regulation (berlaku 2027) — cek per produk dan tanggal.", "https://ec.europa.eu/growth/single-market/ce-marking_en", "EU product & sustainability rules"),
)


# ── Struktur berikut menyediakan konteks terdalam untuk riset halaman admin/edu. ──
# Timeline peristiwa regulasi terverifikasi (sumber: guide Bagian 12 & ringkasan).
REGULATORY_TIMELINE = (
    ("2026-01-01", "CBAM UE fase definitif mulai; tarif Meksiko 5–50% untuk 1.463 pos dari negara non-FTA", "EU/MX"),
    ("2026-02-19", "Agreement on Reciprocal Trade (ART) AS–Indonesia ditandatangani (tarif resiprokal 19%)", "US"),
    ("2026-02-20", "Mahkamah Agung AS (6-3) menyatakan IEEPA tidak memberi wewenang tarif; tarif IEEPA dibatalkan", "US"),
    ("2026-03-30", "Moratorium bea e-commerce WTO (MC14) berakhir tanpa konsensus perpanjangan", "WTO"),
    ("2026-04-01", "Permendag 5/2026 & 6/2026 (deregulasi ekspor Indonesia) berlaku", "ID"),
    ("2026-04-06", "Section 232 AS: baja & aluminium 50% atas nilai penuh barang", "US"),
    ("2026-05-01", "EU–Mercosur diterapkan sementara; tarif nol Tiongkok untuk 53 negara Afrika", "EU/CN"),
    ("2026-06-01", "PP 21/2026 tentang DHE SDA berlaku (repatriasi 100%)", "ID"),
    ("2026-07-01", "UE: bea €3 per jenis barang untuk kiriman bernilai ≤ €150", "EU"),
    ("2026-07-24", "Section 301 'forced labor' AS berlaku atas 60 ekonomi (Indonesia 10%)", "US"),
    ("2026-11-10", "Batas gencatan dagang AS–Tiongkok & penangguhan kontrol tanah jarang Tiongkok", "US/CN"),
    ("2026-12-04", "Section 232 AS: tarif polysilicon & turunannya berlaku", "US"),
    ("2026-12-30", "EUDR berlaku untuk operator besar/menengah", "EU"),
    ("2027-01-01", "UK CBAM berlaku; kenaikan tarif AS untuk furnitur berkain & kabinet", "GB/US"),
    ("2027-02-01", "Penjualan sertifikat CBAM UE dimulai", "EU"),
    ("2027-06-30", "EUDR berlaku untuk operator mikro/kecil", "EU"),
    ("2027-09-30", "Deklarasi CBAM tahunan pertama UE", "EU"),
    ("2028-01-01", "HS 2028 berlaku secara global (edisi ke-8, Siklus Review ke-7 WCO)", "WCO"),
    ("2028-07-01", "Akhir masa bea sementara €3 UE (digantikan EU Customs Data Hub)", "EU"),
)

# Angka kunci HS 2028 (sumber WCO, berlaku 1 Jan 2028).
HS_2028_FACTS = {
    "effective": "2028-01-01",
    "edition": 8,
    "review_cycle": "7th Review Cycle (Jul 2019–Jun 2025)",
    "amendment_sets": 299,
    "headings_total": 1229,
    "subheadings_total": 5852,
    "headings_new": 6,
    "headings_deleted": 5,
    "subheadings_new": 428,
    "subheadings_deleted": 172,
    "highlights": (
        "Vaksin dipindah ke pos baru 30.07 & 30.08; pos baru 21.07 untuk suplemen makanan; "
        "restrukturisasi pos 39.15 untuk limbah plastik (selaras Konvensi Basel); "
        "Catatan 3 Bab 39 memperkenalkan konsep 'single-use' (sedotan, kemasan, peralatan makan, dll.); "
        "subpos baru untuk ambulans, APD, ventilator, dan alat diagnostik."
    ),
    "preparation": "WCO menyusun tabel korelasi HS 2022→2028; ASEAN/AHTN 2028 & BTKI baru menyusul; audit master data HS sejak 2027.",
    "sources": [{"name": "WCO HS 2028", "url": "https://www.wcoomd.org/"}],
}


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
    codes = ("ID", "US", "CA", "GB", "MX", "JP", "CN", "IN") + tuple(
        code for code, bloc in COUNTRY_CUSTOMS.items() if bloc == "EU"
    )
    for code in codes:
        for record in rules_for(code):
            if not db.get("regulations", record["id"]):
                db.insert("regulations", record)


# ── Status FTA/CEPA Indonesia (terverifikasi per snapshot) ────────────────────
# status: in_force | signed_ratifying | concluded | negotiating
INDONESIA_FTAS = (
    ("ATIGA (ASEAN)", "in_force", "Protokol Kedua (upgraded ATIGA) ditandatangani Okt/Des 2025."),
    ("ACFTA (ASEAN–Tiongkok)", "in_force", "ACFTA 3.0 ditandatangani Okt 2025."),
    ("AKFTA / AJCEP / AANZFTA / AIFTA / AHKFTA", "in_force", "Berlaku; cek Product Specific Rule per HS."),
    ("RCEP", "in_force", "Berlaku untuk Indonesia sejak 2 Januari 2023."),
    ("IJEPA (Jepang)", "in_force", "Berlaku (termasuk protokol amandemen)."),
    ("IA-CEPA (Australia)", "in_force", "Berlaku sejak 2020; sebagian besar tarif 0%."),
    ("IK-CEPA (Korea Selatan)", "in_force", "Berlaku sejak 2023."),
    ("IEFTA CEPA (EFTA)", "in_force", "Berlaku sejak 1 November 2021."),
    ("IUAE-CEPA (UEA)", "in_force", "Berlaku."),
    ("IC-CEPA (Chili) / PTA Pakistan / PTA Mozambik", "in_force", "Berlaku."),
    ("ICA-CEPA (Kanada)", "signed_ratifying", "Ditandatangani 24 Sep 2025; UU Kanada disahkan 6 Mei 2026 (SI/2026-30); berlaku setelah pertukaran nota diplomatik."),
    ("IEU-CEPA (Uni Eropa)", "concluded", "Perundingan selesai 23 Sep 2025; target penandatanganan Okt 2026, implementasi awal 2027. Belum memberi tarif preferensi."),
    ("Indonesia–EAEU FTA", "signed_ratifying", "Ditandatangani Des 2025; proses ratifikasi berjalan."),
    ("ART Indonesia–AS", "in_force", "Agreement on Reciprocal Trade ditandatangani 19 Feb 2026 (tarif resiprokal 19%; produk tertentu 0% per Schedule 2B)."),
    ("CPTPP (aksesi)", "negotiating", "Indonesia mengajukan aksesi; belum berlaku."),
)

# ── Prinsip & struktur HS (konteks klasifikasi) ───────────────────────────────
HS_STRUCTURE_NOTE = (
    "6 digit pertama HS seragam di seluruh dunia (dikelola WCO); digit ke-7 dst "
    "adalah tambahan nasional/regional. Indonesia & ASEAN memakai AHTN 8 digit "
    "(BTKI 2022, 11.414 pos tarif). KUMHS 1–6 mengatur interpretasi; baca Catatan "
    "Bagian/Bab sebelum menetapkan pos. Salah klasifikasi berisiko kekurangan bayar, "
    "denda, penahanan barang, dan hilangnya preferensi FTA."
)


def reference_bundle() -> dict:
    """Kumpulan referensi riset terkurasi siap-API (bukan tarif/clearance).

    Dipakai oleh endpoint /reference/ dan konteks AI agar asisten mengutip
    data faktual bertanggal, bukan mengarang.
    """
    from app.data.regulatory_intel import CUSTOMS_SYSTEMS

    return {
        "snapshotDate": SNAPSHOT_DATE,
        "guide": GUIDE,
        "disclaimer": (
            "Referensi riset bertanggal, bukan nasihat hukum/tarif. Verifikasi ke "
            "sumber resmi sebelum bertransaksi."
        ),
        "timeline": [{"date": d, "event": e, "scope": s} for (d, e, s) in REGULATORY_TIMELINE],
        "hs2028": HS_2028_FACTS,
        "hsStructureNote": HS_STRUCTURE_NOTE,
        "indonesiaFtas": [
            {"name": n, "status": st, "note": note} for (n, st, note) in INDONESIA_FTAS
        ],
        "customsSystems": {
            key: {"label": v.get("label", ""), "nomenclature": v.get("nomenclature", ""),
                  "tariffs": v.get("tariffs", ""), "note": v.get("note", "")}
            for key, v in CUSTOMS_SYSTEMS.items()
        },
    }


def full_reference_bundle() -> dict:
    """Bundle lengkap dari data panduan terstruktur (regulatory_guide).

    Menyajikan seluruh isi panduan 2026 (Incoterms, HS, regulasi ID/US/EU,
    FTA, dokumen, pengendalian ekspor, portal, checklist, timeline) dalam
    bentuk terstruktur untuk halaman referensi.
    """
    from app.data import regulatory_guide as g

    base = reference_bundle()
    base.update({
        "disclaimer": g.DISCLAIMER,
        "institutions": [
            {"abbr": a, "name": n, "function": f, "url": u} for a, n, f, u in g.INSTITUTIONS
        ],
        "wtoPrinciples": [{"name": n, "detail": d} for n, d in g.WTO_PRINCIPLES],
        "wtoUpdates": [{"date": d, "event": e} for d, e in g.WTO_UPDATES],
        "incoterms": [
            {"code": c, "name": n, "risk": r, "mode": m} for c, n, r, m in g.INCOTERMS_2020
        ],
        "incotermsNotes": list(g.INCOTERMS_NOTES),
        "hsDigitLengths": [
            {"name": n, "system": s, "digits": d} for n, s, d in g.HS_DIGIT_LENGTHS
        ],
        "hs2022": g.HS_2022_STRUCTURE,
        "kumhs": [{"rule": r, "detail": d} for r, d in g.KUMHS_RULES],
        "classificationTips": list(g.HS_CLASSIFICATION_TIPS),
        "indonesia": {
            "legalBasis": [{"regulation": r, "material": m} for r, m in g.ID_LEGAL_BASIS],
            "btki": g.ID_BTKI,
            "importDereg2025": list(g.ID_IMPORT_DEREG_2025),
            "exportDereg2026": list(g.ID_EXPORT_DEREG_2026),
            "licenses": [{"document": d, "note": n} for d, n in g.ID_LICENSES],
            "systems": [{"name": n, "detail": d} for n, d in g.ID_SYSTEMS],
            "importLevies": [{"levy": l, "rate": r} for l, r in g.ID_IMPORT_LEVIES],
            "importExample": g.ID_IMPORT_EXAMPLE,
            "parcelRules": list(g.ID_PARCEL_RULES),
            "dhe": g.ID_DHE_SDA,
            "hilirisasi": list(g.ID_HILIRISASI),
            "coo": {"portal": g.ID_COO["portal"], "forms": list(g.ID_COO["forms"]), "euGsp": g.ID_COO["eu_gsp"]},
        },
        "unitedStates": {
            "timeline": [{"date": d, "event": e} for d, e in g.US_TIMELINE],
            "section301ForcedLabor": g.US_SECTION_301_FORCED_LABOR,
            "section232": [{"product": p, "tariff": r} for p, r in g.US_SECTION_232],
            "china": list(g.US_CHINA),
            "importCompliance": list(g.US_IMPORT_COMPLIANCE),
        },
        "europeanUnion": {
            "cbam": g.EU_CBAM,
            "eudr": g.EU_EUDR,
            "customsReform": list(g.EU_CUSTOMS_REFORM),
            "tariff": list(g.EU_TARIFF),
        },
        "otherCountries": [
            {"name": n, "authority": a, "note": d} for n, a, d in g.OTHER_COUNTRIES
        ],
        "globalFtas": [{"name": n, "note": d} for n, d in g.GLOBAL_FTAS],
        "rulesOfOrigin": [{"rule": r, "detail": d} for r, d in g.RULES_OF_ORIGIN],
        "standardDocuments": [{"document": d, "function": f} for d, f in g.STANDARD_DOCUMENTS],
        "paymentMethods": g.PAYMENT_METHODS,
        "exportControls": [{"scope": s, "detail": d} for s, d in g.EXPORT_CONTROLS],
        "officialPortals": [
            {"country": c, "portals": list(p)} for c, p in g.OFFICIAL_PORTALS
        ],
        "globalPortals": [{"need": n, "portal": p} for n, p in g.GLOBAL_PORTALS],
        "complianceChecklist": [
            {"section": s, "items": list(items)} for s, items in g.COMPLIANCE_CHECKLIST
        ],
        "primarySources": list(g.PRIMARY_SOURCES),
    })
    return base


# ─────────────────────────────────────────────────────────────────────────────
# SEEDER DATA RIIL DARI PANDUAN (regulations + knowledge_articles)
# ─────────────────────────────────────────────────────────────────────────────
# Setiap entri berasal langsung dari guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-
# 2026.md. Tidak ada data simulasi; baris legacy "Regulation for <CODE>."
# dipensiunkan agar tabel `regulations` hanya berisi referensi faktual.

def _reg(country: str, category: str, description: str, url: str, source: str, idx: int) -> dict:
    return {
        "id": f"REG-GUIDE-{country}-{idx:02d}",
        "countryCode": country,
        "ruleCategory": category,
        "descriptionRule": description,
        "source": source,
        "sourceUrl": url,
        "snapshotDate": SNAPSHOT_DATE,
        "reviewStatus": "research_only",
        "guide": GUIDE,
        "requiredSpecs": [],
        "forbiddenKeywords": [],
    }


def _guide_regulations() -> list[dict]:
    """Bangun baris `regulations` faktual dari data panduan terstruktur."""
    from app.data import regulatory_guide as g

    rows: list[dict] = []

    # ── Indonesia ────────────────────────────────────────────────────────────
    id_url = "https://jdih.kemendag.go.id/"
    for i, (reg, material) in enumerate(g.ID_LEGAL_BASIS, 1):
        rows.append(_reg("ID", "Legal Basis", f"{reg}: {material}.", id_url, reg, i))
    n = len(g.ID_LEGAL_BASIS)
    rows.append(_reg("ID", "Documentation",
                     f"BTKI 2022 berbasis HS 2022/AHTN 2022, berlaku {g.ID_BTKI['effective']}, "
                     f"{g.ID_BTKI['lines']} pos tarif (naik dari {g.ID_BTKI['lines_previous']}). Akses: {g.ID_BTKI['access']}.",
                     "https://www.insw.go.id/", "PMK 26/PMK.010/2022 (BTKI 2022)", n + 1))
    dhe = g.ID_DHE_SDA
    rows.append(_reg("ID", "Documentation",
                     f"DHE SDA {dhe['regulation']} (berlaku {dhe['effective']}): repatriasi {dhe['repatriation']}; "
                     f"nonmigas {dhe['nonmigas_placement']}; migas {dhe['migas_placement']}; {dhe['bank']}; "
                     f"insentif {dhe['tax_incentive']}; sektor {dhe['sectors']}.",
                     "https://peraturan.bpk.go.id/", dhe["regulation"], n + 2))
    rows.append(_reg("ID", "Documentation",
                     "Barang kiriman (e-commerce/kurir) PMK 96/2023 jo. PMK 4/2025: " + " ".join(g.ID_PARCEL_RULES),
                     "https://jdih.kemenkeu.go.id/", "PMK 96/2023; PMK 4/2025", n + 3))
    rows.append(_reg("ID", "Restriction",
                     "Hilirisasi & bea keluar: " + " ".join(g.ID_HILIRISASI),
                     "https://jdih.esdm.go.id/", "Kebijakan hilirisasi minerba", n + 4))
    rows.append(_reg("ID", "Documentation",
                     "Surat Keterangan Asal via " + g.ID_COO["portal"] + ". Form: " + "; ".join(g.ID_COO["forms"]) + ". " + g.ID_COO["eu_gsp"],
                     "https://e-ska.kemendag.go.id/", "e-SKA Kemendag", n + 5))

    # ── Amerika Serikat ──────────────────────────────────────────────────────
    us_url = "https://hts.usitc.gov/"
    for i, (date, event) in enumerate(g.US_TIMELINE, 1):
        rows.append(_reg("US", "Tariff Regime", f"{date}: {event}.", us_url, f"US tariff timeline ({date})", i))
    n = len(g.US_TIMELINE)
    s301 = g.US_SECTION_301_FORCED_LABOR
    rows.append(_reg("US", "Tariff Regime",
                     f"Section 301 'Forced Labor' (berlaku {s301['effective']}) menambah di atas MFN. "
                     f"10%: {', '.join(s301['standard_10pct'])}. 12,5%: {', '.join(s301['standard_12_5pct'])}. "
                     f"Batas MFN: 10% ({', '.join(s301['mfn_capped']['10%'])}), 12,5% ({', '.join(s301['mfn_capped']['12.5%'])}). "
                     f"Pengecualian: {', '.join(s301['exemptions'])}. TRQ tekstil: {', '.join(s301['trq_textile'])}.",
                     "https://www.cbp.gov/trade/automated/csms", "CBP CSMS / Federal Register", n + 1))
    for i, (product, rate) in enumerate(g.US_SECTION_232, 1):
        rows.append(_reg("US", "Tariff Regime", f"Section 232 — {product}: {rate}.", us_url, "Section 232 / HTSUS Ch.99", n + 1 + i))
    n = n + 1 + len(g.US_SECTION_232)
    rows.append(_reg("US", "Documentation", "AS–Tiongkok: " + " ".join(g.US_CHINA),
                     "https://www.cbp.gov/trade/automated/csms", "CBP CSMS", n + 1))
    rows.append(_reg("US", "Documentation", "Kepatuhan impor AS: " + " ".join(g.US_IMPORT_COMPLIANCE),
                     "https://www.cbp.gov/", "CBP / FDA / UFLPA", n + 2))

    # ── Uni Eropa (berlaku untuk semua anggota EU) ───────────────────────────
    eu_url = "https://trade.ec.europa.eu/access-to-markets/en/home"
    cbam = g.EU_CBAM
    rows.append(_reg("EU", "Sustainability",
                     f"CBAM ({cbam['regulation']}): definitif sejak {cbam['definitive_start']}; sektor "
                     f"{', '.join(cbam['sectors'])}; de minimis {cbam['de_minimis']}; {cbam['declarant']} "
                     f"Penjualan sertifikat {cbam['certificate_sale']}; deklarasi pertama {cbam['first_declaration']}. "
                     f"Dampak Indonesia: {cbam['indonesia_impact']}",
                     "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
                     cbam["regulation"], 1))
    eudr = g.EU_EUDR
    rows.append(_reg("EU", "Sustainability",
                     f"EUDR ({eudr['regulation']}): komoditas {', '.join(eudr['commodities'])}. Berlaku "
                     f"{eudr['large_operators']} (operator besar/menengah) dan {eudr['micro_small']} (mikro/kecil). "
                     f"Delegated Act {eudr['delegated_act']}. Kewajiban: {', '.join(eudr['obligations'])}. "
                     f"{eudr['indonesia_relevance']}",
                     "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en",
                     eudr["regulation"], 2))
    rows.append(_reg("EU", "Documentation", "Reformasi kepabeanan & e-commerce UE: " + " ".join(g.EU_CUSTOMS_REFORM),
                     eu_url, "EU customs reform", 3))
    rows.append(_reg("EU", "Tariff", "Tarif UE: " + " ".join(g.EU_TARIFF), eu_url, "TARIC / Access2Markets", 4))

    # ── Negara & kawasan utama lainnya ───────────────────────────────────────
    cc_url = {
        "CN": "https://english.customs.gov.cn/", "GB": "https://www.trade-tariff.service.gov.uk/",
        "JP": "https://www.customs.go.jp/english/", "IN": "https://www.dgft.gov.in/",
        "KR": "https://unipass.customs.go.kr/", "AU": "https://www.abf.gov.au/",
        "CA": "https://www.cbsa-asfc.gc.ca/", "MX": "https://www.sat.gob.mx/",
        "SA": "https://zatca.gov.sa/", "AE": "https://www.mof.gov.ae/",
        "RU": "https://customs.gov.ru/", "BR": "https://www.gov.br/receitafederal/",
        "ASEAN": "https://asean.org/",
    }
    name_to_code = {
        "Tiongkok": "CN", "Inggris": "GB", "Jepang": "JP", "India": "IN", "Korea Selatan": "KR",
        "Australia": "AU", "Kanada": "CA", "Meksiko": "MX", "Arab Saudi": "SA", "UEA": "AE",
        "Rusia/EAEU": "RU", "Brasil/Mercosur": "BR", "ASEAN": "ASEAN",
    }
    for i, (name, auth, detail) in enumerate(g.OTHER_COUNTRIES, 1):
        code = name_to_code.get(name, "XX")
        rows.append(_reg(code, "Documentation", f"{name} ({auth}): {detail}.",
                         cc_url.get(code, "https://www.wto.org/"), f"{name} — {auth}", i))

    return rows


def _guide_knowledge_articles() -> list[dict]:
    """Bangun knowledge_articles faktual dari data panduan terstruktur."""
    from app.data import regulatory_guide as g

    arts: list[dict] = []

    def add(slug: str, title: str, category: str, summary: str, steps: list[str]) -> None:
        arts.append({
            "id": f"KB-GUIDE-{slug}",
            "title": title,
            "category": category,
            "status": "Published",
            "readTime": f"{max(3, len(steps) + 2)} min",
            "summary": summary,
            "steps": steps,
            "updatedAt": SNAPSHOT_DATE,
        })

    add("HS-CODE", "Sistem HS Code & KUMHS 1–6", "HS Code",
        "Struktur HS, panjang digit per negara, dan Ketentuan Umum Menginterpretasi.",
        [f"{name}: {system} ({digits} digit)" for name, system, digits in g.HS_DIGIT_LENGTHS]
        + [f"{rule}: {text}" for rule, text in g.KUMHS_RULES])
    add("HS-2028", "HS 2028: perubahan besar 1 Jan 2028", "HS Code",
        "Angka kunci dan perubahan utama nomenklatur HS edisi ke-8 (WCO).",
        [f"Total pos {g.HS_2028['headings_total']}; subpos {g.HS_2028['subheadings_total']} "
         f"(+{g.HS_2028['subheadings_new']}/-{g.HS_2028['subheadings_deleted']})"]
        + list(g.HS_2028["changes"]) + list(g.HS_2028["preparation"]))
    add("INCOTERMS", "Incoterms® 2020", "Incoterms",
        "Sebelas Incoterms 2020, titik perpindahan risiko, dan moda.",
        [f"{code} — {name}: risiko {risk} ({mode})" for code, name, risk, mode in g.INCOTERMS_2020]
        + list(g.INCOTERMS_NOTES))
    add("ID-REG", "Regulasi Ekspor-Impor Indonesia", "Indonesia",
        "Dasar hukum, BTKI 2022, deregulasi 2025–2026, perizinan, dan pungutan.",
        list(g.ID_IMPORT_DEREG_2025) + list(g.ID_EXPORT_DEREG_2026)
        + [f"{n}: {d}" for n, d in g.ID_LICENSES] + [f"{n}: {d}" for n, d in g.ID_IMPORT_LEVIES])
    add("ID-DHE", "DHE SDA (PP 21/2026)", "Indonesia",
        "Kewajiban penempatan Devisa Hasil Ekspor SDA dan insentifnya.",
        [f"{k}: {v}" for k, v in g.ID_DHE_SDA.items()])
    add("US-TARIFF", "Rezim tarif AS 2025–2026", "Amerika Serikat",
        "Kronologi IEEPA/Section 301/232 dan kepatuhan impor.",
        [f"{d}: {e}" for d, e in g.US_TIMELINE]
        + [f"{p}: {r}" for p, r in g.US_SECTION_232])
    add("EU-CBAM-EUDR", "UE: CBAM, EUDR & reformasi kepabeanan", "Uni Eropa",
        "CBAM fase definitif, EUDR, dan aturan e-commerce/kepabeanan UE.",
        list(g.EU_CUSTOMS_REFORM) + list(g.EU_TARIFF))
    add("FTA", "Perjanjian perdagangan (FTA/CEPA) & aturan asal", "FTA",
        "Status FTA Indonesia, FTA global, dan aturan asal barang.",
        [f"{n} [{st}] — {note}" for n, st, note in g.ID_FTAS]
        + [f"{n}: {d}" for n, d in g.GLOBAL_FTAS]
        + [f"{r}: {d}" for r, d in g.RULES_OF_ORIGIN])
    add("DOCUMENTS", "Dokumen ekspor-impor standar", "Documentation",
        "Daftar dokumen standar dan metode pembayaran internasional.",
        [f"{name}: {fn}" for name, fn in g.STANDARD_DOCUMENTS] + [g.PAYMENT_METHODS])
    add("EXPORT-CONTROL", "Pengendalian ekspor & sanksi", "Export Control",
        "Rezim multilateral dan kontrol ekspor utama per yurisdiksi.",
        [f"{scope}: {detail}" for scope, detail in g.EXPORT_CONTROLS])
    add("CHECKLIST", "Checklist kepatuhan ekspor-impor", "Compliance",
        "Checklist bertahap sebelum transaksi hingga monitoring rutin.",
        [f"【{section}】" for section, _ in g.COMPLIANCE_CHECKLIST]
        + [f"{section}: {item}" for section, items in g.COMPLIANCE_CHECKLIST for item in items])
    add("PORTALS", "Portal resmi untuk verifikasi", "Reference",
        "Portal global & nasional untuk verifikasi tarif, HS, dan regulasi.",
        [f"{need}: {portal}" for need, portal in g.GLOBAL_PORTALS]
        + [f"{country}: {', '.join(portals)}" for country, portals in g.OFFICIAL_PORTALS])

    return arts


def seed_regulatory_guide(db) -> None:
    """Seed data RIIL dari panduan (regulations + knowledge_articles).

    Idempoten: tidak menimpa record yang sudah ada. Memensiunkan baris demo
    legacy agar tabel hanya memuat referensi faktual.
    """
    # Pensiunkan aturan demo legacy ("Regulation for <CODE>.").
    for record in db.all("regulations"):
        if str(record.get("descriptionRule", "")).startswith("Regulation for "):
            db.delete("regulations", record["id"])

    for record in _guide_regulations():
        if not db.get("regulations", record["id"]):
            db.insert("regulations", record)

    for article in _guide_knowledge_articles():
        if not db.get("knowledge_articles", article["id"]):
            db.insert("knowledge_articles", article)
